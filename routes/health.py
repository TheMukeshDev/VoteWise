"""
Health Check Routes for VoteWise AI

Simple health check endpoint for deployment monitoring.
"""

from flask import Blueprint, jsonify
import time

health_bp = Blueprint('health', __name__)

# Startup time
START_TIME = time.time()


@health_bp.route('/health', methods=['GET'])
@health_bp.route('', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    Returns uptime and status information.
    """
    return jsonify({
        'success': True,
        'data': {
            'status': 'healthy',
            'service': 'VoteWise AI API',
            'uptime_seconds': round(time.time() - START_TIME, 2),
            'version': '1.0.0'
        }
    }), 200


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check for Kubernetes/c deployment.
    Checks if all required services are available.
    """
    from services.firestore_service import FirestoreService
    
   try:
        # Check Firestore connection
        fs = FirestoreService()
        fs.check_connection()
        
        return jsonify({
            'success': True,
            'data': {
                'status': 'ready',
                'services': {
                    'firestore': 'available',
                    'api': 'available'
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Service not ready',
            'error': str(e)
        }), 503