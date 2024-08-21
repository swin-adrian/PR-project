from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime

edprovider_bp = Blueprint('edprovider', __name__)

@edprovider_bp.route('/edproviderlanding')
def edproviderlanding():
    #tutor_id = session['user_id']
    return render_template('edproviderlanding.html')
# tutor_bp route for tutor availability


