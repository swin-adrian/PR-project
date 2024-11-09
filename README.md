Easi Resi - Skilled Migration PR Probability Prediction
---------------------------------------------------------
Overview
---------

The Easi Resi application is designed to help skilled migrants estimate their chances of obtaining Permanent Residency (PR) in Australia. The program collects relevant migrant data through a form, processes the information using a logistic regression model, and provides a PR probability score.

Requirements
-------------
Ensure you have the following dependencies installed to run the project successfully:

Python 3.8+
MongoDB Atlas (Authentication credentials already embedded in main.py)
Flask (for running the web server)
PyMongo (for connecting to MongoDB)
Scikit-learn (for machine learning model)
Jinja2 (for rendering HTML templates)
Visual Studio Build Tools 2022


Installation Steps
--------------------

1. Clone the Repository:

	git clone https://github.com/swin-adrian/PR-project.git


2. Navigate to PR-project Directory:
	cd PR-project


3. Install Required Packages: Install the necessary Python libraries by running:

	i. Flask (For creating the web server and routing)
	
		pip install Flask

	ii. PyMongo (For connecting to MongoDb Database)
	
		pip install pymongo

	iii. Scikit-learn (For the logistic regression model used for predicting PR probability)

		pip install scikit-learn

	iv.  Flask-PyMongo (to make PyMongo easier to use in Flask applications)
	
		pip install Flask-PyMongo

	v. Flask-Moment (typically used for date and time formatting in Flask applications)
	
		pip install Flask-Moment

	vi. Flask-Session (allows storing session data on the server-side)

		pip install Flask-Session==0.5.0

	vii. pandas
		
		pip install pandas
		
		


4. Run the main.py

	python app/main.py

The application should now be accessible at http://127.0.0.1:5000.


Program Structure
-------------------
PR-project/
│

├── app/

│ ├── admin.py - Contains routes specifically to execute admin role's features and functions

│ ├── agent.py - Contains routes specifically to execute agent role's features and functions


│ ├── auth.py - Contains user authentication and sign-up functions, redirecting users to different landing pages depending on their roles

│ ├── edprovider.py - Contains routes specifically to execute education provider role's features and functions

│ ├── load_data.py - Script to populate data in MongoDB

│ ├── courses_data.py - Script to populate courses data in MongoDB

│ ├── logreg_model.pkl - Logistic regression model to predict PR probability

│ ├── main.py - Python script to run the main app

│ ├── migrant.py - Contains routes specifically to execute migrant role's features and functions

│ ├── pr_algorithm.py - Script to train the PR model

│ ├── test_model.py - Test script to verify PR probability scores

│ ├── static/

│ │ ├── css/ - Contains all CSS files for styling the application

│ │ │ ├── images/ - Holds static images used across the application

│ │ ├── js/ - Includes JavaScript files for added functionality

│ ├── templates/ - Contains HTML templates for all pages

├── data/

│ ├── Occupation_list.csv - Occupation list to populate the MongoDB

│ ├── pr_train_data.csv - Dataset to train the PR model

│ ├── Updated_Courses_with_Dates.csv - Dataset to populate the MongoD



Test Credentials
-----------------

For Admin
username: adrian@admin.com
password: 1234

For Education Provider
username: adrian@swinburne.edu.au
password: 1234

For Agent
username: adrian@agent2.com
password: 1234

For Migrant
username: adrian@migrant.com
password: 1234




For questions or support, please contact:

Adrian: [104709550@student.swin.edu.au]


