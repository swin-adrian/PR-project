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

        # Get user information from session (Assuming the session has edprovider info)
        user_id = session.get('user_id')
        user_email = session.get('email')  # Assuming user email stored in session

        # Validate and process the cost
        try:
            cost = float(cost)
            if cost < 0:
                flash('Cost cannot be negative.', 'error')
                return redirect(url_for('edprovider.edproviderlanding'))
        except (ValueError, TypeError):
            flash('Invalid cost value.', 'error')
            return redirect(url_for('edprovider.edproviderlanding'))

        # Prepare course data for insertion into `registration` collection
        registration_data = {
            "user_id": user_id,
            "email": user_email,
            "Industry": industry,
            "CourseName": course_name,
            "CourseType": course_type,
            "Duration": duration,
            "CourseStructure": course_structure,
            "KeyLearnings": key_learnings,
            "Cost": cost,
            "registration_date": datetime.utcnow()
        }

        # Insert the data into the `registration` collection
        mongo.db.registration.insert_one(registration_data)
        
        # Flash a success message
        flash("Course added successfully!", "success")

        # Redirect to the view_courses page to view the courses table
        return redirect(url_for('edprovider.view_courses'))

    return render_template('edproviderlanding.html')

# View Courses Route (Now from the `registration` collection)
@edprovider_bp.route('/view_courses', methods=['GET'])
def view_courses():
    page = request.args.get('page', 1, type=int)  # Get the current page, default to 1
    per_page = 6  # Set how many courses you want to display per page
    
    # Count total number of courses in `registration` collection for pagination
    total_courses = mongo.db.registration.count_documents({})
    total_pages = (total_courses + per_page - 1) // per_page  # Calculate total number of pages
    
    # Fetch courses for the current page from `registration` collection
    courses = mongo.db.registration.find().skip((page - 1) * per_page).limit(per_page)
    
    return render_template(
        'add_course.html',
        courses=courses,
        page=page,
        per_page=per_page,
        total_courses=total_courses,
        total_pages=total_pages  # Pass total pages to the template
    )
# Modify course route
@edprovider_bp.route('/modify_course_ajax/<course_id>', methods=['POST'])
def modify_course_ajax(course_id):
    from main import mongo

    # Retrieve form data, including the cost field
    industry = request.form.get('industry')
    course_name = request.form.get('course_name')
    course_type = request.form.get('course_type')
    duration = request.form.get('duration')
    course_structure = request.form.get('course_structure')
    key_learnings = request.form.get('key_learnings')
    cost = request.form.get('cost')

    # Update course data in the 'registration' collection
    updated_course = {
        "Industry": industry,
        "CourseName": course_name,
        "CourseType": course_type,
        "Duration": duration,
        "CourseStructure": course_structure,
        "KeyLearnings": key_learnings,
        "Cost": float(cost),
        "updated_at": datetime.now()
    }

    result = mongo.db.registration.update_one({"_id": ObjectId(course_id)}, {"$set": updated_course})

    if result.modified_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

# Delete course route
@edprovider_bp.route('/delete_course/<course_id>', methods=['POST'])
def delete_course(course_id):
    from main import mongo
    result = mongo.db.registration.delete_one({"_id": ObjectId(course_id)})
    if result.deleted_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})