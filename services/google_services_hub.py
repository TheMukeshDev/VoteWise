"""
Google Services Hub for VoteWise AI

Central initialization for all Google Cloud services.
Provides unified access to:
- Firestore
- Firebase Auth
- Maps
- Calendar
- Translate
- Speech-to-Text
- Text-to-Speech
"""

from typing import Optional, Dict, Any

from services.auth_service import firebase_auth_service, user_profile_service
from services.maps_service import maps_service
from services.calendar_service import calendar_service, local_calendar_service
from services.translate_service import translate_service, election_translator
from services.speech_service import speech_to_text_service, voice_input_handler
from services.tts_service import text_to_speech_service, audio_guidance_player
from services.data_access_layer import firestore_db


class GoogleServicesHub:
    """Central hub for all Google services."""

    def __init__(self):
        self.auth = firebase_auth_service
        self.profiles = user_profile_service
        self.maps = maps_service
        self.calendar = calendar_service
        self.calendar_local = local_calendar_service
        self.translate = translate_service
        self.translator = election_translator
        self.speech_to_text = speech_to_text_service
        self.voice = voice_input_handler
        self.tts = text_to_speech_service
        self.audio = audio_guidance_player
        self.db = firestore_db

    def verify_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token."""
        return self.auth.verify_id_token(id_token)

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile."""
        return self.profiles.get_user_profile(user_id)

    def find_polling_booth(self, lat: float, lng: float) -> Dict[str, Any]:
        """Find nearest polling booth."""
        return self.maps.find_polling_booth(lat, lng)

    def find_multiple_booths(
        self, lat: float, lng: float, max_results: int = 5
    ) -> list:
        """Find multiple polling booths."""
        return self.maps.find_multiple_booths(lat, lng, max_results=max_results)

    def create_calendar_reminder(
        self, title: str, date: str, reminder_type: str = "polling"
    ) -> Dict[str, Any]:
        """Create calendar reminder."""
        return self.calendar.create_election_reminder(
            title, date, reminder_type=reminder_type
        )

    def generate_ics(self, title: str, date: str) -> str:
        """Generate ICS file."""
        return self.calendar_local.generate_voting_calendar(title, date)

    def translate_content(
        self, text: str, target_language: str = "hi"
    ) -> Dict[str, Any]:
        """Translate content."""
        return self.translate.translate(text, target_language)

    def translate_faqs(self, faqs: list, language: str = "hi") -> list:
        """Translate FAQs."""
        return self.translator.translate_faqs(faqs, language)

    def get_supported_languages(self) -> list:
        """Get supported languages."""
        return self.translate.get_supported_languages()

    def get_voice_config(self) -> Dict[str, Any]:
        """Get voice input configuration."""
        return self.speech_to_text.get_audio_config()

    def get_available_voices(self) -> list:
        """Get available TTS voices."""
        return self.tts.get_available_voices()

    def synthesize_speech(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Synthesize speech."""
        return self.tts.synthesize(text, language)

    def speak_election_steps(self, steps: list, language: str = "en") -> Dict[str, Any]:
        """Speak election steps."""
        return self.tts.speak_election_steps(steps, language)

    def get_playback_url(self, audio_content: str, format: str = "mp3") -> str:
        """Get audio playback URL."""
        return self.audio.get_playback_url(audio_content, format)

    def get_health_status(self) -> Dict[str, bool]:
        """Get status of all services."""
        return {
            "firestore": self.db.db is not None,
            "firebase_auth": bool(self.auth._initialized),
            "maps": bool(self.maps.api_key),
            "calendar": bool(self.calendar.access_token),
            "translate": self.translate._initialized,
            "speech_to_text": self.speech_to_text._initialized,
            "text_to_speech": self.tts._initialized,
        }


google_services = GoogleServicesHub()
