"""
Authentication Blueprint Routes for SR University Portal
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.blueprints.auth import auth_bp
from app.db import get_db
from app.models.user import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash, role FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row and check_password_hash(row["password_hash"], password):
        user = User(row["id"], email, row["role"])
        login_user(user)
        flash("Logged in successfully to SR University Portal.", "success")
        next_page = request.args.get("next") or url_for("main.index")
        return redirect(next_page)

    flash("Invalid credentials. Please verify your email and password.", "error")
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out securely.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "student")

    if not email or not password:
        flash("Email and password are required.", "error")
        return redirect(url_for("auth.register"))

    password_hash = generate_password_hash(password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                       (email, password_hash, role))
        conn.commit()
    except Exception as e:
        conn.close()
        flash("Registration failed: " + str(e), "error")
        return redirect(url_for("auth.register"))

    conn.close()
    flash("User registered successfully. You may now log in.", "success")
    return redirect(url_for("auth.login"))
