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
        email = request.form.get('email').strip().lower()
        password = request.form.get('pwd')
        user_type = request.form.get('user_type')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        company_name = request.form.get('company_name')
        abn = request.form.get('abn')
        phone = request.form.get('phone')

        if not email or not password:
            flash("Email and password are required", "danger")
            return redirect(url_for('auth.signup'))

        if not user_type:
            flash("Please select a profile type", "danger")
            return redirect(url_for('auth.signup'))

        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            flash("Email already exists", "danger")
            return redirect(url_for('auth.signup'))

        password_hash = generate_password_hash(password)

        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": user_type
        }

        if user_type == 'Agent':
            user_data.update({
                "first_name": first_name,
                "last_name": last_name,
                "company_name": company_name,
                "abn": abn,
                "phone": phone
            })

        user_id = mongo.db.users.insert_one(user_data).inserted_id
        session['user_id'] = str(user_id)
        session['email'] = email

        if user_type == 'Migrant':
            return redirect(url_for('migrant.migrantlanding'))
        elif user_type == 'Agent':
            return redirect(url_for('agent.agentlanding'))

    return render_template('signup.html')

# Route to handle user logout
@auth_bp.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('auth.home'))

# Login route
@auth_bp.route("/home")
def home():
    return render_template('index.html')