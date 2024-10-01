from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_moment import Moment
from flask_session import Session
from edprovider import edprovider_bp  # Import the education provider blueprint
from auth import auth_bp 
from migrant import migrant_bp
from admin import admin_bp
from agent import agent_bp

app = Flask(__name__)

# Configure MongoDB connection
app.config["MONGO_URI"] = "mongodb+srv://105250334:password007%21%21@cluster0.6vqz8.mongodb.net/flutter"


# Configure session to use Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = "Project51secretkey"
Session(app)

# Initialize PyMongo
mongo = PyMongo(app)

# Initialize Flask-Moment
moment = Moment(app)

# Register blueprints

app.register_blueprint(edprovider_bp)
app.register_blueprint(auth_bp)   
app.register_blueprint(migrant_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(agent_bp)



# Test route to check MongoDB connection
@app.route("/test_mongo")
def test_mongo():
    try:
        
        collections = mongo.db.list_collection_names()
        return f"Connected to MongoDB! Collections: {collections}"
    except Exception as e:
        return f"Failed to connect to MongoDB: {str(e)}"

# Define the index route
@app.route('/')

def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

