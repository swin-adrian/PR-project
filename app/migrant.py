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
        limited_courses = sorted_courses[:2]

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
        course_name = request.form.get('courseName')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        university = request.form.get('university')  # Capture the university from the form

        # Validate the data
        if not all([course_name, first_name, last_name, email, university]):
            return jsonify({"error": "Missing required fields"}), 400

        # Find the corresponding course in the "courses" collection by course_name
        course_data = mongo.db.courses.find_one({"CourseName": course_name})

        # If course is found, fetch the cost and key_learnings, otherwise set defaults
        if course_data:
            cost = course_data.get('Cost', 0.00)  # Default to 0.00 if cost is not available
            key_learnings = course_data.get('KeyLearnings', "Not available")
        else:
            cost = 0.00
            key_learnings = "Not available"

        # Store the registration data along with the course cost, key_learnings, and university
        registration_data = {
            "user_id": user_object_id,
            "course_name": course_name,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "university": university,  # Store the university information
            "cost": cost,  # Include the cost from the course
            "key_learnings": key_learnings,  # Include the key learnings from the course
            "registration_date": datetime.utcnow()
        }

        # Insert the registration data into the "registrations" collection
        mongo.db.registrations.insert_one(registration_data)

        return jsonify({"message": "Registration successful", "cost": cost, "key_learnings": key_learnings}), 200

    except Exception as e:
        print(f"Error occurred during registration: {e}")
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
    return render_template('Userinquiry.html', submit_url=url_for('migrant.submit_inquiry'))




