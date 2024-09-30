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

# Signup route
@auth_bp.route('/signup', methods=["GET", "POST"])
@auth_bp.route('/signup', methods=["GET", "POST"])
def signup():
    mongo = PyMongo(current_app)

    if request.method == "POST":
        email = request.form.get('email').strip().lower()
        password = request.form.get('pwd')

        if not email or not password:
            flash("Email and password are required", "danger")
            return redirect(url_for('auth.signup'))

        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            flash("Email already exists", "danger")
            return redirect(url_for('auth.signup'))

        password_hash = generate_password_hash(password)

        # Detect the role based on the email (including university detection)
        role = detect_role(email)

        # Store university for Education Providers if applicable
        university = None
        if role == 'Education Provider':
            university = 'University Name'  # Set this dynamically based on logic or input

        user_id = mongo.db.users.insert_one({
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "university": university  # Store university if applicable
        }).inserted_id

        session['user_id'] = str(user_id)
        session['email'] = email
        session['role'] = role

        # Store university in session for Education Providers
        if role == 'Education Provider':
            session['university'] = university

        if role == 'Migrant':
            return redirect(url_for('migrant.migrantlanding'))
        elif role == 'Agent':
            return redirect(url_for('agent.agentlanding'))
        elif role == 'Education Provider':
            return redirect(url_for('edprovider.edproviderlanding'))
        elif role == 'Admin':
            return redirect(url_for('admin.adminlanding'))
        else:
            flash("Unsupported email domain", "danger")
            return redirect(url_for('auth.signup'))

    return render_template('signup.html')
