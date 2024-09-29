from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from bson.objectid import ObjectId
from datetime import datetime

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
             "cost": Cost,
            "created_at": datetime.now()
        }

        # Insert the data into MongoDB
        from main import mongo
        mongo.db.courses.insert_one(course_data)
        
        # Flash a success message
        flash("Course added successfully!", "success")

        # Redirect to the add_course page to view the course table
        return redirect(url_for('edprovider.view_courses'))

    return render_template('edproviderlanding.html')
# Route for viewing courses (from registrations collection) with pagination
@edprovider_bp.route('/view_courses', methods=['GET'])
def view_courses():
    page = request.args.get('page', 1, type=int)  # Get the current page, default to 1
    per_page = 6  # Set how many registrations you want to display per page
    
    from main import mongo
    # Count total number of registrations for pagination
    total_registrations = mongo.db.registrations.count_documents({})
    total_pages = (total_registrations + per_page - 1) // per_page  # Calculate total number of pages
    
    # Fetch registrations for the current page
    registrations = mongo.db.registrations.find().skip((page - 1) * per_page).limit(per_page)
    
    # Pass the page, per_page, total_pages, and registrations to the template
    return render_template(
        'add_course.html',
        registrations=registrations,
        page=page,
        per_page=per_page,
        total_registrations=total_registrations,
        total_pages=total_pages  # Pass total pages to the template
    )


# Route for searching courses in registrations collection
@edprovider_bp.route('/search_courses', methods=['GET', 'POST'])
def search_courses():
    page = request.args.get('page', 1, type=int)  # Get the current page or default to 1
    per_page = 10  # Define how many items you want to display per page
    query = request.form.get('search_query') if request.method == 'POST' else request.args.get('search_query', '')

    from main import mongo
    # Search registrations by course_name or key_learnings
    search_filter = {
        "$or": [
            {"course_name": {"$regex": query, "$options": "i"}},
            {"key_learnings": {"$regex": query, "$options": "i"}}
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
        "registration_date": datetime.now()
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