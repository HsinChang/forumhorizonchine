"""
decorators.py

Decorators for URL handlers

"""

from functools import wraps
from google.appengine.api import users
from flask import redirect, request, abort, flash, url_for
import flask_login as login

def login_required(func):
    """Requires standard login credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        user = login.current_user
        if user.is_anonymous():
            flash('login first!', 'error')
            return redirect(url_for('exhibitor.index'))
        return func(*args, **kwargs)
    return decorated_view

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        user = login.current_user
        if user.is_authenticated():
            if user.role != 'admin':
                abort(401)  # Unauthorized
            return func(*args, **kwargs)
        else:
            return redirect(url_for('admin.index'))
    return decorated_view
