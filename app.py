"""
VoteWise AI Backend - Flask Application Factory

A production-ready Flask backend for a civic-tech platform
providing election education, voter guidance, and admin management.
"""

import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from config import get_config
from utils.logging_config import setup_logging, log_request
from utils.response import success_response

from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.election import election_bp
from routes.timeline import timeline_bp
from routes.faq import faq_bp
from routes.reminder import reminder_bp
from routes.polling import polling_bp
from routes.user import user_bp

from middleware.error_handler import register_error_handlers
from middleware.auth_middleware import setup_auth_middleware

logger = logging.getLogger(__name__)


def create_app(config_class=None):
    """
    Application factory pattern for creating Flask app instances.
    Supports configuration injection for testing and deployment.
    """
    if config_class is None:
        config_class = get_config()

    app = Flask(__name__)
    app.config.from_object(config_class)

    load_dotenv(app.config.get("ENV_FILE", ".env"))

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get("CORS_ORIGINS", "*"),
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    setup_logging(app)
    register_error_handlers(app)
    setup_auth_middleware(app)

    _register_blueprints(app)
    _register_frontend_routes(app)
    _register_request_logging(app)

    @app.route("/api/health")
    def health():
        return jsonify(
            {
                "status": "healthy",
                "service": "VoteWise AI",
                "version": app.config.get("VERSION", "1.0.0"),
                "environment": app.config.get("ENV", "production"),
                "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            }
        )

    return app


def _register_blueprints(app):
    """Register all API blueprints with URL prefixes."""

    blueprints = [
        ("/api/auth", auth_bp),
        ("/api/chat", chat_bp),
        ("/api/election", election_bp),
        ("/api/timeline", timeline_bp),
        ("/api/faqs", faq_bp),
        ("/api/reminders", reminder_bp),
        ("/api/polling", polling_bp),
        ("/api/user", user_bp),
    ]

    for url_prefix, blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)


def _get_firebase_config(app):
    """Generate Firebase config for frontend."""
    return {
        "apiKey": app.config.get("FIREBASE_API_KEY"),
        "authDomain": app.config.get("FIREBASE_AUTH_DOMAIN"),
        "projectId": app.config.get("FIREBASE_PROJECT_ID"),
        "storageBucket": app.config.get("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": app.config.get("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": f"1:{app.config.get('FIREBASE_MESSAGING_SENDER_ID')}:web:abc123def456",
    }


def _register_frontend_routes(app):
    """Register all frontend page routes."""

    firebase_config = _get_firebase_config(app)

    @app.route("/")
    def index():
        from flask import render_template

        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        from flask import render_template

        return render_template("app.html", firebase_config=firebase_config)

    @app.route("/login")
    def login_page():
        from flask import render_template

        return render_template("login.html", firebase_config=firebase_config)

    @app.route("/signup")
    def signup_page():
        from flask import render_template

        return render_template("signup.html", firebase_config=firebase_config)

    @app.route("/admin-login")
    def admin_login_page():
        from flask import render_template

        return render_template("admin-login.html")

    @app.route("/results")
    def results_page():
        from flask import render_template

        return render_template("results.html")

    @app.route("/admin")
    def admin_page():
        from flask import render_template

        return render_template("admin.html")

    @app.route("/profile")
    def profile_page():
        from flask import render_template

        return render_template("profile.html", firebase_config=firebase_config)

    @app.route("/settings")
    def settings_page():
        from flask import render_template

        return render_template("settings.html", firebase_config=firebase_config)


def _register_request_logging(app):
    """Register request/response logging hooks."""

    @app.before_request
    def before_request():
        from flask import g

        g.request_start_time = __import__("time").time()

    @app.after_request
    def after_request(response):
        from flask import g

        if hasattr(g, "request_start_time"):
            import time

            duration = time.time() - g.request_start_time
            if app.config.get("ENV") == "development":
                logger.info(
                    f"{request.method} {request.path} {response.status_code} {duration:.3f}s"
                )
        return response


app = create_app()

if __name__ == "__main__":
    port = app.config.get("PORT", 5000)
    debug = app.config.get("DEBUG", True)
    app.run(host="0.0.0.0", port=port, debug=debug)
