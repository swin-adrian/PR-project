from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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
        return 'Admin'

    # Education Provider (University) detection
    university_domains = ['swinburne.edu.au', 'monash.edu.au', 'latrobe.edu.au']
    if email_domain in university_domains:
        return 'Education Provider'

    # Agent detection
    elif 'agent' in email:
        return 'Agent'

    # Default to Migrant
    return 'Migrant'


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
        role = detect_role(email)

        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": role,  # Ensure role is set during creation
            "created_at": datetime.now()
        }

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
        
        # Create the connection object
        connection = {
            'migrant_id': ObjectId(migrant_id),
            'agent_id': ObjectId(agent_id)
        }
        
        # Insert into the connections collection
        mongo.db.connections.insert_one(connection)
        
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
                'localField': 'migrant_id',
                'foreignField': '_id',
                'as': 'migrant'
            }
        },
        {
            '$lookup': {
                'from': 'users',
                'localField': 'agent_id',
                'foreignField': '_id',
                'as': 'agent'
            }
        },
        {
            '$unwind': '$migrant'
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


@admin_bp.route('/delete_connection/<connection_id>', methods=['POST'])
def delete_connection(connection_id):
    from main import mongo
    mongo.db.connections.delete_one({'_id': ObjectId(connection_id)})
    flash("Connection deleted successfully!", "success")
    return redirect(url_for('admin.manage_connections'))
