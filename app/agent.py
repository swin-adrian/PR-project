from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app
from flask_pymongo import PyMongo
from bson import ObjectId

agent_bp = Blueprint('agent', __name__)

@agent_bp.route('/agentlanding')
def agentlanding():
    user_id = session.get('user_id')  # Get the current agent's user_id from session
    mongo = PyMongo(current_app)

    # Get the agent's email from the session
    agent_email = session.get('email')

    if not agent_email:
        flash("Please log in to access this page", "error")
        return redirect(url_for('auth.login'))

    # Initialize MongoDB connection
    mongo = PyMongo(current_app)
    
    # Find the agent's user data in the database
    agent = mongo.db.users.find_one({'_id': ObjectId(user_id), 'role': 'Agent'})
    if not agent:
        flash("Agent not found", "error")
        return redirect(url_for('auth.login'))

    # Find the agent's connections document where the agentid matches the current agent's user_id
    agent_connections = mongo.db.connections.find_one({'agentid': ObjectId(user_id)})

    # Count the total number of migrants (migrantids array length)
    total_migrants = len(agent_connections['migrantids']) if agent_connections and 'migrantids' in agent_connections else 0

    # Find all migrants' details based on the migrantids array
    connections = mongo.db.users.find({
        '_id': {'$in': agent_connections['migrantids']} if agent_connections and 'migrantids' in agent_connections else []
    })

    # Prepare a list of migrant connections
    connections_list = [{
        'migrant_email': migrant['email'],
        'migrant_id': migrant['_id']
    } for migrant in connections]

    # Render the agent landing template with connections and total migrants count
    return render_template('agentlanding.html', agent=agent, connections=connections_list, total_migrants=total_migrants)

@agent_bp.route('/submit_inquiry', methods=['POST'])
def submit_inquiry():
    mongo = PyMongo(current_app)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 403

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch role from the user document
    user_role = user.get('role', 'Agent')

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

@agent_bp.route('/user_inquiry')
def user_inquiry():
    # Render the common inquiry page with the agent submit URL
    return render_template('Userinquiry.html', submit_url=url_for('agent.submit_inquiry'))
