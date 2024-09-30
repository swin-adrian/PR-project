from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime


agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agentlanding')
def agentlanding():
    user_id = session.get('user_id')  # Get the current agent's user_id from session
    mongo = PyMongo(current_app)
    # Query the 'agent_migrant' collection for the document where agentid matches the current user_id
    agent = mongo.db.agent_migrant.find_one({'agentid': user_id})

    # Count the total number of migrants by checking the length of 'migrantids' array
    total_migrants = len(agent['migrantids']) if agent and 'migrantids' in agent else 0

    # Render the agent landing page and pass the total_migrants count to the template
    return render_template('agentlanding.html', total_migrants=total_migrants)
