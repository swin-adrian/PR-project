from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app, request
from flask_pymongo import PyMongo
from bson import ObjectId
from flask import jsonify




agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agentlanding')
def agentlanding():
    user_id = session.get('user_id')
    mongo = PyMongo(current_app)

    # Get the agent's email from the session
    agent_email = session.get('email')

    if not agent_email:
        flash("Please log in to access this page", "error")
        return redirect(url_for('auth.login'))

    # Find the agent's user data in the database
    agent = mongo.db.users.find_one({'_id': ObjectId(user_id), 'role': 'Agent'})
    if not agent:
        flash("Agent not found", "error")
        return redirect(url_for('auth.login'))

    # Find the agent's connections document where the agentid matches the current agent's user_id
    agent_connections = mongo.db.connections.find_one({'agentid': ObjectId(user_id)})
    migrant_ids = agent_connections['migrantids'] if agent_connections and 'migrantids' in agent_connections else []
    total_migrants = len(migrant_ids)

    # Calculate the average age using migrants' dates of birth
    if total_migrants > 0:
        migrants_data = list(mongo.db.users.find({'_id': {'$in': migrant_ids}}, {'dob': 1}))
        total_age = 0
        age_count = 0
        for migrant in migrants_data:
            dob = migrant.get('dob')
            if dob:
                dob_dt = datetime.strptime(dob, '%Y-%m-%d')
                age = (datetime.today() - dob_dt).days // 365
                total_age += age
                age_count += 1
        average_age = total_age / age_count if age_count > 0 else 0
    else:
        average_age = 0

    # Calculate the average PR score and probability
    scores = list(mongo.db.scores.find({'user_id': {'$in': migrant_ids}}, {'total_score': 1, 'pr_probability': 1}))
    if scores:
        total_pr_score = sum(score.get('total_score', 0) for score in scores)
        total_pr_prob = sum(score.get('pr_probability', 0) for score in scores)
        average_pr_score = total_pr_score / len(scores)
        average_pr_probability = total_pr_prob / len(scores)
    else:
        average_pr_score = 0
        average_pr_probability = 0

    # Find top 5 nationalities (capitalizing first letter)
    top_nationalities = list(mongo.db.users.aggregate([
        {'$match': {'_id': {'$in': migrant_ids}, 'nationality': {'$ne': None}}},
        {'$group': {'_id': {'$concat': [
            {'$toUpper': {'$substrCP': ['$nationality', 0, 1]}},
            {'$substrCP': ['$nationality', 1, {'$strLenCP': '$nationality'}]}
        ]}, 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]))

    # Find top 5 current countries (capitalizing first letter)
    top_countries = list(mongo.db.users.aggregate([
        {'$match': {'_id': {'$in': migrant_ids}, 'current_country': {'$ne': None}}},
        {'$group': {'_id': {'$concat': [
            {'$toUpper': {'$substrCP': ['$current_country', 0, 1]}},
            {'$substrCP': ['$current_country', 1, {'$strLenCP': '$current_country'}]}
        ]}, 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]))

    # Gender distribution data
    gender_distribution = list(mongo.db.users.aggregate([
        {'$match': {'_id': {'$in': migrant_ids}, 'gender': {'$ne': None}}},
        {'$group': {'_id': '$gender', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]))

    # Prepare data for the migrant table
    migrants_scores = list(mongo.db.scores.find({'user_id': {'$in': migrant_ids}}, {'user_id': 1, 'total_score': 1, 'pr_probability': 1}))
    migrants_data_map = {str(m['_id']): m for m in mongo.db.users.find({'_id': {'$in': migrant_ids}}, {'first_name': 1, 'last_name': 1})}

    # Combine migrant name, PR score, and probability
    migrants_data_combined = [
        {
            'full_name': f"{migrants_data_map.get(str(score['user_id']), {}).get('first_name', '')} {migrants_data_map.get(str(score['user_id']), {}).get('last_name', '')}",
            'total_score': score['total_score'],
            'pr_probability': score['pr_probability']
        }
        for score in migrants_scores if str(score['user_id']) in migrants_data_map
    ]

    return render_template(
        'agentlanding.html',
        agent=agent,
        total_migrants=total_migrants,
        average_age=round(average_age, 1),
        average_pr_score=round(average_pr_score, 1),
        average_pr_probability=round(average_pr_probability, 1),
        top_nationalities=top_nationalities,
        top_countries=top_countries,
        gender_distribution=gender_distribution,
        migrants_data=migrants_data_combined
    )



@agent_bp.route('/submit_inquiry', methods=['POST'])
def submit_inquiry():
    mongo = PyMongo(current_app)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch role from the user document
    user_role = user.get('role', 'Agent')

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

@agent_bp.route('/user_inquiry')
def user_inquiry():
    # Render the inquiry page with the appropriate URLs
    return render_template(
        'Userinquiry.html',
        submit_url=url_for('agent.submit_inquiry'),
        get_inquiries_url=url_for('agent.get_inquiries')
    )

@agent_bp.route('/get_inquiries', methods=['GET'])
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



@agent_bp.route('/my_migrants')
def my_migrants():
    user_id = session.get('user_id')  # Get the current agent's user_id from session
    mongo = PyMongo(current_app)

    if not user_id:
        flash("Please log in to access this page", "error")
        return redirect(url_for('auth.login'))

    # Find the agent's user data
    agent = mongo.db.users.find_one({'_id': ObjectId(user_id), 'role': 'Agent'})
    if not agent:
        flash("Agent not found", "error")
        return redirect(url_for('auth.login'))

    # Find the agent's connections document where the agentid matches the current agent's user_id
    agent_connections = mongo.db.connections.find_one({'agentid': ObjectId(user_id)})

    # Count the total number of migrants (migrantids array length)
    total_migrants = len(agent_connections['migrantids']) if agent_connections and 'migrantids' in agent_connections else 0

    # Find all migrants' details based on the migrantids array
    connections = mongo.db.users.find({
        '_id': {'$in': agent_connections['migrantids']} if agent_connections and 'migrantids' in agent_connections else []
    })

    # Prepare a list of migrant connections
    connections_list = [{
        'migrant_email': migrant['email'],
        'migrant_id': migrant['_id']
    } for migrant in connections]

    # Render the agent migrants page with connections and total migrants count
    return render_template('agent_migrants.html', agent=agent, connections=connections_list, total_migrants=total_migrants)

@agent_bp.route('/migrant/<migrant_id>', methods=['GET'])
def get_migrant_profile(migrant_id):
    mongo = PyMongo(current_app)

    # Fetch migrant's details from MongoDB using their ObjectId
    migrant = mongo.db.users.find_one({'_id': ObjectId(migrant_id)})

    if not migrant:
        return jsonify({"error": "Migrant not found"}), 404

    # Fetch PR score and probability from the scores collection
    score_data = mongo.db.scores.find_one({'user_id': ObjectId(migrant_id)})
    pr_score = score_data.get('total_score') if score_data else "N/A"
    pr_probability = score_data.get('pr_probability') if score_data else "N/A"

    # Return the migrant's information as a JSON response
    migrant_data = {
        'email': migrant.get('email'),
        'first_name': migrant.get('first_name'),
        'last_name': migrant.get('last_name'),
        'occupation': migrant.get('occupation'),
        'nationality': migrant.get('nationality'),
        'current_country': migrant.get('current_country'),
        'dob': migrant.get('dob'),
        'pr_score': pr_score,
        'pr_probability': pr_probability
    }

    return jsonify(migrant_data), 200

@agent_bp.route('/courses', methods=['GET'])
def get_courses():
    mongo = PyMongo(current_app)
    courses = list(mongo.db.courses.find({}))
    for course in courses:
        course['_id'] = str(course['_id'])  # Convert ObjectId to string for JSON compatibility
    return jsonify(courses)

@agent_bp.route('/linked_migrants', methods=['GET'])
def get_linked_migrants():
    user_id = session.get('user_id')
    mongo = PyMongo(current_app)

    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    agent_connections = mongo.db.connections.find_one({'agentid': ObjectId(user_id)})
    migrant_ids = agent_connections['migrantids'] if agent_connections and 'migrantids' in agent_connections else []

    migrants = list(mongo.db.users.find({'_id': {'$in': migrant_ids}}, {'first_name': 1, 'last_name': 1, 'email': 1}))
    for migrant in migrants:
        migrant['_id'] = str(migrant['_id'])  # Convert ObjectId to string for JSON compatibility
    return jsonify(migrants)

from datetime import datetime

@agent_bp.route('/recommend_course', methods=['POST'])
def recommend_course():
    mongo = PyMongo(current_app)
    data = request.get_json()
    agent_id = session.get('user_id')

    if not agent_id:
        return jsonify({"error": "User not logged in"}), 403

    # Create a new recommendation document
    recommendation = {
        "agent_id": ObjectId(agent_id),
        "migrant_id": ObjectId(data['migrant_id']),
        "course_id": ObjectId(data['course_id']),
        "feedback": data['feedback'],
        "recommended_at": datetime.utcnow()
    }

    mongo.db.recommendations.insert_one(recommendation)
    return jsonify({"message": "Recommendation submitted successfully"}), 200

@agent_bp.route('/agent_courses')
def agent_courses():
    agent_email=session.get('email')
    # Render the agent_courses.html template
    return render_template('agent_courses.html', agent_email=agent_email)
