from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app
from flask_pymongo import PyMongo
from bson import ObjectId


agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agentlanding')
def agentlanding():
<<<<<<< HEAD
    user_id = session.get('user_id')  # Get the current agent's user_id from session
    mongo = PyMongo(current_app)
    # Query the 'agent_migrant' collection for the document where agentid matches the current user_id
    agent = mongo.db.agent_migrant.find_one({'agentid': user_id})

    # Count the total number of migrants by checking the length of 'migrantids' array
    total_migrants = len(agent['migrantids']) if agent and 'migrantids' in agent else 0

    # Render the agent landing page and pass the total_migrants count to the template
    return render_template('agentlanding.html', total_migrants=total_migrants)
=======
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
>>>>>>> a48f1bb36be0c4025dba1ae8ba3f22b66333d25d
