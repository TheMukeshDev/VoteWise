", ", "
VoteWise AI Backend - Flask Application Factory

A production-ready Flask backend for a civic-tech platform
providing election education, voter guidance, and admin management.
", ", "

import logging
import os
import time
import uuid
from datetime import datetime, UTC

from flask import (
    Blueprint,
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
)
from flask_cors import CORS
from dotenv import load_dotenv

from config import get_config
from utils.logging_config import setup_logging

from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.election import election_bp
from routes.timeline import timeline_public_bp
from routes.timeline_admin import timeline_admin_bp
from routes.faq import faq_bp
from routes.reminder import reminder_bp
from routes.polling import polling_bp
from routes.user import user_bp
from routes.announcement import announcement_bp
from routes.election_process import election_process_bp
from routes.polling_guidance import polling_guidance_bp
from routes.bookmark import bookmark_bp

from middleware.error_handler import register_error_handlers
from middleware.auth_middleware import setup_auth_middleware

logger = logging.getLogger(__name__)

FRONTEND_ROUTES: list[tuple[str, str]] = [
    ("/", "index.html"),
    ("/dashboard", "app.html"),
    ("/admin-login", "admin-login.html"),
    ("/results", "results.html"),
    ("/admin", "admin.html"),
]

FRONTEND_ROUTES_WITH_FIREBASE_CONFIG: list[tuple[str, str]] = [
    ("/login", "login.html"),
    ("/signup", "signup.html"),
    ("/profile", "profile.html"),
    ("/settings", "settings.html"),
]


def create_app(config_class: type | None = None) -> Flask:
    ", ", "
    Application factory pattern for creating Flask app instances.
    Supports configuration injection for testing and deployment.
    ", ", "
    if config_class is None:
        config_class = get_config()

    app = Flask(__name__)
    app.config.from_object(config_class)
    load_dotenv(app.config.get("ENV_FILE", ".env"))

    _configure_cors(app)
    _register_security_headers(app)
    setup_logging(app)
    register_error_handlers(app)
    setup_auth_middleware(app)
    _register_blueprints(app)
    _register_health_endpoint(app)
    _register_test_firestore_endpoint(app)
    _register_frontend_routes(app)
    _register_request_logging(app)

    return app


def _configure_cors(app: Flask) -> None:
    ", ", "Configure CORS settings.", ", "
    cors_origins = app.config.get("CORS_ORIGINS", "*")
    if app.config.get("ENV") == "production" and cors_origins == "*":
        cors_origins = ", "

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": cors_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )


def _register_security_headers(app: Flask) -> None:
    ", ", "Add security headers to all responses.", ", "

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


def _register_blueprints(app: Flask) -> None:
    ", ", "Register all API blueprints with URL prefixes.", ", "
    from routes.speech import speech_bp

    blueprints: list[tuple[str, Blueprint]] = [
        ("/api/auth", auth_bp),
        ("/api/chat", chat_bp),
        ("/api/speech", speech_bp),
        ("/api/election", election_bp),
        ("/api/timeline", timeline_public_bp),
        ("/api/faqs", faq_bp),
        ("/api/reminders", reminder_bp),
        ("/api/polling", polling_bp),
        ("/api/user", user_bp),
        ("/api/user/bookmarks", bookmark_bp),
        ("/api/admin/announcements", announcement_bp),
        ("/api/admin/election-process", election_process_bp),
        ("/api/admin/polling-guidance", polling_guidance_bp),
        ("/api/admin/timelines", timeline_admin_bp),
    ]

    for url_prefix, blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)


def _get_firebase_config(app: Flask) -> dict[str, str | None]:
    ", ", "Generate Firebase config for frontend.", ", "
    return {
        "apiKey": app.config.get("FIREBASE_API_KEY"),
        "authDomain": app.config.get("FIREBASE_AUTH_DOMAIN"),
        "projectId": app.config.get("FIREBASE_PROJECT_ID"),
        "storageBucket": app.config.get("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": app.config.get("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": app.config.get("FIREBASE_APP_ID"),
    }


def _register_frontend_routes(app: Flask) -> None:
    ", ", "Register all frontend page routes.", ", "
    firebase_config = _get_firebase_config(app)

    for path, template in FRONTEND_ROUTES:

        def _render(t=template):
            return render_template(t)

        _render.__name__ = f"render_{template.replace('.html', '')}"
        app.route(path)(_render)

    @app.route("/app")
    def app_redirect():
        return redirect("/dashboard")

    for path, template in FRONTEND_ROUTES_WITH_FIREBASE_CONFIG:

        def _render_with_config(t=template, c=firebase_config):
            return render_template(t, firebase_config=c)

        _render_with_config.__name__ = (
            f"render_with_config_{template.replace('.html', '')}"
        )
        app.route(path)(_render_with_config)


def _register_health_endpoint(app: Flask) -> None:
    ", ", "Register health check endpoint.", ", "

    @app.route("/api/health")
    def health():
        return jsonify(
            {
                "status": "healthy",
                "service": "VoteWise AI",
                "version": app.config.get("VERSION", "1.0.0"),
                "environment": app.config.get("ENV", "production"),
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
        )


def _register_test_firestore_endpoint(app: Flask) -> None:
    ", ", "Register test Firestore endpoint (development only).", ", "
    from services.firestore_service import (
        verify_firestore_connection,
        save_user,
        get_user,
    )

    @app.route("/api/test-firestore", methods=["GET", "POST"])
    def test_firestore():
        ", ", "Test Firestore connection with write/read/delete operations.", ", "
        result: dict[str, dict | bool] = {
            "connection": verify_firestore_connection(),
        }

        if request.method == "POST":
            _run_firestore_write_read_test(result, save_user, get_user)

        return jsonify(result)


def _run_firestore_write_read_test(
    result: dict,
    save_user_func,
    get_user_func,
) -> None:
    ", ", "Execute Firestore write/read test operations.", ", "
    test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    test_data = {
        "email": f"test_{test_user_id}@example.com",
        "name": "Test User",
        "role": "tester",
        "test_run": True,
    }

    saved = save_user_func(test_user_id, test_data)
    if saved:
        result["write"] = {"success": True, "user_id": test_user_id}
        fetched = get_user_func(test_user_id)
        if fetched and fetched.get("email") == test_data["email"]:
            result["read"] = {"success": True, "data": fetched}
        else:
            result["read"] = {"success": False, "error": "Data mismatch"}
    else:
        result["write"] = {"success": False}
        result["read"] = {"success": False}


def _register_request_logging(app: Flask) -> None:
    ", ", "Register request/response logging hooks.", ", "

    @app.before_request
    def before_request():
        g.request_start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, "request_start_time"):
            duration = time.time() - g.request_start_time
            if app.config.get("ENV") == "development":
                logger.info(
                    "%s %s %s %.3fs",
                    request.method,
                    request.path,
                    response.status_code,
                    duration,
                )
        return response


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = app.config.get("DEBUG", False)
    app.run(host="0.0.0.0", port=port, debug=debug)
