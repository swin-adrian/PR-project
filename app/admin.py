from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime
from werkzeug.security import generate_password_hash

# Define the admin blueprint
admin_bp = Blueprint('admin', __name__)

def detect_role(email):
    """Detects the role based on the email with the new naming convention."""
    email_domain = email.split('@')[-1].strip().lower()  # Clean up the email domain

    # Admin detection
    if 'admin' in email:
        return 'Admin', None

    # Education Provider (University) detection
    university_domains = {
        'latrobe.edu.au': 'La Trobe',
        'swinburne.edu.au': 'Swinburne',
        'monash.edu.au': 'Monash'
    }

    if email_domain in university_domains:
        return 'Education Provider', university_domains[email_domain]

    # Agent detection
    elif 'agent' in email:
        return 'Agent', None

    # Default to Migrant
    return 'Migrant', None


@admin_bp.route('/adminlanding')
def adminlanding():
    return render_template('adminlanding.html')

@admin_bp.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password_hash')

        if not email or not password:
            flash("Email and Password are required fields.", "error")
            return redirect(url_for('admin.user_management'))

        password_hash = generate_password_hash(password)
        role, university = detect_role(email)  # Detect role and university

        # Prepare user data
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": role,  # Ensure role is set during creation
            "created_at": datetime.now()
        }
        print(user_data)
                # If the role is Education Provider, store the university
        if role == 'Education Provider':
            user_data['university'] = university


        from main import mongo
        try:
            mongo.db.users.insert_one(user_data)
            flash(f"User account added successfully with role '{role}'!", "success")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for('admin.user_management'))

    page = request.args.get('page', 1, type=int)
    per_page = 6

    from main import mongo
    total_users = mongo.db.users.count_documents({})
    total_pages = (total_users + per_page - 1) // per_page

    users = list(mongo.db.users.find().skip((page - 1) * per_page).limit(per_page))

    # Calculate user counts for each role
    user_counts = {
        'Admin': mongo.db.users.count_documents({'role': 'Admin'}),
        'Migrant': mongo.db.users.count_documents({'role': 'Migrant'}),
        'Education Provider': mongo.db.users.count_documents({'role': 'Education Provider'}),
        'Agent': mongo.db.users.count_documents({'role': 'Agent'})
    }
    
    # Ensure every user has a role, even older records
    for user in users:
        if 'role' not in user or user['role'] not in ['Admin', 'Edu Provider', 'Agent', 'Migrant']:
            role = detect_role(user['email'])
            mongo.db.users.update_one(
                {"_id": user['_id']},
                {"$set": {"role": role}}
            )
            user['role'] = role  # Update in local list as well

    return render_template(
        'user_management.html',
        users=users,
        page=page,
        per_page=per_page,
        total_users=total_users,
        total_pages=total_pages,
        user_counts=user_counts
    )

@admin_bp.route('/search_users', methods=['GET', 'POST'])
def search_users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    query = request.form.get('search_query') if request.method == 'POST' else request.args.get('search_query', '')

    from main import mongo
    search_filter = {
        "$or": [
            {"email": {"$regex": query, "$options": "i"}},
            {"role": {"$regex": query, "$options": "i"}}
        ]
    }

    total_users = mongo.db.users.count_documents(search_filter)
    total_pages = (total_users + per_page - 1) // per_page

    users = list(mongo.db.users.find(search_filter).skip((page - 1) * per_page).limit(per_page))
    
    # Ensure every user has a role
    for user in users:
        if 'role' not in user or user['role'] not in ['Admin', 'Edu Provider', 'Agent', 'Migrant']:
            role = detect_role(user['email'])
            mongo.db.users.update_one(
                {"_id": user['_id']},
                {"$set": {"role": role}}
            )
            user['role'] = role  # Update in local list as well

    return render_template(
        'user_management.html',
        users=users,
        page=page,
        per_page=per_page,
        total_users=total_users,
        total_pages=total_pages,
        search_query=query
    )

@admin_bp.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    from main import mongo
    result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@admin_bp.route('/modify_user_ajax/<user_id>', methods=['POST'])
def modify_user_ajax(user_id):
    from main import mongo
    email = request.form.get('email')
    password = request.form.get('password')

    if not email:
        return jsonify({"success": False, "message": "Email is required."})

    # Prepare the updated user data
    updated_user = {
        "email": email,
        "role": detect_role(email),  # Update role based on new email
        "updated_at": datetime.now()
    }

    # Only update password if provided
    if password:
        password_hash = generate_password_hash(password)
        updated_user["password_hash"] = password_hash

    result = mongo.db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": updated_user}
    )

    if result.modified_count > 0:
        return jsonify({"success": True, "role": updated_user["role"]})
    else:
        return jsonify({"success": False, "message": "Failed to update user."})



# Route to update all existing records
@admin_bp.route('/update_all_roles')
def update_all_roles():
    from main import mongo
    users = mongo.db.users.find()
    updated_count = 0
    for user in users:
        role = detect_role(user['email'])
        mongo.db.users.update_one(
            {"_id": user['_id']},
            {"$set": {"role": role}}
        )
        updated_count += 1
    return f"Updated roles for {updated_count} users."

@admin_bp.route('/manage_connections', methods=['GET', 'POST'])
def manage_connections():
    from main import mongo
    
    # Handle form submission for adding a new connection
    if request.method == 'POST':
        migrant_id = request.form.get('migrant_id')
        agent_id = request.form.get('agent_id')
        
        # Update the existing document or insert a new one
        mongo.db.connections.update_one(
            {'agentid': ObjectId(agent_id)},  # Match based on agent_id
            {
                '$addToSet': {'migrantids': ObjectId(migrant_id)}  # Add migrant_id to array if not present
            },
            upsert=True  # If document doesn't exist, insert a new one
        )
        
        flash("Connection added successfully!", "success")
        return redirect(url_for('admin.manage_connections'))
    
    # Fetch all migrants and agents
    migrants = list(mongo.db.users.find({'role': 'Migrant'}))
    agents = list(mongo.db.users.find({'role': 'Agent'}))
    
    # Fetch all connections with populated data
    connections = mongo.db.connections.aggregate([
        {
            '$lookup': {
                'from': 'users',
                'localField': 'migrantids',
                'foreignField': '_id',
                'as': 'migrants'
            }
        },
        {
            '$lookup': {
                'from': 'users',
                'localField': 'agentid',
                'foreignField': '_id',
                'as': 'agent'
            }
        },
        {
            '$unwind': '$agent'
        }
    ])
    
    return render_template(
        'manage_connections.html',
        migrants=migrants,
        agents=agents,
        connections=connections
    )

@admin_bp.route('/delete_connection/<agent_id>/<migrant_id>', methods=['POST'])
def delete_connection(agent_id, migrant_id):
    from main import mongo
    
    # Remove the specific migrant_id from the migrantids array of the agent document
    mongo.db.connections.update_one(
        {'agentid': ObjectId(agent_id)},
        {'$pull': {'migrantids': ObjectId(migrant_id)}}
    )
    
    # Optionally, you can delete the document if there are no more migrantids left
    mongo.db.connections.delete_one({'agentid': ObjectId(agent_id), 'migrantids': {'$size': 0}})
    
    flash("Connection deleted successfully!", "success")
    return redirect(url_for('admin.manage_connections'))


@admin_bp.route('/get_user_summary', methods=['GET'])
def get_user_summary():
    from main import mongo
    
    # Get counts of users by role
    total_users = mongo.db.users.count_documents({})
    admin_count = mongo.db.users.count_documents({"role": "Admin"})
    education_provider_count = mongo.db.users.count_documents({"role": "Education Provider"})
    migrant_count = mongo.db.users.count_documents({"role": "Migrant"})
    agent_count = mongo.db.users.count_documents({"role": "Agent"})

    # Return the counts as a JSON response
    return jsonify({
        "total_users": total_users,
        "admin_count": admin_count,
        "education_provider_count": education_provider_count,
        "migrant_count": migrant_count,
        "agent_count": agent_count
    })


# 1. Endpoint to get the top 5 countries of Migrant users
@admin_bp.route('/api/top-countries', methods=['GET'])
def get_top_countries():

    # Initialize MongoDB
    mongo = PyMongo(current_app)

    try:
        # Use the shared mongo instance from db.py
        top_countries = list(mongo.db.users.aggregate([
            {"$match": {"role": "Migrant"}},
            {"$group": {"_id": "$current_country", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]))
        return jsonify(top_countries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 2. Endpoint to get the number of users by age
@admin_bp.route('/api/users-by-age', methods=['GET'])
def get_users_by_age():
    mongo = PyMongo(current_app)
    try:
        # Calculate the age of users and count the number of users by age
        users_by_age = list(mongo.db.users.aggregate([
            {"$match": {"role": "Migrant"}},
            {"$addFields": {"age": {"$subtract": [{"$year": {"$dateFromString": {"dateString": "$dob"}}}, 1970]}}},
            {"$group": {"_id": "$age", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]))
        return jsonify(users_by_age)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 3. Endpoint to get the number of users by type of English test
@admin_bp.route('/api/users-by-test', methods=['GET'])
def get_users_by_test():
    mongo = PyMongo(current_app)
    try:
        # Group by the type of English test and count the number of users for each test type
        users_by_test = list(mongo.db.users.aggregate([
            {"$match": {"role": "Migrant"}},
            {"$group": {"_id": "$english_test", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]))
        return jsonify(users_by_test)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin_dashboard_m')
def admin_dashboard_m():
    #tutor_id = session['user_id']
    return render_template('admindashboard_m.html')