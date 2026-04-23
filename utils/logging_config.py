"""
Logging configuration for VoteWise AI.
"""

import logging
import sys
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)


class StandardFormatter(logging.Formatter):
    """Standard log format for development."""

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey
        + "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        + reset,
        logging.INFO: blue
        + "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        + reset,
        logging.WARNING: yellow
        + "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        + reset,
        logging.ERROR: red
        + "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        + reset,
        logging.CRITICAL: red
        + "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging(app):
    """
    Configure application logging.

    Args:
        app: Flask application instance
    """
    env = app.config.get("ENV", "production")

    if env == "production":
        formatter = JSONFormatter()
        handler = logging.StreamHandler(sys.stdout)
    else:
        formatter = StandardFormatter()
        handler = logging.StreamHandler(sys.stderr)

    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if env == "production" else logging.DEBUG)
    root_logger.addHandler(handler)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("flask_cors").setLevel(logging.WARNING)

    app.logger.setLevel(logging.DEBUG if env == "development" else logging.INFO)


def log_request(request, response=None, error=None):
    """
    Log an HTTP request.

    Args:
        request: Flask request object
        response: Flask response object (optional)
        error: Exception object (optional)
    """
    logger = logging.getLogger("votewise.request")

    log_data = {
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr,
    }

    if response:
        log_data["status_code"] = response.status_code

    if error:
        log_data["error"] = str(error)
        logger.error(json.dumps(log_data))
    else:
        logger.info(json.dumps(log_data))


def log_admin_action(user_id, action, resource, details=None):
    """
    Log an admin action.

    Args:
        user_id: Admin user ID
        action: Action performed (create, update, delete)
        resource: Resource type
        details: Additional details (optional)
    """
    logger = logging.getLogger("votewise.admin")

    log_data = {
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if details:
        log_data["details"] = details

    logger.info(json.dumps(log_data))


def log_integration_failure(service, error, context=None):
    """
    Log a Google integration failure safely.

    Args:
        service: Service name (maps, calendar, translate, etc.)
        error: Exception object
        context: Additional context (optional)
    """
    logger = logging.getLogger("votewise.integrations")

    log_data = {
        "service": service,
        "error_type": type(error).__name__,
        "context": context or {},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    logger.error(json.dumps(log_data))
