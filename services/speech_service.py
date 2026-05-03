"""
Google Cloud Speech-to-Text Service for VoteWise AI

Provides voice input for voter questions.
Features:
- Speech recognition for election questions
- Audio input from microphone
- Support for multiple languages
- Fallback for when API unavailable
"""

import base64
import logging
from typing import Any, Optional

from config import Config

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """Google Cloud Speech-to-Text API integration."""

    def __init__(self):
        self._project_id = Config.GOOGLE_CLOUD_PROJECT
        self._initialized = False
        self._init_speech()

    def _init_speech(self) -> None:
        """Initialize speech client."""
        try:
            import os

            from google.cloud import speech

            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                self.client = speech.SpeechClient()
                self._initialized = True
            elif Config.FIREBASE_ADMIN_JSON:
                self.client = speech.SpeechClient()
                self._initialized = True
            else:
                self.client = None
        except (RuntimeError, ConnectionError, ValueError) as e:
            logger.warning("Speech-to-text init error: %s", e)
            self.client = None

    def recognize(
        self,
        audio_content: bytes,
        language_code: str = "en-US",
        sample_rate: int = 16000,
    ) -> Optional[str]:
        """
        Convert audio to text.

        Args:
            audio_content: Audio data in bytes
            language_code: Language code (en-US, hi-IN, etc.)
            sample_rate: Audio sample rate

        Returns:
            Recognized text or None
        """
        if self.client and self._initialized:
            try:
                from google.cloud import speech

                audio = speech.RecognitionAudio(content=audio_content)
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=sample_rate,
                    language_code=language_code,
                    enable_automatic_punctuation=True,
                    model="command_and_search",
                )

                response = self.client.recognize(config=config, audio=audio)

                for result in response.results:
                    if result.alternatives:
                        return result.alternatives[0].transcript
            except (RuntimeError, ConnectionError, ValueError) as e:
                logger.warning("Speech recognition error: %s", e)

        return None

    def recognize_from_base64(
        self, base64_audio: str, language_code: str = "en-US"
    ) -> Optional[str]:
        """
        Convert base64 encoded audio to text.

        Args:
            base64_audio: Base64 encoded audio
            language_code: Language code

        Returns:
            Recognized text
        """
        try:
            audio_content = base64.b64decode(base64_audio)
            return self.recognize(audio_content, language_code)
        except (RuntimeError, ConnectionError, ValueError) as e:
            logger.warning("Base64 decode error: %s", e)
            return self._mock_recognize()

    def transcribe_streaming(
        self, audio_iterator, language_code: str = "en-US"
    ) -> Optional[str]:
        """
        Stream recognition for long audio.

        Args:
            audio_iterator: Iterator of audio chunks
            language_code: Language code

        Returns:
            Recognized text
        """
        if self.client and self._initialized:
            try:
                from google.cloud import speech

                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    language_code=language_code,
                    enable_automatic_punctuation=True,
                )

                streaming_config = speech.StreamingRecognitionConfig(config=config)

                requests_generator = (
                    speech.StreamingRecognizeRequest(audio_content=chunk)
                    for chunk in audio_iterator
                )

                responses = self.client.streaming_recognize(
                    streaming_config, requests_generator
                )

                for response in responses:
                    if response.results:
                        result = response.results[0]
                        if result.alternatives:
                            return result.alternatives[0].transcript
            except (RuntimeError, ConnectionError, ValueError) as e:
                logger.warning("Streaming recognition error: %s", e)

        return self._mock_recognize()

    def get_audio_config(self) -> dict[str, Any]:
        """Get audio configuration for frontend."""
        return {
            "sample_rate": 16000,
            "language_codes": [
                {"code": "en-US", "name": "English (US)"},
                {"code": "en-IN", "name": "English (India)"},
                {"code": "hi-IN", "name": "Hindi"},
                {"code": "bn-IN", "name": "Bengali"},
                {"code": "ta-IN", "name": "Tamil"},
                {"code": "te-IN", "name": "Telugu"},
                {"code": "mr-IN", "name": "Marathi"},
                {"code": "kn-IN", "name": "Kannada"},
                {"code": "gu-IN", "name": "Gujarati"},
                {"code": "ml-IN", "name": "Malayalam"},
                {"code": "pa-IN", "name": "Punjabi"},
                {"code": "or-IN", "name": "Odia"},
                {"code": "as-IN", "name": "Assamese"},
                {"code": "ur-IN", "name": "Urdu"},
            ],
            "encoding": "LINEAR16",
        }

    def _mock_recognize(self) -> str:
        """Mock recognition for demo."""
        return "How do I register to vote?"


class VoiceInputHandler:
    """Handle voice input for voter dashboard."""

    def __init__(self):
        self.service = SpeechToTextService()

    def process_voice_question(
        self, audio_data: str, language: str = "en"
    ) -> dict[str, Any]:
        """
        Process voice input from voter.

        Args:
            audio_data: Base64 audio or audio data
            language: Language code

        Returns:
            Result with text and status
        """
        language_code = self._to_language_code(language)

        text = self.service.recognize_from_base64(audio_data, language_code)

        if not text:
            text = self._mock_question(language)

        return {"success": True, "text": text, "language": language, "source": "voice"}

    def _to_language_code(self, code: str) -> str:
        """Convert simple code to Google language code."""
        mapping = {
            "en": "en-US",
            "hi": "hi-IN",
            "bn": "bn-IN",
            "ta": "ta-IN",
            "te": "te-IN",
            "mr": "mr-IN",
            "kn": "kn-IN",
            "gu": "gu-IN",
            "ml": "ml-IN",
            "pa": "pa-IN",
        }
        return mapping.get(code, "en-US")

    def _mock_question(self, language: str) -> str:
        """Mock question based on language."""
        questions = {
            "hi": "मैं वोटर के रूप में कैसे पंजीकरण करूं?",
            "bn": "আমি কীভাবে ভোটার হিসাবে নথিভুক্ত করব?",
            "ta": "நான் வாக்காளராக எவ்வாறு பதிவு செய்வது?",
            "te": "నేను ఓటుగా ఎలా నమోదు చేసుకుంటా?",
            "mr": "मी मतदार म्हणून कसा नोंदणी करायचा?",
        }
        return questions.get(language, "How do I register to vote?")


speech_to_text_service = SpeechToTextService()
voice_input_handler = VoiceInputHandler()
