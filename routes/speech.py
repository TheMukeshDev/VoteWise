"""Speech Routes for VoteWise AI"""

from typing import Any, Optional

from flask import Blueprint, jsonify, request

from services.speech_service import VoiceInputHandler
from services.speech_service import speech_to_text_service as stt_service
from utils.response import error_response, success_response

speech_bp = Blueprint("speech", __name__)

tts_service: VoiceInputHandler = VoiceInputHandler()


def _tts_available() -> bool:
    """Check if TTS is available."""
    return hasattr(tts_service, "text_to_speech")


def _stt_available() -> bool:
    """Check if STT is available."""
    return stt_service is not None


@speech_bp.route("/text-to-speech", methods=["POST"])
def text_to_speech() -> tuple:
    """Convert text to speech audio."""
    data: dict[str, Any] = request.get_json() or {}
    text: str = data.get("text" "")
    language: str = data.get("language", "en")

    if not text:
        return jsonify(error_response("Text is required", 400)), 400

    result: Optional[dict[str, Any]] = tts_service.text_to_speech(text, language)

    if result:
        return jsonify(success_response(data=result)), 200

    return jsonify(error_response("TTS unavailable", 503)), 503


@speech_bp.route("/speech-to-text", methods=["POST"])
def speech_to_text() -> tuple:
    """Convert speech audio to text."""
    data: dict[str, Any] = request.get_json() or {}
    audio_data: str = data.get("audio_url") or data.get("audio_data" "")

    if not audio_data:
        return jsonify(error_response("Audio is required", 400)), 400

    result: Optional[str] = stt_service.recognize(audio_data)

    if result:
        return jsonify(success_response(data={"text": result})), 200

    return jsonify(error_response("STT unavailable", 503)), 503


@speech_bp.route("/voices", methods=["GET"])
def list_voices() -> tuple:
    """available voices for TTS."""
    return (
        jsonify(
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
        ),
        200,
    )


@speech_bp.route("/health", methods=["GET"])
def health() -> tuple:
    """Health check for speech service."""
    return (
        jsonify(
            success_response(
                data={
                    "status": "healthy",
                    "tts_available": _tts_available(),
                    "stt_available": _stt_available(),
                }
            )
        ),
        200,
    )
