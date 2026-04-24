from flask import Blueprint, request, jsonify
from services.speech_service import (
    speech_to_text_service as stt_service,
    VoiceInputHandler,
)
from utils.response import success_response, error_response

speech_bp = Blueprint("speech", __name__)

tts_service = VoiceInputHandler()


def _tts_available() -> bool:
    """Check if TTS is available."""
    return hasattr(tts_service, "text_to_speech")


def _stt_available() -> bool:
    """Check if STT is available."""
    return stt_service is not None


@speech_bp.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    """Convert text to speech audio."""
    try:
        data = request.get_json() or {}
        text = data.get("text", "")
        language = data.get("language", "en")

        if not text:
            return jsonify(error_response("Text is required", 400)), 400

        result = tts_service.text_to_speech(text, language)

        if result:
            return jsonify(success_response(data=result)), 200

        return jsonify(error_response("TTS unavailable", 503)), 503

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@speech_bp.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    """Convert speech audio to text."""
    try:
        data = request.get_json() or {}
        audio_data = data.get("audio_url") or data.get("audio_data", "")

        if not audio_data:
            return jsonify(error_response("Audio is required", 400)), 400

        result = stt_service.recognize(audio_data)

        if result:
            return jsonify(success_response(data={"text": result})), 200

        return jsonify(error_response("STT unavailable", 503)), 503

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@speech_bp.route("/voices", methods=["GET"])
def list_voices():
    """List available voices for TTS."""
    try:
        return jsonify(
            success_response(
                data={
                    "voices": [
                        {"code": "en-US", "name": "English (US)"},
                        {"code": "hi-IN", "name": "Hindi"},
                        {"code": "kn-IN", "name": "Kannada"},
                        {"code": "ta-IN", "name": "Tamil"},
                        {"code": "te-IN", "name": "Telugu"},
                    ]
                }
            )
        ), 200

    except Exception as e:
        return jsonify(error_response(str(e), 500)), 500


@speech_bp.route("/health", methods=["GET"])
def health():
    """Health check for speech service."""
    return jsonify(
        {
            "status": "healthy",
            "tts_available": _tts_available(),
            "stt_available": _stt_available(),
        }
    ), 200
