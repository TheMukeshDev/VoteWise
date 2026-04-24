"""
FAQ Routes for VoteWise AI

Public and admin FAQ management endpoints:
- GET /api/faqs - Get all FAQs
- GET /api/faqs/<id> - Get specific FAQ
- POST /api/admin/faqs - Create FAQ (admin)
- PUT /api/admin/faqs/<id> - Update FAQ (admin)
- DELETE /api/admin/faqs/<id> - Delete FAQ (admin)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware.auth_middleware import require_admin
from utils.response import success_response, error_response
from utils.validators import validate_required_fields, sanitize_string
from services.faq_service import FAQService

faq_bp = Blueprint("faq", __name__)
faq_service = FAQService()


@faq_bp.route("", methods=["GET"])
@faq_bp.route("/", methods=["GET"])
def get_faqs():
    """Get all FAQs with pagination (public)."""
    try:
        category = request.args.get("category")
        language = request.args.get("language", "en")

        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 20, type=int)

        page = max(1, page)
        limit = max(1, min(100, limit))

        faqs, total = faq_service.get_all_paginated(
            category=category, language=language, page=page, limit=limit
        )

        return jsonify(
            success_response(
                data={
                    "faqs": faqs or [],
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total or 0,
                        "pages": ((total or 0) + limit - 1) // limit,
                    },
                }
            )
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@faq_bp.route("/<faq_id>", methods=["GET"])
def get_faq(faq_id):
    """Get a specific FAQ (public)."""
    try:
        faq = faq_service.get_by_id(faq_id)

        if not faq:
            return jsonify(error_response("FAQ not found", 404)), 404

        return jsonify(success_response(data=faq)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@faq_bp.route("", methods=["POST"])
@faq_bp.route("/", methods=["POST"])
@require_admin
def create_faq():
    """Create a new FAQ (admin only)."""
    try:
        data = request.get_json() or {}

        # Validate required fields
        is_valid, missing = validate_required_fields(data, ["question", "answer"])
        if not is_valid:
            return jsonify(
                error_response(f"Missing required fields: {', '.join(missing)}", 400)
            ), 400

        # Create FAQ
        faq = faq_service.create(
            question=data["question"],
            answer=data["answer"],
            category=data.get("category", "general"),
            language=data.get("language", "en"),
        )

        return jsonify(
            success_response(message="FAQ created successfully", data=faq)
        ), 201

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@faq_bp.route("/<faq_id>", methods=["PUT"])
@require_admin
def update_faq(faq_id):
    """Update an FAQ (admin only)."""
    try:
        data = request.get_json() or {}

        faq = faq_service.update(faq_id, data)

        if not faq:
            return jsonify(error_response("FAQ not found", 404)), 404

        return jsonify(
            success_response(message="FAQ updated successfully", data=faq)
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@faq_bp.route("/<faq_id>", methods=["DELETE"])
@require_admin
def delete_faq(faq_id):
    """Delete an FAQ (admin only)."""
    try:
        success = faq_service.delete(faq_id)

        if not success:
            return jsonify(error_response("FAQ not found", 404)), 404

        return jsonify(success_response(message="FAQ deleted successfully")), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
