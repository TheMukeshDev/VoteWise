from flask import Blueprint, request, jsonify
from services.maps_service import get_nearby_polling_booths
from utils.response_helper import success_response, error_response

polling_bp = Blueprint('polling', __name__)

@polling_bp.route('/', methods=['GET'])
def get_polling_booth():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    
    if not lat or not lng:
        return jsonify(*error_response("lat and lng are required query parameters"))
        
    result = get_nearby_polling_booths(lat, lng)
    return jsonify(success_response(data=result))
