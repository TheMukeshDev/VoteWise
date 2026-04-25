"""
API Documentation for VoteWise AI

OpenAPI/Swagger documentation for all endpoints.
"""

from flask import Blueprint, jsonify, render_template

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/docs")
def api_docs():
    """Render OpenAPI documentation UI."""
    return render_template("docs.html")


@docs_bp.route("/openapi.json")
def openapi_spec():
    """Return OpenAPI 3.0 specification."""
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "VoteWise AI API",
            "description": "Civic-tech platform for election education and voter guidance",
            "version": "1.0.0",
        },
        "servers": [{"url": "/api", "description": "Current API"}],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {"200": {"description": "Service is healthy"}},
                }
            },
            "/auth/login": {
                "post": {
                    "summary": "User login",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["id_token"],
                                    "properties": {"id_token": {"type": "string"}},
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Login successful"},
                        "401": {"description": "Invalid token"},
                    },
                }
            },
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
    }
    return jsonify(spec)
