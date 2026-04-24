"""
API Documentation for VoteWise AI

OpenAPI/Swagger documentation for all endpoints.
Returns JSON spec that can be imported into Swagger UI.
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
            "contact": {"name": "VoteWise Team", "url": "https://votewise.ai"},
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        },
        "servers": [{"url": "/api", "description": "Current API"}],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {"application/json": {"example": {"success": True, "data": {"status": "healthy"}}}}
                        }
                    }
                }
            },
            "/auth/login": {
                "post": {
                    "summary": "User login with Firebase token",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["id_token"],
                                    "properties": {"id_token": {"type": "string"}}
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Login successful"},
                        "401": {"description": "Invalid token"},
                    }
                }
            },
            "/chat/chat": {
                "post": {
                    "summary": "AI Chat with Gemini",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["message"],
                                    "properties": {"message": {"type": "string", "maxLength": 1000}}
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "AI response"},
                        "400": {"description": "Invalid request"},
                    }
                }
            },
            "/reminders": {
                "get": {
                    "summary": "Get user reminders",
                    "security": [{"BearerAuth": []}],
                    "responses": {"200": {"description": "List of reminders"}, "401": {"description": "Unauthorized"}}
                },
                "post": {
                    "summary": "Create reminder",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["title", "reminder_date"],
                                    "properties": {
                                        "title": {"type": "string"},
                                        "reminder_date": {"type": "string", "format": "date-time"},
                                        "description": {"type": "string"},
                                        "reminder_type": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {"201": {"description": "Created"}, "401": {"description": "Unauthorized"}}
                }
            },
            "/polling": {
                "get": {
                    "summary": "Find polling booth",
                    "parameters": [
                        {"name": "lat", "in": "query", "required": True, "schema": {"type": "number"}},
                        {"name": "lng", "in": "query", "required": True, "schema": {"type": "number"}}
                    ],
                    "responses": {"200": {"description": "Polling booth data"}, "400": {"description": "Missing lat/lng"}}
                }
            },
            "/faqs": {"get": {"summary": "Get FAQs", "responses": {"200": {"description": "List of FAQs"}}},
            "/timeline": {"get": {"summary": "Get election timeline", "responses": {"200": {"description": "Timeline data"}}},
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT token from /auth/login"
                }
            }
        },
        "tags": [
            {"name": "Auth", "description": "Authentication endpoints"},
            {"name": "Chat", "description": "AI Chat endpoints"},
            {"name": "User", "description": "User management"},
            {"name": "Elections", "description": "Election information"},
        ]
    }
    return jsonify(spec)
