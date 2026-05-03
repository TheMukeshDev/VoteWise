", ", "Polling Booth Routes for VoteWise AI", ", "

from flask import Blueprint, request, jsonify
from services.maps_service import get_nearby_polling_booths
from utils.response import success_response, error_response
from typing import Optional, Any


polling_bp = Blueprint("polling", __name__)


def _validate_coordinates(lat: Optional[str], lng: Optional[str]) -> bool:
    ", ", "Validate latitude and longitude are within valid ranges.", ", "
    try:
        lat_float: float = float(lat)
        lng_float: float = float(lng)
        return -90 <= lat_float <= 90 and -180 <= lng_float <= 180
    except (TypeError, ValueError):
        return False


@polling_bp.route(", ", methods=["GET"])
def get_polling_booth() -> tuple:
    ", ", "Get nearby polling booth for given coordinates.", ", "
    lat: Optional[str] = request.args.get("lat")
    lng: Optional[str] = request.args.get("lng")

    if not lat or not lng:
        return jsonify(
            error_response("lat and lng are required query parameters", 400)
        ), 400

    if not _validate_coordinates(lat, lng):
        return jsonify(
            error_response(
                "Invalid coordinates. Lat must be -90 to 90, Lng must be -180 to 180",
                400,
            )
        ), 400

    result: Optional[dict[str, Any]] = get_nearby_polling_booths(lat, lng)
    if result:
        return jsonify(success_response(data=result)), 200
    return jsonify(error_response("Could not find polling booth", 500)), 500
