from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from bson.objectid import ObjectId
from datetime import datetime
from flask_pymongo import PyMongo

# Define the blueprint
edprovider_bp = Blueprint('edprovider', __name__)

# Route to add a course (formerly edproviderlanding, now edprovideraddcourse.html)
@edprovider_bp.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        # Capture form data
        industry = request.form.get('industry')
        course_name = request.form.get('course_name')
        course_type = request.form.get('course_type')
        duration = request.form.get('duration')
        course_structure = request.form.get('course_structure')
        key_learnings = request.form.get('key_learnings')
        cost = request.form.get('cost')

        # Get the university from the user's session
        university = session.get('university')
        if not university:
            flash('University information is missing. Please log in again.', 'error')
            return redirect(url_for('auth.login'))

        # Validate and process the cost
        try:
            cost = float(cost)
            if cost < 0:
                flash('Cost cannot be negative.', 'error')
                return redirect(url_for('edprovider.add_course'))
        except (ValueError, TypeError):
            flash('Invalid cost value.', 'error')
            return redirect(url_for('edprovider.add_course'))

        # Prepare course data
        course_data = {
            "Industry": industry,
            "CourseName": course_name,
            "CourseType": course_type,
            "Duration": duration,
            "CourseStructure": course_structure,
            "KeyLearnings": key_learnings,
            "Cost": cost,
            "University": university,
            "CreatedAt": datetime.now()
        }

        # Insert the data into MongoDB
        from main import mongo
        mongo.db.courses.insert_one(course_data)

        # Flash a success message
        flash("Course added successfully!", "success")
        return redirect(url_for('edprovider.view_courses'))

    return render_template('edprovideraddcourse.html')  # Render the renamed template for adding courses


# Route for viewing courses (formerly view_courses, now edproviderviewcourse.html)
@edprovider_bp.route('/courses', methods=['GET'])
def view_courses():
    # Get the user's university from the session
    user_university = session.get('university')

    if not user_university:
        return jsonify({"error": "User session not found or university not specified."}), 400

    page = request.args.get('page', 1, type=int)
    per_page = 6

    from main import mongo
    # Count total number of registrations for the user's university
    total_registrations = mongo.db.registrations.count_documents({"university": user_university})
    total_pages = (total_registrations + per_page - 1) // per_page

    # Fetch registrations for the current page, filtering by university
    registrations = mongo.db.registrations.find({"university": user_university}).skip((page - 1) * per_page).limit(per_page)

    # Convert the cost field to a float for each registration
    registrations = [
        {**registration, "cost": float(registration.get("cost", 0.00)) if registration.get("cost") is not None else 0.00}
        for registration in registrations
    ]


    return render_template(
        'edproviderviewcourse.html',  # Use the renamed template for viewing courses
        registrations=registrations,
        page=page,
        per_page=per_page,
        total_registrations=total_registrations,
        total_pages=total_pages
    )



# Route for searching courses by first name, last name, or course name
@edprovider_bp.route('/search_courses', methods=['GET', 'POST'])
def search_courses():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    query = request.form.get('search_query') if request.method == 'POST' else request.args.get('search_query', '')

    from main import mongo
    # Get the user's university from the session
    user_university = session.get('university')

    if not user_university:
        return jsonify({"error": "User session not found or university not specified."}), 400

    # Search registrations by first_name, last_name, or course_name for the user's university
    search_filter = {
        "$and": [
            {"university": user_university},
            {"$or": [
                {"first_name": {"$regex": query, "$options": "i"}},
                {"last_name": {"$regex": query, "$options": "i"}},
                {"course_name": {"$regex": query, "$options": "i"}}
            ]}
        ]
    }

    # Count total matching registrations for pagination
    total_registrations = mongo.db.registrations.count_documents(search_filter)
    total_pages = (total_registrations + per_page - 1) // per_page

    # Retrieve the relevant page of registrations
    registrations = mongo.db.registrations.find(search_filter).skip((page - 1) * per_page).limit(per_page)

    return render_template(
        'edproviderviewcourse.html',
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
        "university": session.get('university')
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



# Route for course visuals (formerly edprovidervisuals, now edproviderlanding.html)
@edprovider_bp.route('/edproviderlanding', methods=['GET'])
def edproviderlanding():
    mongo = PyMongo(current_app)

    # Get the user's university from the session
    user_university = session.get('university')

    if not user_university:
        flash("Please log in to access this page", "error")
        return redirect(url_for('auth.login'))

    # Fetch registrations for the university
    registrations = list(mongo.db.registrations.find({'university': user_university}))
    if not registrations:
        flash("No registered students found for this university.", "error")
        return render_template('edproviderlanding.html', total_students=0, average_age=0, average_pr_score=0, average_pr_probability=0, top_nationalities=[], top_countries=[], gender_distribution=[], revenue=0, potential_revenue=0)

    student_ids = [reg['user_id'] for reg in registrations]
    total_students = len(student_ids)

    # Calculate the average age using students' dates of birth
    if total_students > 0:
        students_data = list(mongo.db.users.find({'_id': {'$in': student_ids}}, {'dob': 1, 'nationality': 1, 'current_country': 1, 'gender': 1}))
        total_age = 0
        age_count = 0
        for student in students_data:
            dob = student.get('dob')
            if dob:
                dob_dt = datetime.strptime(dob, '%Y-%m-%d')
                age = (datetime.today() - dob_dt).days // 365
                total_age += age
                age_count += 1
        average_age = total_age / age_count if age_count > 0 else 0
    else:
        average_age = 0

    # Calculate the average PR score and probability
    scores = list(mongo.db.scores.find({'user_id': {'$in': student_ids}}, {'total_score': 1, 'pr_probability': 1}))
    if scores:
        total_pr_score = sum(score.get('total_score', 0) for score in scores)
        total_pr_prob = sum(score.get('pr_probability', 0) for score in scores)
        average_pr_score = total_pr_score / len(scores)
        average_pr_probability = total_pr_prob / len(scores)
    else:
        average_pr_score = 0
        average_pr_probability = 0

    # Top 5 nationalities
    top_nationalities = list(mongo.db.users.aggregate([
        {'$match': {'_id': {'$in': student_ids}, 'nationality': {'$ne': None}}},
        {'$group': {'_id': '$nationality', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]))

    # Top 5 current countries
    top_countries = list(mongo.db.users.aggregate([
        {'$match': {'_id': {'$in': student_ids}, 'current_country': {'$ne': None}}},
        {'$group': {'_id': '$current_country', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]))

    # Gender distribution
    gender_distribution = list(mongo.db.users.aggregate([
        {'$match': {'_id': {'$in': student_ids}, 'gender': {'$ne': None}}},
        {'$group': {'_id': '$gender', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]))

    # Fetch top 5 registered courses
    top_registered_courses = list(mongo.db.registrations.aggregate([
        {"$match": {"university": user_university}},
        {"$group": {"_id": {"course_id": "$course_id", "course_name": "$course_name"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]))

    # Fetch top 5 saved courses
    top_saved_courses = list(mongo.db.saved_courses.aggregate([
        {"$unwind": "$course_ids"},
        {"$group": {"_id": "$course_ids", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]))

    # Fetch course names and costs for revenue calculation
    course_names_map = {
        str(course["_id"]): {"name": course["CourseName"], "cost": course["Cost"]}
        for course in mongo.db.courses.find({}, {"CourseName": 1, "Cost": 1})
    }

    # Calculate Revenue (Registered)
    revenue = 0
    for course in top_registered_courses:
        course_cost = course_names_map.get(str(course["_id"]["course_id"]), {}).get("cost", 0)
        revenue += course["count"] * course_cost

    # Calculate Potential Revenue (Saved)
    potential_revenue = 0
    for saved_course in top_saved_courses:
        course_cost = course_names_map.get(saved_course["_id"], {}).get("cost", 0)
        potential_revenue += saved_course["count"] * course_cost

    # Map saved course ids to course names
    for saved_course in top_saved_courses:
        saved_course["name"] = course_names_map.get(saved_course["_id"], {}).get("name", "Unknown Course")

    return render_template(
        'edproviderlanding.html',
        total_students=total_students,
        average_age=round(average_age, 1),
        average_pr_score=round(average_pr_score, 1),
        average_pr_probability=round(average_pr_probability, 1),
        top_nationalities=top_nationalities,
        top_countries=top_countries,
        gender_distribution=gender_distribution,
        revenue=round(revenue, 2),
        potential_revenue=round(potential_revenue, 2),
        top_registered_courses=top_registered_courses,
        top_saved_courses=top_saved_courses
    )




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
        course_name = registration.get('course_name', 'Unknown Course')
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
    # Render the inquiry page with the appropriate URLs for edproviders
    return render_template(
        'edprovider_userinquiry.html',  # Use specific HTML for edprovider
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



