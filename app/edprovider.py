from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime

edprovider_bp = Blueprint('edprovider', __name__)

@edprovider_bp.route('/edproviderlanding')
def edproviderlanding():
    #tutor_id = session['user_id']
    return render_template('edproviderlanding.html')
# tutor_bp route for tutor availability

@edprovider_bp.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        coursecode = request.form.get('coursecode')
        coursetype = request.form.get('coursetype')
        duration = request.form.get('duration')

        # Inserting course details into MongoDB
        course_data = {
            "CourseCode": coursecode,
            "CourseType": coursetype,
            "Duration": duration,
            "created_at": datetime.now()
        }

        try:
            mongo.db.courses.insert_one(course_data)
            flash("Course added successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")

        return redirect(url_for('edprovider.edproviderlanding'))
    
    return render_template('add_course.html')

