from flask import Blueprint, request, jsonify, current_app
from utils.response_helper import format_chat_response
from config import Config
from google import genai
import json
import time
from functools import wraps

chat_bp = Blueprint("chat", __name__)

# Rate limiting storage (simple in-memory for demo)
rate_limit_store = {}

# Initialize Gemini client
try:
    api_key = Config.GEMINI_API_KEY
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = None
except Exception as e:
    print(f"Warning: Failed to initialize Gemini client: {e}")
    client = None


def rate_limit(max_requests=30, window_seconds=60):
    """Simple rate limiting decorator"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            ip = request.remote_addr or "unknown"
            current_time = time.time()

            # Clean old entries
            if ip in rate_limit_store:
                rate_limit_store[ip] = [
                    t for t in rate_limit_store[ip] if current_time - t < window_seconds
                ]
            else:
                rate_limit_store[ip] = []

            # Check limit
            if len(rate_limit_store[ip]) >= max_requests:
                return jsonify(
                    {
                        "success": False,
                        "error": "Too many requests. Please try again later.",
                        "code": "RATE_LIMITED",
                    }
                ), 429

            # Add this request
            rate_limit_store[ip].append(current_time)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@chat_bp.route("/chat", methods=["POST"])
@rate_limit(max_requests=30, window_seconds=60)
def chat():
    """AI Chat endpoint with rate limiting"""
    try:
        data = request.json or {}
        message = data.get("message", "")
        user_prefs = data.get("user_prefs", {})

        # Validate input
        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400

        if len(message) > 1000:
            return jsonify(
                {
                    "success": False,
                    "error": "Message too long. Maximum 1000 characters.",
                }
            ), 400

        # Generate AI response
        if client:
            try:
                prompt = f"""
You are VoteWise AI, a neutral, helpful civic assistant for election education.
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

                # Parse response
                try:
                    response_data = json.loads(response.text)
                    result = {
                        "success": True,
                        "intro": response_data.get(
                            "intro", "Here's what you need to know."
                        ),
                        "steps": response_data.get("steps", []),
                        "tips": response_data.get("tips", []),
                        "actions": response_data.get("actions", []),
                    }
                except:
                    # Fallback
                    result = {
                        "success": True,
                        "intro": response.text[:200]
                        if response.text
                        else "I'm here to help!",
                        "steps": [
                            "Visit the Election Commission website for more details"
                        ],
                        "tips": ["Always verify information from official sources"],
                        "actions": [],
                    }
            except Exception as e:
                current_app.logger.error(f"AI Error: {e}")
                result = {
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
        else:
            # Fallback responses when no API
            result = _get_fallback_response(message)

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Chat error: {e}")
        return jsonify(
            {"success": False, "error": "Something went wrong. Please try again."}
        ), 500


def _get_fallback_response(message):
    """Fallback responses for demo"""
    message = message.lower()

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
        "default": {
            "intro": "I'm here to help with election education!",
            "steps": [
                "Learn about voter registration",
                "Find your polling booth",
                "Understand required documents",
                "Track election timeline",
            ],
            "tips": ["Always verify from official sources"],
            "actions": ["Ask me about registration", "Ask about documents"],
        },
    }

    for key, resp in responses.items():
        if key in message:
            resp["success"] = True
            return resp

    responses["default"]["success"] = True
    return responses["default"]


@chat_bp.route("/health", methods=["GET"])
def health():
    """Health check for chat service"""
    return jsonify(
        {"status": "healthy", "ai_available": client is not None, "rate_limited": False}
    ), 200
