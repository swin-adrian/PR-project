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

#App route to handle user signups
@auth_bp.route('/signup', methods=["GET", "POST"])
def signup():
    # Access the "mongo" object from the current app
    mongo = PyMongo(current_app)

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('pwd')
        user_type = request.form.get('acct')

        # Access the "users" collection using the "mongo" object
        existing_user = mongo.db.users.find_one({"username": username})

        if existing_user:
            flash("Username already exists", "danger")
            return "Username already exists"

        password_hash = generate_password_hash(password)

        user_id = mongo.db.users.insert_one({
            "username": username,
            "password_hash": password_hash,
            "acct": user_type,
        }).inserted_id

        session['user_id'] = user_id

        if user_type == 'tutor':
            return redirect(url_for('tutor.tutor_form'))

        if user_type == 'student':
            return redirect(url_for('student.student_form'))


        flash("Registration successful!", "success")
        return "Registration successful"

    return render_template('signup.html')

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/landing")

# Defining a route for 'landing.html' or the landing page
@auth_bp.route("/landing")
def landing():
    return render_template('landing.html')
