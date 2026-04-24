from flask import Blueprint, request, jsonify
from services.maps_service import get_nearby_polling_booths
from utils.response import success_response, error_response

polling_bp = Blueprint("polling", __name__)


@polling_bp.route("", methods=["GET"])
def get_polling_booth():
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    if not lat or not lng:
        return jsonify(
            error_response("lat and lng are required query parameters", 400)
        ), 400

    try:
        result = get_nearby_polling_booths(lat, lng)
        if result:
            return jsonify(success_response(data=result)), 200
        return jsonify(error_response("Could not find polling booth", 500)), 500
    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500
