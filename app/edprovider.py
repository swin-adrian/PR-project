from flask import Blueprint, render_template, request, redirect, url_for, flash
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
