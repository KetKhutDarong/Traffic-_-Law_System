from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime
import sqlite3
import hashlib
import os
import json
from config import Config
from utils.decorators import login_required, role_required, permission_required
from utils.db import get_db, init_db
from utils.rbac import check_permission
from routes.auth import auth_bp
from routes.user import user_bp
from routes.officer import officer_bp
from routes.admin import admin_bp
from routes.api import api_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register custom Jinja2 filters
def format_number(value):
    """Format number with commas"""
    if value is None:
        return "0"
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)

def from_json(value):
    """Convert JSON string to Python object"""
    if value is None or value == '':
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value

# Register filters
app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['fromjson'] = from_json

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(officer_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
