", ", "
Error Handlers for VoteWise AI

Provides centralized error handling for the Flask application.
", ", "

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    ", ", "Base API error class.", ", "

    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "internal_error"

    def to_dict(self):
        return {"success": False, "message": self.message, "error": self.error_code}


class NotFoundError(APIError):
    ", ", "404 Not Found error.", ", "

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404, "not_found")


class UnauthorizedError(APIError):
    ", ", "401 Unauthorized error.", ", "

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401, "unauthorized")


class ForbiddenError(APIError):
    ", ", "403 Forbidden error.", ", "

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, 403, "forbidden")


class ValidationError(APIError):
    ", ", "400 Validation error.", ", "

    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, 400, "validation_error")


class ConflictError(APIError):
    ", ", "409 Conflict error.", ", "

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, 409, "conflict")


def register_error_handlers(app: Flask):
    ", ", "Register error handlers for the Flask app.", ", "

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(
            {
                "success": False,
                "message": error.description,
                "error": error.name.lower().replace(" , ", "_"),
            }
        ), error.code

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify(
            {"success": False, "message": "Endpoint not found", "error": "not_found"}
        ), 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify(
            {
                "success": False,
                "message": "Internal server error",
                "error": "internal_error",
            }
        ), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return jsonify(
            {
                "success": False,
                "message": "An unexpected error occurred",
                "error": "unexpected_error",
            }
        ), 500
