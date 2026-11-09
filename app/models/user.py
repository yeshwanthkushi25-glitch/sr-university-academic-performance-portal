"""
User Model and Role-Based Access Control
"""

from functools import wraps
from flask import jsonify, current_app
from flask_login import UserMixin, current_user
from app.extensions import login_manager


class User(UserMixin):
    """User representation for authentication and role authorization."""

    def __init__(self, id_, email, role):
        self.id = id_
        self.email = email
        self.role = role

    @staticmethod
    def get(user_id):
        from app.db import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, role FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(row["id"], row["email"], row["role"])
        return None

    @staticmethod
    def get_by_email(email):
        from app.db import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password_hash, role FROM users WHERE email = ?", (email.strip().lower(),))
        row = cursor.fetchone()
        conn.close()
        return row


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def roles_required(*roles):
    """Decorator to enforce role-based access control on routes."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"success": False, "error": "Authentication required. Please sign in."}), 401
            if current_user.role not in roles:
                return jsonify({"success": False, "error": "Insufficient permissions. Access denied."}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator
