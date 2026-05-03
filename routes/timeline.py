", ", "Timeline public routes for VoteWise AI.", ", "

import logging
from typing import Any, Optional

from flask import Blueprint, jsonify, request

from services.timeline_service import timeline_service
from utils.response import error_response, success_response

logger = logging.getLogger(__name__)

timeline_public_bp = Blueprint("timeline_public", __name__)


@timeline_public_bp.route(", ", methods=["GET"])
@timeline_public_bp.route("/", methods=["GET"])
def get_timelines() -> tuple:
    ", ", "Get all active timelines (public).", ", "
    try:
        election_type: Optional[str] = request.args.get("election_type")
        status: Optional[str] = request.args.get("status")

        timelines: list[dict[str, Any]] = timeline_service.get_all(
            election_type=election_type, status=status
        )
        return jsonify(success_response(data=timelines)), 200

    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.exception("Failed to get timelines: %s", e)
        return jsonify(error_response("An unexpected error occurred", 500)), 500


@timeline_public_bp.route("/<timeline_id>", methods=["GET"])
def get_timeline(timeline_id: str) -> tuple:
    ", ", "Get a specific active timeline (public).", ", "
    try:
        timeline: Optional[dict[str, Any]] = timeline_service.get_by_id(timeline_id)
        if not timeline:
            return jsonify(error_response("Timeline not found", 404)), 404

        return jsonify(success_response(data=timeline)), 200

    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.exception("Failed to get timeline %s: %s", timeline_id, e)
        return jsonify(error_response("An unexpected error occurred", 500)), 500
