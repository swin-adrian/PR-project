from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app
from flask_pymongo import PyMongo
from bson import ObjectId

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agentlanding')
def agentlanding():
    # Get the agent's email from the session
    agent_email = session.get('email')

    if not agent_email:
        flash("Please log in to access this page", "error")
        return redirect(url_for('auth.login'))

    # Initialize MongoDB connection
    mongo = PyMongo(current_app)
    
    # Find the agent's user data in the database
    agent = mongo.db.users.find_one({'email': agent_email, 'role': 'Agent'})
    if not agent:
        flash("Agent not found", "error")
        return redirect(url_for('auth.login'))

    # Find all connections where the agent is the agent_id
    connections = mongo.db.connections.aggregate([
        {'$match': {'agent_id': agent['_id']}},
        {
            '$lookup': {
                'from': 'users',  # Join with the users collection to get migrant details
                'localField': 'migrant_id',
                'foreignField': '_id',
                'as': 'migrant_details'
            }
        },
        {'$unwind': '$migrant_details'},  # Unwind to get individual migrant documents
        {'$project': {
            'migrant_email': '$migrant_details.email',  # Include only necessary fields
            'migrant_id': '$migrant_details._id'
        }}
    ])

    connections_list = list(connections)  # Convert cursor to list for easier handling

    # Render the agent landing template with connections
    return render_template('agentlanding.html', agent=agent, connections=connections_list)
