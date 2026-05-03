"""Election data routes for VoteWise AI."""

from typing import Any, Optional

from flask import Blueprint, jsonify

from services.election_service import get_election_process, get_faqs, get_timeline
from utils.response import success_response

election_bp = Blueprint("election", __name__)


@election_bp.route("/process", methods=["GET"])
def get_election_process_handler() -> tuple:
    """Get election process steps."""
    data: Optional[list[dict[str, Any]]] = get_election_process()
    return jsonify(success_response(data=data))


@election_bp.route("/timeline", methods=["GET"])
def get_election_timeline() -> tuple:
    """Get election timeline."""
    data: Optional[list[dict[str, Any]]] = get_timeline()
    return jsonify(success_response(data=data))


@election_bp.route("/faqs", methods=["GET"])
def get_election_faqs() -> tuple:
    """Get election FAQs."""
    data: Optional[list[dict[str, Any]]] = get_faqs()
    return jsonify(success_response(data=data))
