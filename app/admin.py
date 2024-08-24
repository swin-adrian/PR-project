from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from bson import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/adminlanding')
def adminlanding():
    return render_template('adminlanding.html')





