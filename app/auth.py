from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo

auth_bp = Blueprint('auth', __name__)



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

            # Redirect based on the user role
            if user.get('role') == 'Migrant':
                return redirect(url_for('migrant.migrantlanding'))
            elif user.get('role') == 'Agent':
                return redirect(url_for('agent.agentlanding'))
            elif user.get('role') == 'Admin':
                return redirect(url_for('admin.adminlanding'))
            elif user.get('role') == 'Education Provider':
                session['university'] = user.get('university')
                university = user.get('university')
                print(university)
                return redirect(url_for('edprovider.edproviderlanding', university=university))
            else:
                return "Unsupported user type."

        login_error = "Your password or email is incorrect."

    return render_template('login_error.html', error=login_error)


# Signup route
@auth_bp.route('/signup', methods=["GET", "POST"])
def signup():
    mongo = PyMongo(current_app)

    if request.method == "POST":
        # Get the email, password, and user type (from the radio button selection)
        email = request.form.get('email').strip().lower()  # Ensure email is lowercase and trimmed
        password = request.form.get('pwd')
        user_type = request.form.get('user_type')  # Get the selected user type from the radio button

        # Check if email, password, and user type are provided
        if not email or not password:
            flash("Email and password are required", "danger")
            return redirect(url_for('auth.signup'))

        if not user_type:
            flash("Please select a profile type", "danger")
            return redirect(url_for('auth.signup'))

        # Check if the email already exists in the database
        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            flash("Email already exists", "danger")
            return redirect(url_for('auth.signup'))

        # Hash the password for secure storage
        password_hash = generate_password_hash(password)

        # Insert the new user into the database with their selected role
        user_id = mongo.db.users.insert_one({
            "email": email,  # Use email as the unique identifier
            "password_hash": password_hash,
            "role": user_type  # Store the user type from the radio button (Migrant or Agent)
        }).inserted_id

        # Set the session to the new user's ID and email
        session['user_id'] = str(user_id)
        session['email'] = email

        # Redirect the user based on their selected profile type (role)
        if user_type == 'Migrant':
            return redirect(url_for('migrant.migrantlanding'))
        elif user_type == 'Agent':
            return redirect(url_for('agent.agentlanding'))

    return render_template('signup.html')


@auth_bp.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('auth.login'))

# Login route
@auth_bp.route("/home")
def home():
    return render_template('index.html')