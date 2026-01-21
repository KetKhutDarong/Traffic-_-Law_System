from functools import wraps
from flask import session, redirect, url_for, flash
from utils.rbac import check_permission

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login first', 'error')
                return redirect(url_for('auth.login'))
            if session.get('role') != role:
                flash('Access denied', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login first', 'error')
                return redirect(url_for('auth.login'))
            if not check_permission(session.get('role'), permission):
                flash('You do not have permission for this action', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
