from functools import wraps
from flask import session, redirect, flash


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first")
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get('role') != role:
                flash("Unauthorized access")
                return redirect('/login')
            return f(*args, **kwargs)
        return wrapper
    return decorator