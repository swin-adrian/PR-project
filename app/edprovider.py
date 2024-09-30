from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from bson.objectid import ObjectId
from datetime import datetime
from flask_pymongo import PyMongo

# Define the blueprint
edprovider_bp = Blueprint('edprovider', __name__)

# Route for edproviderlanding (Add Course form)
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
        cost = request.form.get('cost')  # New field

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
            "cost": cost,
            "university": session.get('university'),  # Save the course under the university in session
            "created_at": datetime.now()
        }

        # Insert the data into MongoDB
        from main import mongo
        mongo.db.courses.insert_one(course_data)
        
        # Flash a success message
        flash("Course added successfully!", "success")

        # Redirect to the view_courses page to view the course table
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
        course_list = registration.get('course_name', 'Unknown Course').split(', ')  # Handle multiple courses
        cost = registration.get('cost', 0)

        # Count students and costs per course
        for course in course_list:
            course_counts[course] = course_counts.get(course, 0) + 1
            total_costs[course] = total_costs.get(course, 0) + cost

    # Return the aggregated data as JSON
    return jsonify({"courses": course_counts, "costs": total_costs})
