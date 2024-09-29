from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo

auth_bp = Blueprint('auth', __name__)

# Detect role function must be defined before being used in signup and login
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

# Login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    mongo = PyMongo(current_app)
    login_error = None  # Initialize a variable for login error

    if request.method == "POST":  # Fix indentation here
        # Get the email and password, and convert the email to lowercase
        email = request.form.get('email').strip().lower()  # Ensure email is lowercase and trimmed
        password = request.form.get('password')  # Match the form's input name, possibly 'password' instead of 'pwd'

        # Check if email and password are provided
        if not email or not password:
            login_error = "Email and password are required."
            return render_template('login_error.html', error=login_error)

        # Access the "users" collection using the "mongo" object and query by email
        user = mongo.db.users.find_one({"email": email})

        # Check if the user exists and verify the password
        if user and check_password_hash(user["password_hash"], password):
            # Set the session with the user's email or ID
            session['user_id'] = str(user['_id'])  # Store user ID in the session
            session['email'] = user.get('email')  # Store email for easier use

            # Extract domain from email
            email_domain = user.get('email').split('@')[-1]

            # Redirect based on the email domain (migrant, agent, edprovider, admin)
            if email_domain == 'gmail.com':
                return redirect(url_for('migrant.migrantlanding'))
            elif email_domain == 'agent.com':
                return redirect(url_for('agent.agentlanding'))
            elif email_domain in ['swinburne.edu.au', 'monash.edu.au', 'latrobe.edu.au']:
                return redirect(url_for('edprovider.edproviderlanding', university=user.get('university')))
            elif email_domain == 'admin.com':
                return redirect(url_for('admin.adminlanding'))
            else:
                return "Unsupported user type."

        login_error = "Your password or email is incorrect."  # Set the login error message

    return render_template('login_error.html', error=login_error)  # Pass the login error to the template


# Signup route
@auth_bp.route('/signup', methods=["GET", "POST"])
def signup():
    mongo = PyMongo(current_app)

    if request.method == "POST": 
        # Get the email and password, and convert the email to lowercase
        email = request.form.get('email').strip().lower()  # Ensure email is lowercase and trimmed
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

        # Detect the role based on the email (including university detection)
        role = detect_role(email)

        # Insert the new user into the database
        user_id = mongo.db.users.insert_one({
            "email": email,  # Use email as the unique identifier
            "password_hash": password_hash,
            "role": role,  # Store the role based on email
        }).inserted_id

        # Set the session to the new user's ID, email, and role
        session['user_id'] = str(user_id)
        session['email'] = email
        session['role'] = role

        # Redirect based on the role
        if role == 'Migrant':
            return redirect(url_for('migrant.migrantlanding'))
        elif role == 'Agent':
            return redirect(url_for('agent.agentlanding'))
        elif role == 'Education Provider':
            return redirect(url_for('edprovider.edproviderlanding'))  # Redirect for university staff
        elif role == 'Admin':
            return redirect(url_for('admin.adminlanding'))
        else:
            flash("Unsupported email domain", "danger")
            return redirect(url_for('auth.signup'))

    return render_template('signup.html')
