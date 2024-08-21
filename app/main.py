from flask import Flask,  render_template
from auth import auth_bp

#from flask_moment import Moment
#from flask_pymongo import PyMongo
#from flask_session import Session

from migrant import migrant_bp
from agent import agent_bp
from edprovider import edprovider_bp
#from utils import format_timedelta

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://adriansmyint:k1tT13uqwTNZFO7S@tipproject.uo3zhgb.mongodb.net/fabulousfive"

# Configure session to use Flask-Session
#app.config['SESSION_TYPE'] = 'filesystem'
#app.secret_key = "Project51secretkey"
#Session(app)
#mongo = PyMongo(app)
#moment = Moment(app)

#Creating app routes
app.register_blueprint(auth_bp)
app.register_blueprint(migrant_bp)
app.register_blueprint(agent_bp)
app.register_blueprint(edprovider_bp)
#app.register_blueprint(student_bp, url_prefix='/student')

# Adding the format_timedelta function to Jinja2 filters
#app.jinja_env.filters['format_timedelta'] = format_timedelta
@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
