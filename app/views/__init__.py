from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user

def roles_required(*roles):
    """
    Decorator to restrict access to users with specific roles.
    Example:
        @employer_bp.route('/dashboard')
        @roles_required('employer')
        def dashboard():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                # 403 Forbidden
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
