from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/user_management', methods=['GET', 'POST'])
def user_management():
    # If a form is submitted (POST request)
    if request.method == 'POST':
        # Capture form data for adding a new user
        email = request.form.get('email')
        role = request.form.get('role')

        # Prepare the user data
        user_data = {
            "email": email,
            "role": role,
            "created_at": datetime.now()
        }

        # Insert the user data into MongoDB
        from main import mongo
        mongo.db.users.insert_one(user_data)
        
        # Flash a success message
        flash("User account added successfully!", "success")
        # Redirect to the same page (adminlanding) to prevent form re-submission on page refresh
        return redirect(url_for('admin.user_management'))

    # Handle GET request - Fetch users and implement pagination
    page = request.args.get('page', 1, type=int)  # Get the current page, default to 1
    per_page = 6  # Set how many users to display per page
    
    from main import mongo
    # Count total number of users for pagination
    total_users = mongo.db.users.count_documents({})
    total_pages = (total_users + per_page - 1) // per_page  # Calculate total number of pages
    
    # Fetch users for the current page
    users = mongo.db.users.find().skip((page - 1) * per_page).limit(per_page)

    # Render the adminlanding.html template with all data
    return render_template(
        'user_management.html',
        users=users,
        page=page,
        per_page=per_page,
        total_users=total_users,
        total_pages=total_pages  # Pass total pages to the template for pagination
    )

# Route for searching users with pagination
@admin_bp.route('/search_users', methods=['GET', 'POST'])
def search_users():
    page = request.args.get('page', 1, type=int)  # Get the current page or default to 1
    per_page = 10  # Define how many items you want to display per page
    query = request.form.get('search_query') if request.method == 'POST' else request.args.get('search_query', '')

    from main import mongo
    # Search users by email or role
    search_filter = {
        "$or": [
            {"email": {"$regex": query, "$options": "i"}},
            {"role": {"$regex": query, "$options": "i"}}
        ]
    }

    # Count total matching users for pagination
    total_users = mongo.db.users.count_documents(search_filter)
    total_pages = (total_users + per_page - 1) // per_page  # Calculate total number of pages

    # Retrieve the relevant page of users
    users = mongo.db.users.find(search_filter).skip((page - 1) * per_page).limit(per_page)

    return render_template(
        'admin_view_users.html',
        users=users,
        page=page,
        per_page=per_page,
        total_users=total_users,
        total_pages=total_pages,  # Pass total pages to the template
        search_query=query
    )

# Route for deleting a user using AJAX
@admin_bp.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    from main import mongo
    result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

# AJAX route for modifying a user
@admin_bp.route('/modify_user_ajax/<user_id>', methods=['POST'])
def modify_user_ajax(user_id):
    from main import mongo
    updated_user = {
        "email": request.form.get('email'),
        "role": request.form.get('role'),
        "updated_at": datetime.now()
    }

    result = mongo.db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": updated_user}
    )

    if result.modified_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})






