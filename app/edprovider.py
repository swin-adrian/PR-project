from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from bson.objectid import ObjectId
from datetime import datetime
from flask_pymongo import PyMongo

# Define the blueprint
edprovider_bp = Blueprint('edprovider', __name__)

@edprovider_bp.route('/edproviderlanding', methods=['GET', 'POST'])
def edproviderlanding():
    if request.method == 'POST':
        # Capture form data
        industry = request.form.get('industry')
        course_name = request.form.get('course_name')
        course_type = request.form.get('course_type')
        duration = request.form.get('duration')
        course_structure = request.form.get('course_structure')
        key_learnings = request.form.get('key_learnings')
        cost = request.form.get('cost')

        # Get the university from the user's document
        university = session.get('university')
        if not university:
            flash('University information is missing. Please log in again.', 'error')
            return redirect(url_for('auth.login'))

        # Validate and process the cost
        try:
            cost = float(cost)
            if cost < 0:
                flash('Cost cannot be negative.', 'error')
                return redirect(url_for('edprovider.edproviderlanding'))
        except (ValueError, TypeError):
            flash('Invalid cost value.', 'error')
            return redirect(url_for('edprovider.edproviderlanding'))

        # Prepare course data
        course_data = {
            "Industry": industry,
            "CourseName": course_name,
            "CourseType": course_type,
            "Duration": duration,
            "CourseStructure": course_structure,
            "KeyLearnings": key_learnings,
            "Cost": cost,
            "University": university,  # Automatically set from the user's session
            "CreatedAt": datetime.now()
        }

        # Insert the data into MongoDB
        from main import mongo
        mongo.db.courses.insert_one(course_data)

        # Flash a success message
        flash("Course added successfully!", "success")
        return redirect(url_for('edprovider.view_courses'))

    return render_template('edproviderlanding.html')


# Route for viewing courses (from registrations collection) with pagination
@edprovider_bp.route('/view_courses', methods=['GET'])
def view_courses():
    # Get the user's university from the session
    user_university = session.get('university')

    if not user_university:
        return jsonify({"error": "User session not found or university not specified."}), 400

    page = request.args.get('page', 1, type=int)  # Get the current page, default to 1
    per_page = 6  # Set how many registrations you want to display per page
    
    from main import mongo
    # Count total number of registrations for the user's university
    total_registrations = mongo.db.registrations.count_documents({"university": user_university})
    total_pages = (total_registrations + per_page - 1) // per_page  # Calculate total number of pages
    
    # Fetch registrations for the current page, filtering by university
    registrations = mongo.db.registrations.find({"university": user_university}).skip((page - 1) * per_page).limit(per_page)

    # Convert the cost field to a float for each registration
    registrations = [
        {**registration, "cost": float(registration.get("cost", 0.00)) if registration.get("cost") is not None else 0.00}
        for registration in registrations
    ]
    
    # Pass the page, per_page, total_pages, and filtered registrations to the template
    return render_template(
        'add_course.html',
        registrations=registrations,
        page=page,
        per_page=per_page,
        total_registrations=total_registrations,
        total_pages=total_pages  # Pass total pages to the template
    )



# Route for searching courses by first name, last name, or course name
@edprovider_bp.route('/search_courses', methods=['GET', 'POST'])
def search_courses():
    page = request.args.get('page', 1, type=int)  # Get the current page or default to 1
    per_page = 10  # Define how many items you want to display per page
    query = request.form.get('search_query') if request.method == 'POST' else request.args.get('search_query', '')

    from main import mongo
    # Get the user's university from the session
    user_university = session.get('university')

    if not user_university:
        return jsonify({"error": "User session not found or university not specified."}), 400

    # Search registrations by first_name, last_name, or course_name for the user's university
    search_filter = {
        "$and": [
            {"university": user_university},  # Filter by university
            {"$or": [
                {"first_name": {"$regex": query, "$options": "i"}},
                {"last_name": {"$regex": query, "$options": "i"}},
                {"course_name": {"$regex": query, "$options": "i"}}
            ]}
        ]
    }

    # Count total matching registrations for pagination
    total_registrations = mongo.db.registrations.count_documents(search_filter)
    total_pages = (total_registrations + per_page - 1) // per_page  # Calculate total number of pages

    # Retrieve the relevant page of registrations
    registrations = mongo.db.registrations.find(search_filter).skip((page - 1) * per_page).limit(per_page)

    return render_template(
        'add_course.html',
        registrations=registrations,
        page=page,
        per_page=per_page,
        total_registrations=total_registrations,
        total_pages=total_pages,
        search_query=query
    )


# Route for modifying a registration in the registrations collection using AJAX
@edprovider_bp.route('/modify_registration_ajax/<registration_id>', methods=['POST'])
def modify_registration_ajax(registration_id):
    from main import mongo

    # Retrieve form data including the cost
    cost = request.form.get('cost')

    # Update registration with the new values
    updated_registration = {
        "course_name": request.form.get('course_name'),
        "first_name": request.form.get('first_name'),
        "last_name": request.form.get('last_name'),
        "email": request.form.get('email'),
        "cost": float(cost),
        "key_learnings": request.form.get('key_learnings'),
        "registration_date": datetime.now(),
        "university": session.get('university')  # Ensure that the university is updated as well
    }

    result = mongo.db.registrations.update_one({"_id": ObjectId(registration_id)}, {"$set": updated_registration})

    if result.modified_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


# Route for deleting a registration using AJAX
@edprovider_bp.route('/delete_registration/<registration_id>', methods=['POST'])
def delete_registration(registration_id):
    from main import mongo
    result = mongo.db.registrations.delete_one({"_id": ObjectId(registration_id)})
    if result.deleted_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})
    

# Route for displaying the EdProvider visuals page
@edprovider_bp.route('/edprovidervisuals', methods=['GET'])
def edprovidervisuals():
    return render_template('edprovidervisuals.html')


# Route for viewing courses data (used by the charts)
@edprovider_bp.route('/view_courses_data', methods=['GET'])
def view_courses_data():
    from main import mongo

    # Get the user's university from the session
    user_university = session.get('university')

    if not user_university:
        return jsonify({"error": "User session not found or university not specified."}), 400

    # Fetch all registrations for the user's university
    registrations = list(mongo.db.registrations.find({"university": user_university}))

    course_counts = {}
    total_costs = {}

    # Aggregate data for courses and cost associated with the university
    for registration in registrations:
        course_name = registration.get('course_name', 'Unknown Course')  # Don't split the course name
        cost = registration.get('cost', 0)

        # Count students and costs per course
        course_counts[course_name] = course_counts.get(course_name, 0) + 1
        total_costs[course_name] = total_costs.get(course_name, 0) + cost

    # Return the aggregated data as JSON
    return jsonify({"courses": course_counts, "costs": total_costs})

@edprovider_bp.route('/submit_inquiry', methods=['POST'])
def submit_inquiry():
    mongo = PyMongo(current_app)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch role from the user document
    user_role = user.get('role', 'Education Provider')

    inquiry_content = request.form.get("inquiry")
    if not inquiry_content:
        return jsonify({"error": "Inquiry content is required."}), 400

    inquiry_data = {
        "user_id": ObjectId(user_id),
        "role": user_role,
        "inquiry": inquiry_content,
        "submitted_at": datetime.utcnow(),
        "status": "Pending"
    }

    mongo.db.inquiries.insert_one(inquiry_data)
    return jsonify({"message": "Inquiry submitted successfully!"}), 200

@edprovider_bp.route('/user_inquiry')
def user_inquiry():
    # Render the inquiry page with the appropriate URLs
    return render_template(
        'Userinquiry.html',
        submit_url=url_for('edprovider.submit_inquiry'),
        get_inquiries_url=url_for('edprovider.get_inquiries')
    )

@edprovider_bp.route('/get_inquiries', methods=['GET'])
def get_inquiries():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])

    inquiries_cursor = mongo.db.inquiries.find({"user_id": ObjectId(user_id)})
    inquiries = []
    for inquiry in inquiries_cursor:
        submitted_at = inquiry.get('submitted_at', 'N/A')
        if isinstance(submitted_at, datetime):
            submitted_at = submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            submitted_at = str(submitted_at)
        inquiries.append({
            "inquiry": inquiry.get('inquiry', 'No inquiry provided'),
            "submitted_at": submitted_at,
            "status": inquiry.get('status', 'Pending')
        })

    return jsonify(inquiries)


