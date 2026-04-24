"""
Firestore Health Check Service for VoteWise AI
"""

import firebase_admin
from firebase_admin import firestore


class FirestoreHealthCheck:
    """Check Firestore connectivity."""

    @staticmethod
    def check_connection():
        """Check if Firestore is connected."""
        try:
            db = firestore.client()
            if db:
                doc = db.collection("_health_check").document("test").get()
                return {
                    "connected": True,
                    "message": "Firestore is connected and working",
                }
            return {"connected": False, "message": "Firestore client not available"}
        except Exception as e:
            return {
                "connected": False,
                "message": f"Firestore connection failed: {str(e)}",
            }

    @staticmethod
    def get_collections():
        """Get list of collections in Firestore."""
        try:
            db = firestore.client()
            if db:
                collections = db.collections()
                return [col.id for col in collections]
            return []
        except Exception:
            return []


firestore_health = FirestoreHealthCheck()
