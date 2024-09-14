<<<<<<< HEAD
from flask import Blueprint, render_template, request, jsonify, current_app
from bson import ObjectId
from flask_pymongo import PyMongo
=======
from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
>>>>>>> new-somto2
from datetime import datetime

# Define the blueprint
edprovider_bp = Blueprint('edprovider', __name__)

<<<<<<< HEAD
@edprovider_bp.route('/edproviderlanding', methods=['GET'])
def edproviderlanding():
    mongo = PyMongo(current_app)
    courses = list(mongo.db.courses.find())  # Fetch the list of courses
    return render_template('edproviderlanding.html', courses=courses)

@edprovider_bp.route('/add_course_ajax', methods=['POST'])
def add_course_ajax():
    mongo = PyMongo(current_app)
    course_code = request.form.get('course_code')
    course_type = request.form.get('course_type')
    duration = request.form.get('duration')

    course_data = {
        "CourseCode": course_code,
        "CourseType": course_type,
        "Duration": duration,
        "created_at": datetime.now()
    }

    try:
        mongo.db.courses.insert_one(course_data)
        courses = list(mongo.db.courses.find())
        for course in courses:
            course["_id"] = str(course["_id"])  # Convert ObjectId to string
        return jsonify({"success": True, "courses": courses})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@edprovider_bp.route('/delete_course/<course_id>', methods=['POST'])
def delete_course(course_id):
    mongo = PyMongo(current_app)
    try:
        mongo.db.courses.delete_one({'_id': ObjectId(course_id)})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@edprovider_bp.route('/modify_course', methods=['POST'])
def modify_course():
    mongo = PyMongo(current_app)

    # Get form data
    course_id = request.form.get('course_id')
    updated_code = request.form.get('course_code')
    updated_type = request.form.get('course_type')
    updated_duration = request.form.get('duration')

    try:
        mongo.db.courses.update_one(
            {'_id': ObjectId(course_id)},
            {'$set': {
                'CourseCode': updated_code,
                'CourseType': updated_type,
                'Duration': updated_duration
            }}
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
=======
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

        # Prepare course data
        course_data = {
            "Industry": industry,
            "CourseName": course_name,
            "CourseType": course_type,
            "Duration": duration,
            "CourseStructure": course_structure,
            "KeyLearnings": key_learnings,
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

# Route for viewing the course table (course_table.html)
@edprovider_bp.route('/view_courses', methods=['GET'])
def view_courses():
    from main import mongo
    courses = mongo.db.courses.find().limit(10)
    return render_template('add_course.html', courses=courses)

# Route for searching courses
@edprovider_bp.route('/search_courses', methods=['POST'])
def search_courses():
    query = request.form.get('search_query')
    from main import mongo
    # Search courses by CourseName or Industry
    courses = mongo.db.courses.find({
        "$or": [
            {"CourseName": {"$regex": query, "$options": "i"}},
            {"Industry": {"$regex": query, "$options": "i"}}
        ]
    })
    return render_template('add_course.html', courses=courses)

# Route for deleting a course
@edprovider_bp.route('/delete_course/<course_id>', methods=['POST'])
def delete_course(course_id):
    from main import mongo
    mongo.db.courses.delete_one({"_id": ObjectId(course_id)})
    flash("Course deleted successfully!", "success")
    return redirect(url_for('edprovider.view_courses'))
>>>>>>> new-somto2
