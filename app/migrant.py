from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from bson import ObjectId




# Define the Blueprint before using it
migrant_bp = Blueprint('migrant', __name__)
@migrant_bp.route('/recommendcourse', methods=['GET'])
def recommendcourse():
    try:
        # Initialize MongoDB
        mongo = PyMongo(current_app)
        
        # Get the user_id from the session and fetch the user's profile
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 403

        user_profile = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user_profile:
            return jsonify({"error": "User profile not found"}), 404

        # Extract the user's occupation
        user_occupation = user_profile.get("occupation", "")
        if not user_occupation:
            return jsonify({"error": "Occupation not found in profile"}), 400

        # Query the occupation collection to get the industry
        occupation_data = mongo.db.occupations.find_one({"Occupation": user_occupation})
        if not occupation_data:
            return jsonify({"error": "Occupation not found in database"}), 404

        # Extract the industry from the occupation data
        industry = occupation_data.get("Industry", "")
        if not industry:
            return jsonify({"error": "Industry not found for occupation"}), 404

        # Use the occupation and industry to form the comparison string
        migrant_text = f"{industry} {user_occupation}"

        # Fetch courses from MongoDB
        courses_cursor = mongo.db.courses.find({})
        courses = list(courses_cursor)

        if not courses:
            return jsonify({"courses": []})  # No courses found

        # Convert ObjectId to string in the courses list
        for course in courses:
            course['_id'] = str(course['_id'])  # Convert ObjectId to string

        # Prepare course text for comparison (combine Industry and KeyLearnings)
        course_texts = [f"{course.get('Industry', '')} {course.get('KeyLearnings', '')}" for course in courses]

        # Add user input to the course texts for comparison
        course_texts.append(migrant_text)

        # Apply TF-IDF to compare user input with courses
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(course_texts)

        # Get the similarity scores between the user input (last entry) and the courses
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

        # Assign similarity scores to courses
        for idx, score in enumerate(similarity_scores):
            courses[idx]['Similarity_Score'] = round(score * 100, 2)  # Convert to percentage

        # Sort the courses by similarity score (highest first)
        sorted_courses = sorted(courses, key=lambda x: x['Similarity_Score'], reverse=True)

        # Assign ranking points to the top courses
        if len(sorted_courses) > 0:
            sorted_courses[0]['Ranking_Points'] = 20  # Top course gets 20 points
        if len(sorted_courses) > 1:
            sorted_courses[1]['Ranking_Points'] = 15  # Second course gets 15 points
        for course in sorted_courses[2:]:
            course['Ranking_Points'] = 0  # Remaining courses get 0 points

        # Calculate total points (Similarity Score + Ranking Points)
        for course in sorted_courses:
            course['Total_Points'] = course['Similarity_Score'] + course['Ranking_Points']

        # Limit the number of courses to 2
        limited_courses = sorted_courses[:5]

        # Return the limited courses as a JSON response
        return jsonify({"courses": limited_courses})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500




@migrant_bp.route('/migrantlanding')
def migrantlanding():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')
    migrant_email = session.get('email')
    
    if user_id:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        first_name = user.get("first_name", "Migrant")
        occupation = user.get("occupation", "Unknown")
        profile_complete = user.get("profile_complete", False)

        # Fetch the industry from the "occupations" collection using the occupation
        occupation_data = mongo.db.occupations.find_one({"Occupation": occupation})
        industry = occupation_data.get("Industry", "Unknown") if occupation_data else "Unknown"

        # Fetch the user's PR score and probability from the "scores" collection
        score_data = mongo.db.scores.find_one({"user_id": ObjectId(user_id)})
        total_score = score_data.get("total_score", None) if score_data else None
        pr_prob = score_data.get("pr_probability", None) if score_data else None
    else:
        first_name = "Migrant"
        occupation = "Unknown"
        industry = "Unknown"
        profile_complete = False
        total_score = None
        pr_prob = None
    
    # Pass the score, probability, occupation, and industry to the template
    return render_template('migrantlanding.html', first_name=first_name, profile_complete=profile_complete, total_score=total_score, pr_prob=pr_prob, occupation=occupation, industry=industry, migrant_email=migrant_email)


@migrant_bp.route('/form')
def migrantform():
    user_id = session['user_id']
    print(user_id)
    return render_template('form.html')


@migrant_bp.route('/get_occupations', methods=["POST"])
def get_occupations():
    mongo = PyMongo(current_app)
    
    # Get the occupation type (mltssl, stsol, rol) from the POST request
    occupation_type = request.json.get('type')

    # Query MongoDB for occupations that match the selected type
    occupations_cursor = mongo.db.occupations.find({"Type": occupation_type})
    
    # Extract only the occupation names from the documents
    occupations = [occupation["Occupation"] for occupation in occupations_cursor]

    # If occupations are found, return them in JSON format
    if occupations:
        return jsonify(occupations)
    
    # If no occupations are found, return an empty list
    return jsonify([]), 404




@migrant_bp.route('/submit_migrant_form', methods=["POST"])
def submit_migrant_form():
    mongo = PyMongo(current_app)

    if request.method == "POST":
        # Collect form data
        visa_subclass = request.form.get('visa-subclass', 0)  # Default to 0 if missing
        occupation = request.form.get("occupation", "")
        first_name = request.form.get("first-name", "")
        last_name = request.form.get("last-name", "")
        dob = request.form.get('dob', '1970-01-01')  # Default to a valid date if missing
        nationality = request.form.get('nationality', "")
        current_country = request.form.get("current-country", "")
        etest = request.form.get('english-test', "")
        escore = request.form.get('ielts-score') if etest == "IELTS" else \
                 request.form.get('pte-score') if etest == "PTE" else \
                 request.form.get('cae-score') if etest == "CAE" else \
                 request.form.get('oet-score') if etest == "OET" else \
                 request.form.get('toefl-score') if etest == "TOEFL" else None
        escore = escore if escore is not None else 0  # Default to 0 if missing
        owe = request.form.get('os-work-experience', 0)  # Default to 0 if missing
        awe = request.form.get('au-work-experience', 0)  # Default to 0 if missing
        eduqual = request.form.get('highest-qualification', 0)  # Default to 0 if missing
        ausqual = request.form.get('ausqual', "no")
        rs = request.form.get('regionalStudy', "no")
        squal = request.form.get('squal', "no")
        acl = request.form.get('acl', "no")
        partqual = request.form.get('partner-qualification', "option4")
        profyear = request.form.get('profyear', "no")

        # 1. Mapping visa subclass
        visa_mapping = {"189": 0, "190": 1, "491": 2}
        visa_value = visa_mapping.get(visa_subclass, 0)  # Default to 0

        # 2. Convert DOB to age
        today = datetime.today()
        dob_dt = datetime.strptime(dob, '%Y-%m-%d')
        age = today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))

        # 3. Mapping English language scores
        english_mapping = {
            "IELTS": [(6, 0), (7, 1), (8, 2)],
            "OET": [("B", 0), ("B", 1), ("A", 2)],
            "TOEFL": [(64, 0), (98, 1), (113, 2)],
            "PTE": [(50, 0), (65, 1), (79, 2)],
            "CAE": [(169, 0), (185, 1), (200, 2)]
        }
        english_value = 0  # Default to 0
        if escore:
            if etest in english_mapping:
                scores = english_mapping[etest]
                for score, value in scores:
                    if etest == "OET":
                        if escore >= score:  # For OET score comparison (A or B)
                            english_value = value
                    else:
                        try:
                            if int(escore) >= score:  # For numerical scores
                                english_value = value
                        except ValueError:
                            pass

        # 4. Mapping education qualifications
        edu_mapping = {"no-qualification": 0, "diploma": 1, "bachelor": 2, "phd": 3}
        edu_value = edu_mapping.get(eduqual, 0)  # Default to 0

        # 5. Yes/No mappings
        ausqual_value = 1 if ausqual == "yes" else 0
        rs_value = 1 if rs == "yes" else 0
        squal_value = 1 if squal == "yes" else 0
        acl_value = 1 if acl == "yes" else 0
        profyear_value = 1 if profyear == "yes" else 0

        # 6. Partner qualification mapping
        partqual_mapping = {
            "option1": 3,
            "option2": 2,
            "option3": 1,
            "option4": 0
        }
        partqual_value = partqual_mapping.get(partqual, 0)  # Default to 0

        # Creating the dictionary with numerical values for scoring
        score_data = {
            "visa_subclass": visa_value,
            "age": age,
            "english_score": english_value,
            "os_work_experience": int(owe),
            "au_work_experience": int(awe),
            "edu_qualification": edu_value,
            "aus_qualification": ausqual_value,
            "regional_study": rs_value,
            "specialist_qualification": squal_value,
            "australian_community_language": acl_value,
            "partner_qualification": partqual_value,
            "professional_year": profyear_value
        }

        # Calculate scores using the provided function
        individual_scores, total_score = calculate_scores(score_data)

        # Load the model for PR prediction
        model = joblib.load('logreg_model.pkl')

        # Preprocess the input data for prediction
        input_data = pd.DataFrame([score_data])
        input_data_scaled = StandardScaler().fit_transform(input_data)  # Assuming the same scaling as in training

        # Predict PR probability
        pr_prob = model.predict_proba(input_data_scaled)[:, 1][0] * 100  # Convert to percentage
        pr_prob = round(pr_prob, 1)

        # Convert user_id to ObjectId before using it in MongoDB query
        user_id = session['user_id']
        user_object_id = ObjectId(user_id)  # Convert string to ObjectId

        # Store the user profile data in the "users" collection
        mongo.db.users.update_one(
            {"_id": user_object_id},  # Use ObjectId for the query
            {"$set": {
                "first_name": first_name,
                "last_name": last_name,
                "dob": dob,
                "nationality": nationality,
                "current_country": current_country,
                "occupation": occupation,
                "profile_complete": True  # Mark profile as complete
            }}
        )

        # Store or update the scores and probability in the "scores" collection
        score_data_to_store = {
            "user_id": user_object_id,  # Foreign key to reference the user
            "individual_scores": individual_scores,
            "total_score": total_score,
            "pr_probability": pr_prob
        }

        # Use replace_one to update the existing score document or insert a new one if not found
        mongo.db.scores.replace_one(
            {"user_id": user_object_id},  # Match the user_id
            score_data_to_store,
            upsert=True  # Insert if no existing document is found
        )

        # Redirect to the results page with the calculated total score and PR probability
        return redirect(url_for('migrant.migrantlanding', total_score=total_score, pr_prob=pr_prob))


def calculate_scores(score_data):
    # Score mappings based on the provided instructions
    visa_score_mapping = {0: 0, 1: 5, 2: 15}
    age_score_mapping = [
        (18, 24, 25), 
        (25, 32, 30), 
        (33, 39, 25), 
        (40, 44, 15)
    ]
    english_score_mapping = {0: 0, 1: 10, 2: 20}
    ose_score_mapping = [
        (0, 2, 0), 
        (3, 4, 5), 
        (5, 7, 10), 
        (8, float('inf'), 15)
    ]
    awe_score_mapping = [
        (0, 0, 0),
        (1, 2, 5), 
        (3, 4, 10), 
        (5, 7, 15), 
        (8, float('inf'), 20)
    ]
    edu_score_mapping = {0: 0, 1: 10, 2: 15, 3: 20}
    ausqual_score_mapping = {0: 0, 1: 5}
    yes_no_mapping = {0: 0, 1: 5} 
    spec_mapping = {0:0, 1: 10} # For regional study, ACL, professional year
    partner_qual_mapping = {0: 0, 1: 5, 2: 10, 3: 10}

    # Helper function to find the range score
    def get_range_score(value, mapping):
        for min_val, max_val, score in mapping:
            if min_val <= value <= max_val:
                return score
        return 0

    # Calculate individual scores
    visa_score = visa_score_mapping.get(score_data.get('visa_subclass'), 0)
    age_score = get_range_score(score_data.get('age', 0), age_score_mapping)
    english_score = english_score_mapping.get(score_data.get('english_score'), 0)
    ose_score = get_range_score(int(score_data.get('os_work_experience', 0)), ose_score_mapping)
    awe_score = get_range_score(int(score_data.get('au_work_experience', 0)), awe_score_mapping)
    edu_score = edu_score_mapping.get(score_data.get('edu_qualification'), 0)
    ausqual_score = ausqual_score_mapping.get(score_data.get('aus_qualification'), 0)
    rs_score = yes_no_mapping.get(score_data.get('regional_study'), 0)
    squal_score = spec_mapping.get(score_data.get('specialist_qualification'), 0)
    acl_score = yes_no_mapping.get(score_data.get('australian_community_language'), 0)
    partner_score = partner_qual_mapping.get(score_data.get('partner_qualification'), 0)
    profyear_score = yes_no_mapping.get(score_data.get('professional_year'), 0)

    # Create a dictionary for individual scores
    individual_scores = {
        "visa_score": visa_score,
        "age_score": age_score,
        "english_score": english_score,
        "os_work_experience_score": ose_score,
        "au_work_experience_score": awe_score,
        "edu_qualification_score": edu_score,
        "aus_qualification_score": ausqual_score,
        "regional_study_score": rs_score,
        "specialist_qualification_score": squal_score,
        "acl_score": acl_score,
        "partner_qualification_score": partner_score,
        "professional_year_score": profyear_score
    }

    # Calculate total score
    total_score = sum(individual_scores.values())

    return individual_scores, total_score

@migrant_bp.route('/results')
def results_page():
    total_score = request.args.get('total_score', default=0, type=float)
    pr_prob = request.args.get('pr_prob', default=0, type=float)
    
    # Render the template and pass the parameters
    return render_template('prscore.html', total_score=total_score, pr_prob=pr_prob)


@migrant_bp.route('/register_course', methods=['POST'])
def register_course():
    mongo = PyMongo(current_app)

    try:
        # Get the user_id from the session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 403

        user_object_id = ObjectId(user_id)

        # Get data from the request
        data = request.get_json()
        course_id = data.get('courseId')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')
        university = data.get('university')

        if not all([course_id, first_name, last_name, email, university]):
            return jsonify({"error": "Missing required fields"}), 400

        # Find the course by course_id
        course_data = mongo.db.courses.find_one({"_id": ObjectId(course_id)})
        if not course_data:
            return jsonify({"error": "Course not found"}), 404

        # Store the registration data along with all relevant course details
        registration_data = {
            "user_id": user_object_id,
            "course_id": course_id,
            "course_name": course_data.get('CourseName'),
            "industry": course_data.get('Industry', 'N/A'),
            "duration": course_data.get('Duration', 'N/A'),
            "university": university,
            "cost": course_data.get('Cost', 'N/A'),
            "registration_date": datetime.utcnow()
        }

        # Insert the registration into the registrations collection
        mongo.db.registrations.insert_one(registration_data)

        return jsonify({"message": "Course registered successfully!"}), 200

    except Exception as e:
        print(f"Error occurred during course registration: {e}")
        return jsonify({"error": "An error occurred while processing your registration."}), 500


    
@migrant_bp.route('/submit_inquiry', methods=['POST'])
def submit_inquiry():
    mongo = PyMongo(current_app)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch role from the user document
    user_role = user.get('role', 'Migrant')

    inquiry_content = request.form.get("inquiry")
    if not inquiry_content:
        return jsonify({"error": "Inquiry content is required."}), 400

    inquiry_data = {
        "user_id": ObjectId(user_id),
        "role": user_role,
        "inquiry": inquiry_content,
        "submitted_at": datetime.utcnow(),
        "status": "Pending"
    }

    mongo.db.inquiries.insert_one(inquiry_data)
    return jsonify({"message": "Inquiry submitted successfully!"}), 200


@migrant_bp.route('/userinquiry')
def user_inquiry():
    return render_template(
        'Userinquiry.html',
        submit_url=url_for('migrant.submit_inquiry'),
        get_inquiries_url=url_for('migrant.get_inquiries')
    )

@migrant_bp.route('/get_inquiries', methods=['GET'])
def get_inquiries():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])

    inquiries_cursor = mongo.db.inquiries.find({"user_id": ObjectId(user_id)})
    inquiries = []
    for inquiry in inquiries_cursor:
        submitted_at = inquiry.get('submitted_at', 'N/A')
        if isinstance(submitted_at, datetime):
            submitted_at = submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            submitted_at = str(submitted_at)
        inquiries.append({
            "inquiry": inquiry.get('inquiry', 'No inquiry provided'),
            "submitted_at": submitted_at,
            "status": inquiry.get('status', 'Pending')
        })

    return jsonify(inquiries)



@migrant_bp.route('/get_saved_courses', methods=['GET'])
def get_saved_courses():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    # Fetch saved courses for the user
    saved_data = mongo.db.saved_courses.find_one({"user_id": ObjectId(user_id)})
    saved_course_ids = saved_data.get("course_ids", []) if saved_data else []

    return jsonify({"saved_courses": saved_course_ids})

@migrant_bp.route('/save_course', methods=['POST'])
def save_course():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    course_id = request.json.get('course_id')
    if not course_id:
        return jsonify({"error": "No course ID provided"}), 400

    # Check if a saved_courses document exists for the user
    saved_data = mongo.db.saved_courses.find_one({"user_id": ObjectId(user_id)})

    if saved_data:
        # Update the document by adding the course to the array if it doesn't exist
        if course_id not in saved_data['course_ids']:
            mongo.db.saved_courses.update_one(
                {"user_id": ObjectId(user_id)},
                {"$push": {"course_ids": course_id}}
            )
    else:
        # Create a new document for the user with the course_id
        mongo.db.saved_courses.insert_one({
            "user_id": ObjectId(user_id),
            "course_ids": [course_id]
        })

    return jsonify({"message": "Course saved successfully!"})

@migrant_bp.route('/unsave_course', methods=['POST'])
def unsave_course():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    course_id = request.json.get('course_id')
    if not course_id:
        return jsonify({"error": "No course ID provided"}), 400

    # Remove the course from the saved courses array
    mongo.db.saved_courses.update_one(
        {"user_id": ObjectId(user_id)},
        {"$pull": {"course_ids": course_id}}
    )

    return jsonify({"message": "Course unsaved successfully!"})

# Route for rendering migrantcourses.html
@migrant_bp.route('/migrantcourses', methods=['GET'])
def migrantcourses():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')
    migrant_email=session.get('email')
    if not user_id:
        return redirect(url_for('auth.login'))  # Redirect to login if user is not logged in
    
    # Fetch additional data if necessary (registered courses, agent-recommended courses, etc.)
    return render_template('migrantcourses.html', migrant_email=migrant_email)

@migrant_bp.route('/get_saved_courses_details', methods=['GET'])
def get_saved_courses_details():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    # Fetch saved courses for the user
    saved_data = mongo.db.saved_courses.find_one({"user_id": ObjectId(user_id)})
    saved_course_ids = saved_data.get("course_ids", []) if saved_data else []

    # Fetch the course details for the saved courses
    saved_courses = []
    if saved_course_ids:
        saved_courses_cursor = mongo.db.courses.find({"_id": {"$in": [ObjectId(id) for id in saved_course_ids]}})
        for course in saved_courses_cursor:
            # Ensure all required fields are included, use default values if necessary
            saved_courses.append({
                "CourseID": str(course.get("_id")),
                "CourseName": course.get("CourseName", "N/A"),
                "Industry": course.get("Industry", "N/A"),
                "Duration": course.get("Duration", "N/A"),
                "University": course.get("University", "N/A"),  # Ensure "University" is included
                "Cost": course.get("Cost", "N/A")
            })

    return jsonify({"saved_courses": saved_courses})


@migrant_bp.route('/get_registered_courses', methods=['GET'])
def get_registered_courses():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    # Query to find registered courses for this user
    registered_courses = mongo.db.registrations.find({"user_id": ObjectId(user_id)})

    # Collect courses into a list
    course_list = []
    for course in registered_courses:
        course_data = {
            "CourseName": course.get('course_name'),
            "Industry": course.get('industry', 'N/A'),
            "Duration": course.get('duration', 'N/A'),
            "University": course.get('university', 'N/A')
        }
        course_list.append(course_data)

    # Return the list of registered courses
    if course_list:
        return jsonify({"courses": course_list})
    else:
        return jsonify({"courses": []})  # Return empty list if no registered courses


@migrant_bp.route('/get_recommended_courses_details', methods=['GET'])
def get_recommended_courses_details():
    try:
        # Initialize MongoDB
        mongo = PyMongo(current_app)
        
        # Get the user_id from the session and fetch the user's profile
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 403

        user_profile = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user_profile:
            return jsonify({"error": "User profile not found"}), 404

        # Extract the user's occupation
        user_occupation = user_profile.get("occupation", "")
        if not user_occupation:
            return jsonify({"error": "Occupation not found in profile"}), 400

        # Query the occupation collection to get the industry
        occupation_data = mongo.db.occupations.find_one({"Occupation": user_occupation})
        if not occupation_data:
            return jsonify({"error": "Occupation not found in database"}), 404

        # Extract the industry from the occupation data
        industry = occupation_data.get("Industry", "")
        if not industry:
            return jsonify({"error": "Industry not found for occupation"}), 404

        # Use the occupation and industry to form the comparison string
        migrant_text = f"{industry} {user_occupation}"

        # Fetch courses from MongoDB
        courses_cursor = mongo.db.courses.find({})
        courses = list(courses_cursor)

        if not courses:
            return jsonify({"courses": []})  # No courses found

        # Convert ObjectId to string in the courses list
        for course in courses:
            course['_id'] = str(course['_id'])  # Convert ObjectId to string

        # Prepare course text for comparison (combine Industry and KeyLearnings)
        course_texts = [f"{course.get('Industry', '')} {course.get('KeyLearnings', '')}" for course in courses]

        # Add user input to the course texts for comparison
        course_texts.append(migrant_text)

        # Apply TF-IDF to compare user input with courses
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(course_texts)

        # Get the similarity scores between the user input (last entry) and the courses
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

        # Assign similarity scores to courses
        for idx, score in enumerate(similarity_scores):
            courses[idx]['Similarity_Score'] = round(score * 100, 2)  # Convert to percentage

        # Sort the courses by similarity score (highest first)
        sorted_courses = sorted(courses, key=lambda x: x['Similarity_Score'], reverse=True)

        # Limit the number of courses to 5 (or change this limit as necessary)
        limited_courses = sorted_courses[:5]

        # Return the detailed recommended courses as a JSON response
        return jsonify({"recommended_courses": limited_courses})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500
    
@migrant_bp.route('/register_course_migrantcourses', methods=['POST'])
def register_course_migrantcourses():
    mongo = PyMongo(current_app)
    
    try:
        # Get the user_id from the session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 403

        user_object_id = ObjectId(user_id)

        # Get data from the request
        course_id = request.json.get('course_id')
        if not course_id:
            return jsonify({"error": "No course ID provided"}), 400

        # Find the course by course_id
        course_data = mongo.db.courses.find_one({"_id": ObjectId(course_id)})
        if not course_data:
            return jsonify({"error": "Course not found"}), 404

        # Store the registration data with all relevant course details
        registration_data = {
            "user_id": user_object_id,
            "course_id": course_id,
            "course_name": course_data.get('CourseName'),
            "industry": course_data.get('Industry', 'N/A'),  # Default to 'N/A' if missing
            "duration": course_data.get('Duration', 'N/A'),  # Default to 'N/A' if missing
            "university": course_data.get('University', 'N/A'),  # Default to 'N/A' if missing
            "cost": course_data.get('Cost', 'N/A'),  # Include cost if available
            "registration_date": datetime.utcnow()
        }

        # Insert the registration into the registrations collection
        mongo.db.registrations.insert_one(registration_data)

        return jsonify({"message": "Course registered successfully!"}), 200

    except Exception as e:
        print(f"Error occurred during course registration: {e}")
        return jsonify({"error": "An error occurred while processing your registration."}), 500



@migrant_bp.route('/save_course_migrantcourses', methods=['POST'])
def save_course_migrantcourses():
    mongo = PyMongo(current_app)

    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "User not logged in"}), 403

        course_id = request.json.get('course_id')
        if not course_id:
            return jsonify({"error": "No course ID provided"}), 400

        # Check if the user already has a saved_courses document
        saved_courses = mongo.db.saved_courses.find_one({"user_id": ObjectId(user_id)})

        if saved_courses:
            # Add the course to the user's saved courses if not already present
            if course_id not in saved_courses['course_ids']:
                mongo.db.saved_courses.update_one(
                    {"user_id": ObjectId(user_id)},
                    {"$push": {"course_ids": course_id}}
                )
        else:
            # If no saved_courses document exists, create a new one
            mongo.db.saved_courses.insert_one({
                "user_id": ObjectId(user_id),
                "course_ids": [course_id]
            })

        return jsonify({"message": "Course saved successfully!"}), 200

    except Exception as e:
        print(f"Error occurred during saving course: {e}")
        return jsonify({"error": "An error occurred while saving the course."}), 500

@migrant_bp.route('/myagent')
def myagent():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('auth.login'))  # Redirect to login if the user is not logged in

    # Find the connection document where the migrant is associated with an agent
    connection = mongo.db.connections.find_one({"migrantids": ObjectId(user_id)})
    agent = None
    recommended_courses = []

    if connection:
        # If a connection is found, get the agent's details using the agentid
        agent = mongo.db.users.find_one({"_id": ObjectId(connection['agentid'])})

        if agent:
            # Fetch the agent's recommended courses for this migrant
            recommendations_cursor = mongo.db.recommendations.find({"agent_id": agent['_id'], "migrant_id": ObjectId(user_id)})
            recommendations = list(recommendations_cursor)

            # Fetch course details for each recommended course
            for recommendation in recommendations:
                # Check if 'courseid' exists in the recommendation document
                course_id = recommendation.get('course_id')
                if course_id:
                    # Retrieve course details from the courses collection
                    course_details = mongo.db.courses.find_one({"_id": ObjectId(course_id)})
                    if course_details:
                        # Add the course details to the recommendation data
                        recommendation['CourseName'] = course_details.get('CourseName')
                        recommendation['Industry'] = course_details.get('Industry')
                        recommendation['CourseType'] = course_details.get('CourseType')
                        recommendation['Duration'] = course_details.get('Duration')
                        recommendation['Cost'] = course_details.get('Cost')
                        recommendation['Feedback'] = recommendation.get('feedback')  # Add feedback if available

                        # Add to the recommended_courses list
                        recommended_courses.append(recommendation)

    return render_template('myagent.html', agent=agent, recommended_courses=recommended_courses)


@migrant_bp.route('/findagent')
def findagent():
    mongo = PyMongo(current_app)
    
    # Fetch available agents
    agents_cursor = mongo.db.users.find({"role": "Agent"})
    agents = list(agents_cursor)
    
    return render_template('findagent.html', agents=agents)

@migrant_bp.route('/linkagent', methods=['POST'])
def linkagent():
    mongo = PyMongo(current_app)
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    agent_id = request.json.get('agent_id')
    if not agent_id:
        return jsonify({"error": "No agent ID provided"}), 400

    # Check if a connection already exists for the agent
    connection = mongo.db.connections.find_one({"agentid": ObjectId(agent_id)})

    if connection:
        # If a connection exists, add the migrant ID to the migrantids array if not already present
        if ObjectId(user_id) not in connection['migrantids']:
            mongo.db.connections.update_one(
                {"agentid": ObjectId(agent_id)},
                {"$push": {"migrantids": ObjectId(user_id)}}
            )
    else:
        # If no connection exists, create a new connection document
        mongo.db.connections.insert_one({
            "agentid": ObjectId(agent_id),
            "migrantids": [ObjectId(user_id)]
        })

    return jsonify({"message": "Agent linked successfully!"}), 200


