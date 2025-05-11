from flask_login import current_user
from functools import wraps
from flask import jsonify

def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Authentication required"}), 401
            if current_user.role != role:
                return jsonify({"error": "Forbidden: insufficient role"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator
