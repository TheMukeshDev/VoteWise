from flask import Blueprint, request, jsonify
from services.firestore_service import save_user, get_user
from utils.response_helper import success_response, error_response

user_bp = Blueprint('user', __name__)

@user_bp.route('/save', methods=['POST'])
def save():
    data = request.json or {}
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify(*error_response("user_id is required"))
        
    saved_id = save_user(user_id, data)
    if saved_id:
        return jsonify(success_response(message="User profile saved successfully"))
    return jsonify(*error_response("Failed to save user", 500))

@user_bp.route('/<id>', methods=['GET'])
def fetch_user(id):
    user_data = get_user(id)
    if user_data:
        return jsonify(success_response(data=user_data))
    return jsonify(*error_response("User not found", 404))
