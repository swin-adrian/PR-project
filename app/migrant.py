from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


# Define the Blueprint before using it
migrant_bp = Blueprint('migrant', __name__)
@migrant_bp.route('/recommendcourse', methods=['GET', 'POST'])
def recommendcourse():
    try:
        if request.method == 'POST':
            # Collect user input from the form
            industry = request.form.get("industry")
            key_learnings = request.form.get("key_learnings")

            # Combine the user input into a single text string for comparison
            migrant_text = f"{industry} {key_learnings}"

            # Initialize MongoDB
            mongo = PyMongo(current_app)

            # Fetch courses from MongoDB
            courses_cursor = mongo.db.courses.find({})
            courses = list(courses_cursor)

            if not courses:
                return jsonify({"courses": []})  # No courses found

            # Convert ObjectId to string in the courses list
            for course in courses:
                course['_id'] = str(course['_id'])  # Convert ObjectId to string

            # Prepare course text for comparison (combine CourseStructure and KeyLearnings)
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
        else:
            return render_template('recommendcourse.html')
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500




@migrant_bp.route('/migrantlanding')
def migrantlanding():
    #tutor_id = session['user_id']
    return render_template('migrantlanding.html')
# tutor_bp route for tutor availability


@migrant_bp.route('/form')
def migrantform():
    #tutor_id = session['user_id']
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
        visa_subclass = request.form.get('visa-subclass')
        dob = request.form.get('dob')  # format: 'YYYY-MM-DD'
        etest = request.form.get('english-test')
        escore = request.form.get('ielts-score') if etest == "IELTS" else \
         request.form.get('pte-score') if etest == "PTE" else \
         request.form.get('cae-score') if etest == "CAE" else \
         request.form.get('oet-score') if etest == "OET" else \
         request.form.get('toefl-score') if etest == "TOEFL" else None
        owe = request.form.get('os-work-experience')
        awe = request.form.get('au-work-experience')
        eduqual = request.form.get('highest-qualification')
        ausqual = request.form.get('ausqual')
        rs = request.form.get('regionalStudy')
        squal = request.form.get('squal')
        acl = request.form.get('acl')
        partqual = request.form.get('partner-qualification')
        profyear = request.form.get('profyear')

        # 1. Mapping visa subclass
        visa_mapping = {"189": 0, "190": 1, "491": 2}
        visa_value = visa_mapping.get(visa_subclass, None)
        
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
        english_value = None  # Default value if no score or invalid data
        if escore:  # Proceed only if escore is not None or empty
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
                            pass  # In case escore is not a valid number
        
        # 4. Mapping education qualifications
        edu_mapping = {"no-qualification": 0, "diploma": 1, "bachelor": 2, "phd": 3}
        edu_value = edu_mapping.get(eduqual, None)

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
        partqual_value = partqual_mapping.get(partqual, None)

        # Creating the dictionary with numerical values
        score_data = {
            "visa_subclass": visa_value,
            "age": age,
            "english_score": english_value,
            "os_work_experience": owe,
            "au_work_experience": awe,
            "edu_qualification": edu_value,
            "aus_qualification": ausqual_value,
            "regional_study": rs_value,
            "specialist_qualification": squal_value,
            "australian_community_language": acl_value,
            "partner_qualification": partqual_value,
            "professional_year": profyear_value
        }

        individual_scores, total_score = calculate_scores(score_data)
        # Load the model
        model = joblib.load('logreg_model.pkl')
        
        # Preprocess the input data for prediction
        input_data = pd.DataFrame([score_data])
        input_data_scaled = StandardScaler().fit_transform(input_data)  # Assuming same scaling as in training
        
        # Predict PR probability
        pr_prob = model.predict_proba(input_data_scaled)[:, 1][0] * 100  # Convert to percentage

        pr_prob = round(pr_prob, 1)
        
        
        # You can now store or return the total score and individual scores as needed
        # Redirect to the results page with query parameters
        return redirect(url_for('migrant.results_page', total_score=total_score, pr_prob=pr_prob))  

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