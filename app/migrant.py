from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime

migrant_bp = Blueprint('migrant', __name__)

@migrant_bp.route('/migrantlanding')
def migrantlanding():
    #tutor_id = session['user_id']
    return render_template('migrantlanding.html')
# tutor_bp route for tutor availability



