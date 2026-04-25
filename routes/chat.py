from flask import Blueprint, request, jsonify, current_app
from utils.response import error_response
from config import Config
from google import genai
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)

# Initialize Gemini client
client = None
try:
    api_key = Config.GEMINI_API_KEY
    if api_key:
        client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialized")
except Exception as e:
    logger.warning(f"Failed to initialize Gemini client: {e}")


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    AI Chat endpoint with Gemini integration.

    Expected JSON: {"message": "How do I register to vote?", "user_prefs": {}}
    Returns: {"intro": "", "steps": [], "tips": [], "actions": []}
    """
    data = request.get_json() or {}
    message = data.get("message", "")
    user_prefs = data.get("user_prefs", {})

    if not message:
        return jsonify(error_response("Message is required", 400)), 400

    if len(message) > 1000:
        return jsonify(
            error_response("Message too long. Maximum 1000 characters.", 400)
        ), 400

    try:
        result = _generate_ai_response(message, user_prefs)
        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Chat error: {e}")
        return jsonify(
            {
                "success": True,
                "intro": "I'm here to help with your election questions!",
                "steps": [
                    "Visit the Election Commission website",
                    "Check your voter ID status",
                    "Locate your polling booth",
                ],
                "tips": ["Always verify from official sources"],
                "actions": [],
            }
        ), 200


def _detect_intent(message: str) -> str:
    """Detect user intent from message keywords."""
    message_lower = message.lower()

    intent_keywords = {
        "register": ["register", "voter id", "epic", "enroll"],
        "document": ["document", "id proof", "aadhaar", "passport", "license"],
        "booth": ["booth", "polling station", "location", "find"],
    }

    for intent, keywords in intent_keywords.items():
        if any(kw in message_lower for kw in keywords):
            return intent
    return "default"


def _generate_ai_response(message: str, user_prefs: dict) -> dict:
    """Generate AI response using Gemini or fallback to rule-based responses."""
    intent = _detect_intent(message)

    if intent and intent != "default":
        return _get_fallback_response(intent)

    if client:
        return _call_gemini_api(message, user_prefs)

    return _get_fallback_response(message)


def _get_fallback_response(message):
    """Fallback responses for unknown messages"""
    message_lower = message.lower()

    responses = {
        "register": {
            "intro": "To register as a voter:",
            "steps": [
                "Visit the Election Commission website",
                "Fill the online form with your details",
                "Submit ID and address proof",
                "Get your voter ID (EPIC)",
            ],
            "tips": ["Register at least 30 days before elections"],
            "actions": ["Learn more about registration"],
        },
        "document": {
            "intro": "Accepted ID documents:",
            "steps": [
                "Voter ID (EPIC) - Recommended",
                "Aadhaar Card",
                "Passport",
                "Driving License",
            ],
            "tips": ["Carry any one photo ID to the polling station"],
            "actions": ["View full document list"],
        },
        "booth": {
            "intro": "Find your polling booth:",
            "steps": [
                "Check your voter slip",
                "Visit Election Commission website",
                "Enter your EPIC number or name",
                "Note the location and directions",
            ],
            "tips": ["Visit a day before to familiarize yourself"],
            "actions": ["Find my polling booth"],
        },
    }

    for key, resp in responses.items():
        if key in message_lower:
            resp["success"] = True
            return resp

    default_resp = {
        "intro": "I'm here to help with election education!",
        "steps": [
            "Learn about voter registration",
            "Find your polling booth",
            "Understand required documents",
            "Track election timeline",
        ],
        "tips": ["Always verify from official sources"],
        "actions": ["Ask me about registration", "Ask about documents"],
    }
    default_resp["success"] = True
    return default_resp


def _call_gemini_api(message: str, user_prefs: dict) -> dict:
    """Call Gemini API for AI response."""
    if not client:
        return _get_fallback_response(message)

    try:
        prompt = f"""You are VoteWise AI, a neutral, helpful civic assistant for election education.
Keep responses brief, friendly, and informative.
Respond in this JSON format only:
{{"intro": "Brief intro", "steps": ["step1", "step2"], "tips": ["tip1"], "actions": ["action1"]}}

User: {message}
Context: {user_prefs}
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        text = response.candidates[0].content.parts[0].text
        text = text.strip("```json").strip("```").strip()
        import json

        result = json.loads(text)
        result["success"] = True
        return result
    except Exception:
        return _get_fallback_response(message)


@chat_bp.route("/health", methods=["GET"])
def health():
    """Health check for chat service"""
    return jsonify(
        {"status": "healthy", "ai_available": client is not None, "rate_limited": False}
    ), 200
