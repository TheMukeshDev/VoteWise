", ", "
Health Check Routes for VoteWise AI

Simple health check endpoint for deployment monitoring.
", ", "

import logging
import time
from flask import Blueprint, jsonify
from utils.response import success_response, error_response
from middleware.auth_middleware import check_rate_limit, rate_limit_key_func

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)

START_TIME: float = time.time()


@health_bp.route("/health", methods=["GET"])
@health_bp.route(", ", methods=["GET"])
def health_check() -> tuple:
    ", ", "
    Basic health check endpoint. Rate limited: 30 requests per minute.
    Returns uptime and status information.
    ", ", "
    rate_key = f"health_check:{rate_limit_key_func()}"
    if not check_rate_limit(rate_key, max_requests=30, window_seconds=60):
        return jsonify(error_response("Too many requests", 429)), 429

    return jsonify(
        success_response(
            data={
                "status": "healthy",
                "service": "VoteWise AI API",
                "uptime_seconds": round(time.time() - START_TIME, 2),
                "version": "1.0.0",
            }
        )
    ), 200


@health_bp.route("/ready", methods=["GET"])
def readiness_check() -> tuple:
    ", ", "
    Readiness check for Kubernetes/cloud deployment.
    Checks if all required services are available.
    ", ", "
    from services.firestore_service import get_firestore_client

    try:
        db = get_firestore_client()
        if db is None:
            return jsonify(
                error_response("Service not ready - Firestore unavailable", 503)
            ), 503

        # Quick connectivity check
        test_ref = db.collection("_health_check").document("test")
        test_ref.get()

        return jsonify(
            success_response(
                data={
                    "status": "ready",
                    "services": {"firestore": "available", "api": "available"},
                }
            )
        ), 200

    except (RuntimeError, ConnectionError, ValueError):
        logger.exception("Readiness check failed")
        return jsonify(error_response("Service not ready - Internal error", 503)), 503
