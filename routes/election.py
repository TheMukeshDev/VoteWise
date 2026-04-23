from flask import Blueprint, jsonify
from services.election_service import get_election_process, get_faqs, get_timeline
from utils.response_helper import success_response

election_bp = Blueprint('election', __name__)

@election_bp.route('/process', methods=['GET'])
def process():
    data = get_election_process()
    return jsonify(success_response(data=data))

@election_bp.route('/timeline', methods=['GET'])
def timeline():
    data = get_timeline()
    return jsonify(success_response(data=data))

@election_bp.route('/faqs', methods=['GET'])
def faqs():
    data = get_faqs()
    return jsonify(success_response(data=data))
