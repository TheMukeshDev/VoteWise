from flask import Blueprint, jsonify
from services.election_service import get_election_process, get_faqs, get_timeline
from utils.response import success_response

election_bp = Blueprint("election", __name__)


@election_bp.route("/process", methods=["GET"])
def get_election_process_handler():
    data = get_election_process()
    return jsonify(success_response(data=data))


@election_bp.route("/timeline", methods=["GET"])
def get_election_timeline():
    data = get_timeline()
    return jsonify(success_response(data=data))


@election_bp.route("/faqs", methods=["GET"])
def get_election_faqs():
    data = get_faqs()
    return jsonify(success_response(data=data))
