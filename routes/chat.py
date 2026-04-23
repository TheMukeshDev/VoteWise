from flask import Blueprint, request, jsonify
from utils.response_helper import format_chat_response
from config import Config
from google import genai
import json

chat_bp = Blueprint("chat", __name__)

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


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")
    user_prefs = data.get("user_prefs", {})

    if not message:
        return jsonify({"error": "Message is required"}), 400

    if client:
        try:
            prompt = f"""
You are VoteWise AI, a neutral, helpful civic assistant. 
Explain the following query about the election process.
You MUST respond strictly in the following JSON format:
{{
  "intro": "A short introductory explanation",
  "steps": ["Step 1 description", "Step 2 description", ...],
  "tips": ["Useful tip 1", "Useful tip 2", ...],
  "actions": ["Find polling booth", "Set reminder", "Show official link"]
}}
Do NOT include any markdown code blocks, just the raw JSON string.

User Query: {message}
User Preferences: {user_prefs}
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            # Parse the JSON response
            try:
                response_data = json.loads(response.text)
                formatted_response = format_chat_response(
                    intro=response_data.get("intro", "Here is what you need to know."),
                    steps=response_data.get("steps", []),
                    tips=response_data.get("tips", []),
                    actions=response_data.get("actions", []),
                )
            except json.JSONDecodeError:
                # Fallback if LLM didn't return perfect JSON
                formatted_response = format_chat_response(
                    intro=response.text,
                    steps=["Please rephrase for a more structured answer."],
                    actions=["Ask again"],
                )
        except Exception as e:
            formatted_response = format_chat_response(
                intro="I'm having trouble connecting to my AI brain right now.",
                steps=[],
                tips=[f"Error: {str(e)}"],
                actions=[],
            )
    else:
        # Mock structured response
        formatted_response = format_chat_response(
            intro="Here is a basic overview of the election process.",
            steps=[
                "Register to vote.",
                "Verify your name on the list.",
                "Go to the polling booth on election day.",
                "Cast your vote.",
            ],
            tips=["Make sure you carry a valid ID."],
            actions=["Find polling booth", "Set reminder"],
        )

    return jsonify(formatted_response)
