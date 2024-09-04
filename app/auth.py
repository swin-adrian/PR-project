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

        # Check if the user exists and verify the password
        if user and check_password_hash(user["password_hash"], password):

            if user['user_type'] == 'migrant':
                print("welcome Migrant")
                return redirect(url_for('migrant.migrantlanding'))
            elif user['user_type'] == 'agent':
                return redirect(url_for('agent.agentlanding'))
            elif user['user_type'] == 'edprovider':
                return redirect(url_for('edprovider.edproviderlanding'))
            elif user['user_type'] == 'Administrator':  
                return redirect(url_for('admin.adminlanding')) 
            return "Unsupported user type"

        login_error = "Your password or username is incorrect"  # Set the login error message

    return render_template('login_error.html', error=login_error)  # Pass the login error to the template


@auth_bp.route('/signup', methods=["GET", "POST"])
def signup():
    mongo = PyMongo(current_app)

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('pwd')

        # Check if email and password are provided
        if not email or not password:
            flash("Email and password are required", "danger")
            return redirect(url_for('auth.signup'))

        # Check if the email already exists in the database
        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            flash("Email already exists", "danger")
            return redirect(url_for('auth.signup'))

        # Hash the password for secure storage
        password_hash = generate_password_hash(password)

        # Insert the new user into the database
        user_id = mongo.db.users.insert_one({
            "email": email,
            "password_hash": password_hash
        }).inserted_id

        # Set the session to the new user's ID
        session['user_id'] = str(user_id)

        # Extract the domain from the email and redirect accordingly
        email_domain = email.split('@')[-1]

        if email_domain == 'gmail.com':
            return redirect(url_for('migrant.migrantlanding'))
        elif email_domain == 'agent.com':
            return redirect(url_for('agent.agentlanding'))
        elif email_domain == 'edprovider.com':
            return redirect(url_for('edprovider.edproviderlanding'))
        elif email_domain == 'admin.com':
            return redirect(url_for('admin.adminlanding'))
        else:
            flash("Unsupported email domain", "danger")
            return redirect(url_for('auth.signup'))

    return render_template('signup.html')


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/landing")

# Defining a route for 'landing.html' or the landing page
@auth_bp.route("/landing")
def landing():
    return render_template('landing.html')
