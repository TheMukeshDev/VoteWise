"""
Google Cloud Text-to-Speech Service for VoteWise AI

Provides spoken responses for voters.
Features:
- Convert election guidance to speech
- Support for multiple languages
- Accessibility audio playback
- MP3 audio output
"""

import logging
import base64
from typing import Optional, Dict, Any, List
from config import Config

logger = logging.getLogger(__name__)


class TextToSpeechService:
    """Google Cloud Text-to-Speech API integration."""

    VOICE_PROFILES = {
        "en": {"language_code": "en-US", "name": "en-US-Neural2-J"},
        "hi": {"language_code": "hi-IN", "name": "hi-IN-Neural2-D"},
        "bn": {"language_code": "bn-IN", "name": "bn-IN-Standard-A"},
        "ta": {"language_code": "ta-IN", "name": "ta-IN-Standard-A"},
        "te": {"language_code": "te-IN", "name": "te-IN-Standard-A"},
        "mr": {"language_code": "mr-IN", "name": "mr-IN-Standard-A"},
        "kn": {"language_code": "kn-IN", "name": "kn-IN-Standard-A"},
        "gu": {"language_code": "gu-IN", "name": "gu-IN-Standard-A"},
        "ml": {"language_code": "ml-IN", "name": "ml-IN-Standard-A"},
        "pa": {"language_code": "pa-IN", "name": "pa-IN-Standard-A"},
    }

    def __init__(self):
        self.api_key = Config.GOOGLE_CLOUD_PROJECT
        self._initialized = False
        self._init_tts()

    def _init_tts(self):
        """Initialize TTS client."""
        try:
            from google.cloud import texttospeech
            import os

            if Config.FIREBASE_CREDENTIALS_PATH and os.path.exists(
                Config.FIREBASE_CREDENTIALS_PATH
            ):
                self.client = texttospeech.TextToSpeechClient()
                self._initialized = True
            else:
                self.client = None
        except Exception as e:
            logger.warning(f"Text-to-speech init error: {e}")
            self.client = None

    def synthesize(
        self,
        text: str,
        language: str = "en",
        voice_gender: str = "neutral",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        audio_format: str = "mp3",
    ) -> Optional[Dict[str, Any]]:
        """
        Convert text to speech.

        Args:
            text: Text to synthesize
            language: Language code (en, hi, etc.)
            voice_gender: MALE, FEMALE, or NEUTRAL
            speaking_rate: Speed of speech (0.25 to 4.0)
            pitch: Pitch adjustment (-20.0 to 20.0)
            audio_format: MP3, LINEAR16, or OGG_OPUS

        Returns:
            Audio data and metadata
        """
        if self.client and self._initialized:
            try:
                from google.cloud import texttospeech

                voice = self._get_voice_config(language, voice_gender)
                audio_config = self._get_audio_config(
                    audio_format, speaking_rate, pitch
                )

                synthesis_input = texttospeech.SynthesisInput(text=text)

                response = self.client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                audio_content = response.audio_content
                return {
                    "audio_content": base64.b64encode(audio_content).decode("utf-8"),
                    "audio_format": audio_format,
                    "language": language,
                    "text": text,
                }
            except Exception as e:
                logger.warning(f"Synthesis error: {e}")

        return self._mock_synthesize(text, language, audio_format)

    def synthesize_ssml(
        self, ssml: str, language: str = "en", audio_format: str = "mp3"
    ) -> Optional[Dict[str, Any]]:
        """
        Synthesize SSML for advanced control.

        Args:
            ssml: SSML content
            language: Language code
            audio_format: Audio format

        Returns:
            Audio data
        """
        if self.client and self._initialized:
            try:
                from google.cloud import texttospeech

                voice = self._get_voice_config(language)
                audio_config = self._get_audio_config(audio_format)

                synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

                response = self.client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                audio_content = response.audio_content
                return {
                    "audio_content": base64.b64encode(audio_content).decode("utf-8"),
                    "audio_format": audio_format,
                    "language": language,
                }
            except Exception as e:
                logger.warning(f"SSML synthesis error: {e}")

        return None

    def speak_election_steps(
        self, steps: List[Dict[str, Any]], language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Convert election steps to speech.

        Args:
            steps: List of election steps
            language: Language code

        Returns:
            Audio data
        """
        text = self._format_steps_for_speech(steps)
        return self.synthesize(text, language)

    def speak_faq_answer(
        self, question: str, answer: str, language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Speak FAQ question and answer.

        Args:
            question: FAQ question
            answer: FAQ answer
            language: Language code

        Returns:
            Audio data
        """
        text = f"Question: {question}. Answer: {answer}"
        return self.synthesize(text, language)

    def speak_timeline_event(
        self, event: Dict[str, Any], language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Speak election timeline event.

        Args:
            event: Timeline event data
            language: Language code

        Returns:
            Audio data
        """
        text = f"Important date: {event.get('title', 'Election Event')}"
        if event.get("date"):
            text += f" on {event.get('date')}"
        if event.get("description"):
            text += f". {event.get('description')}"

        return self.synthesize(text, language)

    def _get_voice_config(self, language: str, gender: str = "neutral") -> Dict:
        """Get voice configuration."""
        from google.cloud import texttospeech

        voice_profile = self.VOICE_PROFILES.get(language, self.VOICE_PROFILES["en"])

        gender_map = {
            "male": texttospeech.VoiceSelectionParams.MALE,
            "female": texttospeech.VoiceSelectionParams.FEMALE,
            "neutral": texttospeech.VoiceSelectionParams.NEUTRAL,
        }

        return texttospeech.VoiceSelectionParams(
            language_code=voice_profile["language_code"],
            name=voice_profile["name"],
            ssml_gender=gender_map.get(
                gender, texttospeech.VoiceSelectionParams.NEUTRAL
            ),
        )

    def _get_audio_config(
        self, audio_format: str, speaking_rate: float = 1.0, pitch: float = 0.0
    ) -> Dict:
        """Get audio configuration."""
        from google.cloud import texttospeech

        encoding_map = {
            "mp3": texttospeech.AudioConfig.MP3,
            "linear16": texttospeech.AudioConfig.LINEAR16,
            "ogg_opus": texttospeech.AudioConfig.OGG_OPUS,
        }

        return texttospeech.AudioConfig(
            audio_encoding=encoding_map.get(audio_format, texttospeech.AudioConfig.MP3),
            speaking_rate=speaking_rate,
            pitch=pitch,
        )

    def _format_steps_for_speech(self, steps: List[Dict]) -> str:
        """Format election steps for speech."""
        text_parts = []

        for i, step in enumerate(steps, 1):
            if isinstance(step, dict):
                step_text = step.get("title") or step.get("description", "")
            else:
                step_text = str(step)

            text_parts.append(f"Step {i}: {step_text}")

        return ". ".join(text_parts)

    def _mock_synthesize(
        self, text: str, language: str, audio_format: str
    ) -> Dict[str, Any]:
        """Mock synthesis when API unavailable."""
        return {
            "audio_content": "",
            "audio_format": audio_format,
            "language": language,
            "text": text,
            "mock": True,
        }

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available voice profiles."""
        if self.client and self._initialized:
            try:
                from google.cloud import texttospeech

                response = self.client.list_voices()

                voices = []
                for voice in response.voices:
                    if voice.language_codes:
                        voices.append(
                            {
                                "name": voice.name,
                                "language_codes": voice.language_codes,
                                "ssml_gender": texttospeech.VoiceSelectionParams.SsmlGender(
                                    voice.ssml_gender
                                ).name,
                                "natural_sample_rate_hertz": voice.natural_sample_rate_hertz,
                            }
                        )

                return voices
            except Exception:
                pass

        return list(self.VOICE_PROFILES.values())


class AudioGuidancePlayer:
    """Audio player for election guidance."""

    def __init__(self):
        self.service = TextToSpeechService()

    def play_election_info(
        self, info_type: str, data: Any, language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate audio for election information.

        Args:
            info_type: Type (faq, steps, timeline)
            data: Data to speak
            language: Language code

        Returns:
            Audio playback data
        """
        if info_type == "faq":
            return self.service.speak_faq_answer(
                data.get("question", ""), data.get("answer", ""), language
            )
        elif info_type == "steps":
            return self.service.speak_election_steps(data, language)
        elif info_type == "timeline":
            return self.service.speak_timeline_event(data, language)

        return self.service.synthesize(str(data), language)

    def get_playback_url(self, audio_content: str, audio_format: str = "mp3") -> str:
        """
        Get audio playback URL.

        Args:
            audio_content: Base64 audio
            audio_format: Format

        Returns:
            Data URL for playback
        """
        mime_types = {
            "mp3": "audio/mp3",
            "linear16": "audio/wav",
            "ogg_opus": "audio/ogg",
        }

        mime = mime_types.get(audio_format, "audio/mp3")
        return f"data:{mime};base64,{audio_content}"


text_to_speech_service = TextToSpeechService()
audio_guidance_player = AudioGuidancePlayer()
