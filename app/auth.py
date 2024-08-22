from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo

auth_bp = Blueprint('auth', __name__)

#route for user login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Access the "mongo" object from the current app
    mongo = PyMongo(current_app)
    login_error = None  # Initialize a variable for login error

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Access the "users" collection using the "mongo" object
        user = mongo.db.users.find_one({"username": username})

        if user and user["password"]==password:

            if user['usertype'] == 'migrant':
                print("welcome Migrant")
                return redirect(url_for('migrant.migrantlanding'))
            elif user['usertype'] == 'agent':
                return redirect(url_for('agent.agentlanding'))
            elif user['usertype'] == 'edprovider':
                return redirect(url_for('edprovider.edproviderlanding'))
            return "Unsupported user type"

        #login_error = "Your password or username is incorrect"  # Set the login error message

    return render_template('login_error.html')  # Pass the login error to the template


@auth_bp.route('/signup', methods=["GET", "POST"])
def signup():
    
    mongo = PyMongo(current_app)

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('pwd')
        firstname = request.form.get('Firstname')
        lastname = request.form.get('Lastname')
        user_type = request.form.get('acct')  # This must be defined before use
        migrant_id = request.form.get('migrant_id')
        email = request.form.get('email')
        dob = request.form.get('dob')
        qualifications = request.form.get('qualifications')
        nationality = request.form.get('nationality')
        experience = request.form.get('experience')

        # Combine firstname and lastname
        name = f"{firstname} {lastname}"

        # Ensure user_type is defined before this condition
        if not username or not password or not user_type or not migrant_id or not name or not email:
            flash("All fields are required", "danger")
            return redirect(url_for('auth.signup'))

        # Check if the username already exists
        existing_user = mongo.db.users.find_one({"username": username})
        
        if existing_user:
            flash("Username already exists", "danger")
            return redirect(url_for('auth.signup'))

        # Hash the password for secure storage
        password_hash = generate_password_hash(password)

        # Insert the new user into the database
        user_id = mongo.db.users.insert_one({
            "username": username,
            "password_hash": password_hash,
            "user_type": user_type,  # This ensures user_type is saved correctly
            "migrant_id": migrant_id,
            "name": name,
            "email": email,
            "dob": dob,
            "qualifications": qualifications,
            "nationality": nationality,
            "experience": experience
        }).inserted_id

        # Set the session to the new user's ID
        session['user_id'] = str(user_id)

        # Redirect based on the user type
        if user_type == 'Skilled Migrant':
            return redirect(url_for('migrant.migrantlanding'))
        elif user_type == 'agent':
            return redirect(url_for('agent.agentlanding'))
        elif user_type == 'edprovider':
            return redirect(url_for('edprovider.edproviderlanding'))
        elif user_type == 'Adminstrator':
            return redirect(url_for('admin.adminlanding'))

        flash("Registration successful!", "success")
        return redirect(url_for('auth.index.html'))

    return render_template('signup.html')

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/landing")

# Defining a route for 'landing.html' or the landing page
@auth_bp.route("/landing")
def landing():
    return render_template('landing.html')
