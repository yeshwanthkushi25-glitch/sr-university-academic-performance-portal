"""
SR University Academic Performance Portal - Application Factory
"""

import logging
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from app.config import get_config
from app.extensions import login_manager, csrf, talisman, CSP_POLICY
from app.db import init_db, seed_sample_data_if_empty


def create_app(config_name=None):
    """
    Application Factory for SR University Academic Performance Portal.
    Initializes Flask application, binds extensions, registers blueprints,
    configures structured logging, and sets up centralized error handlers.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_folder = os.path.join(base_dir, "templates")
    static_folder = os.path.join(base_dir, "static")

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder
    )

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Configure structured logging
    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # Initialize extensions
    login_manager.init_app(app)
    csrf.init_app(app)

    # Initialize Talisman with CSP allowing CDNs, fonts, and inline styles
    talisman.init_app(
        app,
        content_security_policy=CSP_POLICY,
        force_https=False,
        session_cookie_secure=False
    )

    # Unauthorized handler for Flask-Login
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error": "Authentication required. Please sign in."}), 401
        flash("Please sign in to access this feature.", "info")
        return redirect(url_for("auth.login", next=request.path))

    # Register modular blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # Register centralized error handlers
    register_error_handlers(app)

    # Initialize database tables and seeds if not testing
    with app.app_context():
        if not app.config.get("TESTING"):
            try:
                init_db(app)
                seed_sample_data_if_empty(app)
            except Exception as e:
                app.logger.error("Database initialization error: %s", e)

    return app


def register_error_handlers(app):
    """Registers standardized HTTP error handlers returning JSON or HTML based on request type."""

    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error": "Bad request", "details": str(e)}), 400
        return render_template("errors/400.html", error=e), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error": "Unauthorized", "details": str(e)}), 401
        return redirect(url_for("auth.login", next=request.path))

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error": "Forbidden - Insufficient permissions"}), 403
        return render_template("errors/403.html", error=e), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error": "Resource not found"}), 404
        return render_template("errors/404.html", error=e), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error("Internal Server Error: %s", e)
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"success": False, "error": "Internal server error"}), 500
        return render_template("errors/500.html", error=e), 500
