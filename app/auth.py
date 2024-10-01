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

    if request.method == "POST":
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        if not email or not password:
            login_error = "Email and password are required."
            return render_template('login_error.html', error=login_error)

        # Query the user from the database
        user = mongo.db.users.find_one({"email": email})

        if user and check_password_hash(user["password_hash"], password):
            session['user_id'] = str(user['_id'])
            session['email'] = user.get('email')

            # Set the session for university if the user is an Education Provider
            if user.get('role') == 'Education Provider':
                session['university'] = user.get('university')  # Store university in session

            # Redirect based on the email domain or role
            if email.endswith('gmail.com'):
                return redirect(url_for('migrant.migrantlanding'))
            elif email.endswith('agent.com'):
                return redirect(url_for('agent.agentlanding'))
            elif email.endswith(('swinburne.edu.au', 'monash.edu.au', 'latrobe.edu.au')):
                return redirect(url_for('edprovider.edproviderlanding', university=user.get('university')))
            elif email.endswith('admin.com'):
                return redirect(url_for('admin.adminlanding'))
            else:
                return "Unsupported user type."

        login_error = "Your password or email is incorrect."

    return render_template('login_error.html', error=login_error)

# Function to detect the university based on the email domain
def detect_university(email):
    email_domain = email.split('@')[-1].lower().strip()

    if email_domain == 'latrobe.edu.au':
        return 'La Trobe'
    elif email_domain == 'swinburne.edu.au':
        return 'Swinburne'
    elif email_domain == 'monash.edu.au':
        return 'Monash'
    else:
        return None  # If the email doesn't match a known university

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

        # Detect the role based on the email using the detect_role() function
        role = detect_role(email)
        university = None

        # If the role is Education Provider, detect the university
        if role == "Education Provider":
            university = detect_university(email)
            if not university:
                flash("Email domain not recognized for university. Please use a valid university email.", "danger")
                return redirect(url_for('auth.signup'))

        # Hash the password for secure storage
        password_hash = generate_password_hash(password)

        # Insert the new user into the database with the detected role and optional university
        user_data = {
            "email": email,  # Use email as the unique identifier
            "password_hash": password_hash,
            "role": role,
        }

        if university:
            user_data['university'] = university  # Add university if the user is an Education Provider

        # Insert the new user
        user_id = mongo.db.users.insert_one(user_data).inserted_id

        # Set the session to the new user's ID and email, store university if applicable
        session['user_id'] = str(user_id)
        session['email'] = email

        if university:
            session['university'] = university

        # Redirect based on the detected role
        if role == 'Migrant':
            return redirect(url_for('migrant.migrantlanding'))
        elif role == 'Agent':
            return redirect(url_for('agent.agentlanding'))
        elif role == 'Education Provider':
            return redirect(url_for('edprovider.edproviderlanding', university=university))
        elif role == 'Admin':
            return redirect(url_for('admin.adminlanding'))
        else:
            return "Unsupported user type."

    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('auth.login'))