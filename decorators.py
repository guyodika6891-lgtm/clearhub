from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(f): return role_required("admin")(f)
def staff_required(f): return role_required("admin", "staff")(f)
def student_required(f): return role_required("student")(f)