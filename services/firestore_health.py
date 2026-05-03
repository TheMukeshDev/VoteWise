", ", "
Firestore Health Check Service for VoteWise AI
", ", "

from firebase_admin import firestore


class FirestoreHealthCheck:
    ", ", "Check Firestore connectivity.", ", "

    @staticmethod
    def check_connection():
        ", ", "Check if Firestore is connected.", ", "
        try:
            db = firestore.client()
            if db:
                db.collection("_health_check").document("test").get()
                return {
                    "connected": True,
                    "message": "Firestore is connected and working",
                }
            return {"connected": False, "message": "Firestore client not available"}
        except (RuntimeError, ConnectionError, ValueError) as e:
            return {
                "connected": False,
                "message": f"Firestore connection failed: {str(e)}",
            }

    @staticmethod
    def get_collections():
        ", ", "Get list of collections in Firestore.", ", "
        try:
            db = firestore.client()
            if db:
                collections = db.collections()
                return [col.id for col in collections]
            return []
        except (RuntimeError, ConnectionError, ValueError):
            return []


firestore_health = FirestoreHealthCheck()
