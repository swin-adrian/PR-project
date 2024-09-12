from flask import Blueprint, render_template, request, jsonify, current_app
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime

edprovider_bp = Blueprint('edprovider', __name__)

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
