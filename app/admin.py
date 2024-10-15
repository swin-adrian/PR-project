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
        print(role)
        # Prepare user data
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": role,  # Ensure role is set during creation
            "created_at": datetime.now()
        }
        
                # If the role is Education Provider, store the university
        if role == 'Education Provider':
            user_data['university'] = university

        print(user_data)
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

# Route to display the inquiries
@admin_bp.route('/viewinquiries', methods=['GET'])
def viewinquiries():
    # Access the MongoDB instance
    mongo = PyMongo(current_app)

    # Fetch inquiries from the 'inquiries' collection
    inquiries_cursor = mongo.db.inquiries.find()
    inquiries = []

    for inquiry in inquiries_cursor:
        # Convert ObjectId fields to strings for JSON serialization
        inquiry["_id"] = str(inquiry["_id"])
        if "user_id" in inquiry:
            inquiry["user_id"] = str(inquiry["user_id"])

            # Fetch user email based on user_id
            user = mongo.db.users.find_one({"_id": ObjectId(inquiry["user_id"])})
            inquiry["user_email"] = user["email"] if user else "Unknown"
        else:
            inquiry["user_id"] = None
            inquiry["user_email"] = "Unknown"

        # Ensure 'inquiry' field exists
        if "inquiry" not in inquiry:
            inquiry["inquiry"] = "No inquiry provided"

        # Ensure 'status' field exists
        if "status" not in inquiry:
            inquiry["status"] = "Pending"

        # Format 'submitted_at' if necessary
        if "submitted_at" in inquiry:
            if isinstance(inquiry["submitted_at"], datetime):
                inquiry["submitted_at"] = inquiry["submitted_at"].strftime('%Y-%m-%d %H:%M:%S')
            else:
                inquiry["submitted_at"] = str(inquiry["submitted_at"])
        else:
            inquiry["submitted_at"] = "N/A"

        inquiries.append(inquiry)

    # Render the template and pass the inquiries data
    return render_template('viewinquiries.html', inquiries=inquiries)

# Route to modify an inquiry (update status)
@admin_bp.route('/modify_inquiry/<inquiry_id>', methods=['POST'])
def modify_inquiry(inquiry_id):
    mongo = PyMongo(current_app)
    status = request.form.get('status')
    if not status:
        return jsonify({"success": False, "message": "Status is required"}), 400

    # Update the 'status' field of the specific inquiry
    try:
        result = mongo.db.inquiries.update_one(
            {"_id": ObjectId(inquiry_id)},
            {"$set": {"status": status}}
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if result.modified_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Inquiry not found"}), 404

# Route to delete an inquiry
@admin_bp.route('/delete_inquiry/<inquiry_id>', methods=['POST'])
def delete_inquiry(inquiry_id):
    mongo = PyMongo(current_app)

    # Delete the inquiry with the given _id
    try:
        result = mongo.db.inquiries.delete_one({"_id": ObjectId(inquiry_id)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    if result.deleted_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Inquiry not found"}), 404


# Occupation lists

@admin_bp.route('/occupations', methods=['GET', 'POST'])
def occupations():
    # If a form is submitted (POST request)
    if request.method == 'POST':
        # Capture form data for adding a new occupation
        occupation_name = request.form.get('occupation')
        anzsco_code = request.form.get('anzsco_code')
        industry = request.form.get('industry')
        occupation_type = request.form.get('occupation_type')

        # Prepare the occupation data
        occupation_data = {
            "Occupation": occupation_name,
            "ANZSCOCode": anzsco_code,
            "Industry": industry,
            "Type": occupation_type,
            "created_at": datetime.now()
        }

        # Insert the occupation data into MongoDB
        from main import mongo
        mongo.db.occupations.insert_one(occupation_data)

        # Flash a success message
        flash("Occupation added successfully!", "success")
        # Redirect to the same page (occupationlanding) to prevent form re-submission on page refresh
        return redirect(url_for('admin.occupations'))

    # Handle GET request - Fetch occupations and implement pagination
    page = request.args.get('page', 1, type=int)  # Get the current page, default to 1
    per_page = 8  # Set how many occupations to display per page

    from main import mongo
    # Count total number of occupations for pagination
    total_occupations = mongo.db.occupations.count_documents({})
    total_pages = (total_occupations + per_page - 1) // per_page  # Calculate total number of pages

    # Fetch occupations for the current page
    occupations = mongo.db.occupations.find().skip((page - 1) * per_page).limit(per_page)

    # Render the occupationlanding.html template with all data
    return render_template(
        'occupations.html',
        occupations=occupations,
        page=page,
        per_page=per_page,
        total_occupations=total_occupations,
        total_pages=total_pages  # Pass total pages to the template for pagination
    )

# Route for searching occupations with pagination
@admin_bp.route('/search_occupations', methods=['GET', 'POST'])
def search_occupations():
    page = request.args.get('page', 1, type=int)  # Get the current page or default to 1
    per_page = 10  # Define how many items you want to display per page
    query = request.form.get('search_query') if request.method == 'POST' else request.args.get('search_query', '')

    from main import mongo
    # Search occupations by name, ANZSCO code, or industry
    search_filter = {
        "$or": [
            {"Occupation": {"$regex": query, "$options": "i"}},
            {"ANZSCOode": {"$regex": query, "$options": "i"}},
            {"Industry": {"$regex": query, "$options": "i"}}
        ]
    }

    # Count total matching occupations for pagination
    total_occupations = mongo.db.occupations.count_documents(search_filter)
    total_pages = (total_occupations + per_page - 1) // per_page  # Calculate total number of pages

    # Retrieve the relevant page of occupations
    occupations = mongo.db.occupations.find(search_filter).skip((page - 1) * per_page).limit(per_page)

    return render_template(
        'occupations.html',
        occupations=occupations,
        page=page,
        per_page=per_page,
        total_occupations=total_occupations,
        total_pages=total_pages,  # Pass total pages to the template
        search_query=query
    )
@admin_bp.route('/get_occupation_summary', methods=['GET'])
def get_occupation_summary():
    from main import mongo
    
    # Query the MongoDB collection for the occupation summary data
    total_occupations = mongo.db.occupations.count_documents({})
    agriculture_count = mongo.db.occupations.count_documents({"Industry": "Agriculture"})
    beekeeping_count = mongo.db.occupations.count_documents({"Industry": "Beekeeping"})
    other_count = mongo.db.occupations.count_documents({"Industry": {"$nin": ["Agriculture", "Beekeeping"]}})
    
    # Return summary as JSON
    return jsonify({
        "total_occupations": total_occupations,
        "agriculture_count": agriculture_count,
        "beekeeping_count": beekeeping_count,
        "other_count": other_count
    })

# Route for deleting an occupation using AJAX
@admin_bp.route('/delete_occupation/<occupation_id>', methods=['POST'])
def delete_occupation(occupation_id):
    from main import mongo
    result = mongo.db.occupations.delete_one({"_id": ObjectId(occupation_id)})
    if result.deleted_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

# AJAX route for modifying an occupation
@admin_bp.route('/modify_occupation_ajax/<occupation_id>', methods=['POST'])
def modify_occupation_ajax(occupation_id):
    from main import mongo
    updated_occupation = {
        "Occupation": request.form.get('occupation'),
        "ANZSCO code": request.form.get('anzsco_code'),
        "Industry": request.form.get('industry'),
        "Type": request.form.get('occupation_type'),
        "updated_at": datetime.now()
    }

    result = mongo.db.occupations.update_one(
        {"_id": ObjectId(occupation_id)}, 
        {"$set": updated_occupation}
    )

    if result.modified_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})