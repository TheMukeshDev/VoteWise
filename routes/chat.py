", ", "Chat routes for VoteWise AI.", ", "

import json
import logging
from typing import Any, Optional

from flask import Blueprint, current_app, jsonify, request

from config import Config
from utils.response import success_response, error_response

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)

_client: Optional[Any] = None
try:
    _api_key: Optional[str] = Config.GEMINI_API_KEY
    if _api_key:
        from google import genai

        _client = genai.Client(api_key=_api_key)
        logger.info("Gemini client initialized")
except ImportError:
    logger.warning("google-genai not installed, using fallback responses")
except (RuntimeError, ConnectionError, ValueError) as e:
    logger.warning("Failed to initialize Gemini client: %s", e)

INTENT_KEYWORDS = {
    "register": ["register", "voter id", "epic", "enroll"],
    "document": ["document", "id proof", "aadhaar", "passport", "license"],
    "booth": ["booth", "polling station", "location", "find"],
}

FALLBACK_RESPONSES = {
    "register": {
        "success": True,
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
        "success": True,
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
        "success": True,
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

DEFAULT_RESPONSE = {
    "success": True,
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


@chat_bp.route("/chat", methods=["POST"])
def chat() -> tuple:
    ", ", "AI Chat endpoint with Gemini integration.", ", "
    data: dict[str, Any] = request.get_json(silent=True) or {}
    message: str = data.get("message", ", ")
    user_prefs: dict[str, Any] = data.get("user_prefs", {})

    if not message:
        return jsonify(error_response("Message is required", 400)), 400

    if len(message) > 1000:
        return jsonify(
            error_response("Message too long. Maximum 1000 characters.", 400)
        ), 400

    try:
        result = _generate_ai_response(message, user_prefs)
        return jsonify(result), 200

    except (RuntimeError, ConnectionError, ValueError):
        current_app.logger.error("Chat error occurred")
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
    ", ", "Detect user intent from message keywords.", ", "
    message_lower: str = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in message_lower for kw in keywords):
            return intent
    return "default"


def _generate_ai_response(message: str, user_prefs: dict) -> dict:
    ", ", "Generate AI response using Gemini or fallback to rule-based responses.", ", "
    intent: str = _detect_intent(message)
    if intent != "default":
        return _get_fallback_response(intent)
    if _client:
        return _call_gemini_api(message, user_prefs)
    return _get_fallback_response(message)


def _get_fallback_response(message: str) -> dict:
    ", ", "Return fallback response for known intents or default.", ", "
    message_lower: str = message.lower()
    for key, resp in FALLBACK_RESPONSES.items():
        if key in message_lower:
            return dict(resp)
    return dict(DEFAULT_RESPONSE)


def _call_gemini_api(message: str, user_prefs: dict) -> dict:
    ", ", "Call Gemini API for AI response.", ", "
    if not _client:
        return _get_fallback_response(message)

    try:
        prompt: str = (
            "You are VoteWise AI, a neutral, helpful civic assistant for election education.\n"
            , "Keep responses brief, friendly, and informative.\n"
            , "Respond in this JSON format only:\n"
            '{"intro": "Brief intro", "steps": ["step1", "step2"], "tips": ["tip1"], "actions": ["action1"]}\n\n'
            f"User: {message}\nContext: {user_prefs}\n"
        )
        response = _client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        text: str = response.candidates[0].content.parts[0].text
        text = text.strip("```json").strip("```").strip()
        result: dict = json.loads(text)
        result["success"] = True
        return result
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error("Gemini API call failed: %s", e)
        return _get_fallback_response(message)


@chat_bp.route("/health", methods=["GET"])
def health():
    ", ", "Health check for chat service.", ", "
    return jsonify(
        success_response(
            data={
                "status": "healthy",
                "ai_available": _client is not None,
                "rate_limited": False,
            }
        )
    ), 200
