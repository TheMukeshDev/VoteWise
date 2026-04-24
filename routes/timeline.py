"""
Timeline Public Routes for VoteWise AI

Public timeline endpoints:
- GET /api/timeline - Get all timelines (public)
- GET /api/timeline/<id> - Get specific timeline (public)
"""

from flask import Blueprint, request, jsonify
from utils.response import success_response, error_response
from services.timeline_service import timeline_service

timeline_public_bp = Blueprint("timeline_public", __name__)


@timeline_public_bp.route("", methods=["GET"])
@timeline_public_bp.route("/", methods=["GET"])
def get_timelines():
    """Get all active timelines (public)."""
    try:
        election_type = request.args.get("election_type")
        status = request.args.get("status")

        timelines = timeline_service.get_all(election_type=election_type, status=status)

        return jsonify(success_response(data=timelines)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@timeline_public_bp.route("/<timeline_id>", methods=["GET"])
def get_timeline(timeline_id):
    """Get a specific active timeline (public)."""
    try:
        timeline = timeline_service.get_by_id(timeline_id)

        if not timeline:
            return jsonify(error_response("Timeline not found", 404)), 404

        return jsonify(success_response(data=timeline)), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
