", ", "Comprehensive tests for external Google/Firebase services to push coverage to 85%+.", ", "

import pytest
from unittest.mock import MagicMock, patch
import base64


class TestAuthServiceExtended:
    ", ", "Test FirebaseAuthService and UserProfileService.", ", "

    @patch("services.auth_service.auth.verify_id_token")
    def test_verify_token_invalid(self, mock_verify):
        from services.auth_service import FirebaseAuthService

        mock_verify.side_effect = ValueError("Invalid token")
        service = FirebaseAuthService()
        result = service.verify_id_token("bad_token")
        assert result is None

    @patch("services.auth_service.auth.verify_id_token")
    def test_verify_token_expired(self, mock_verify):
        from services.auth_service import FirebaseAuthService
        from firebase_admin import auth

        mock_verify.side_effect = auth.ExpiredIdTokenError("Token expired")
        service = FirebaseAuthService()
        result = service.verify_id_token("expired_token")
        assert result is None

    @patch("services.auth_service.auth.verify_id_token")
    def test_verify_token_success(self, mock_verify):
        from services.auth_service import FirebaseAuthService

        mock_verify.return_value = {"uid": "u1", "email": "a@b.com"}
        service = FirebaseAuthService()
        result = service.verify_id_token("valid_token")
        assert result["uid"] == "u1"

    @patch("services.auth_service.auth.create_custom_token")
    def test_create_custom_token_success(self, mock_create):
        from services.auth_service import FirebaseAuthService

        mock_create.return_value = b"custom_token_bytes"
        service = FirebaseAuthService()
        result = service.create_custom_token("u1")
        assert result == "custom_token_bytes"

    @patch("services.auth_service.auth.create_custom_token")
    def test_create_custom_token_string(self, mock_create):
        from services.auth_service import FirebaseAuthService

        mock_create.return_value = "custom_token_string"
        service = FirebaseAuthService()
        result = service.create_custom_token("u1")
        assert result == "custom_token_string"

    @patch("services.auth_service.auth.create_custom_token")
    def test_create_custom_token_with_claims(self, mock_create):
        from services.auth_service import FirebaseAuthService

        mock_create.return_value = b"token"
        service = FirebaseAuthService()
        result = service.create_custom_token("u1", {"role": "admin"})
        assert result is not None
        mock_create.assert_called_with("u1", {"role": "admin"})

    @patch("services.auth_service.auth.create_custom_token")
    def test_create_custom_token_failure(self, mock_create):
        from services.auth_service import FirebaseAuthService

        mock_create.side_effect = ValueError("Invalid UID")
        service = FirebaseAuthService()
        result = service.create_custom_token("bad_uid")
        assert result is None

    @patch("services.auth_service.auth.get_user")
    def test_get_user_not_found(self, mock_get):
        from services.auth_service import FirebaseAuthService
        from firebase_admin import auth

        mock_get.side_effect = auth.UserNotFoundError("Not found")
        service = FirebaseAuthService()
        result = service.get_user("missing")
        assert result is None

    @patch("services.auth_service.auth.get_user")
    def test_get_user_firebase_error(self, mock_get):
        from services.auth_service import FirebaseAuthService
        from firebase_admin import auth

        mock_get.side_effect = auth.FirebaseError("Error")
        service = FirebaseAuthService()
        result = service.get_user("u1")
        assert result is None

    @patch("services.auth_service.auth.create_user")
    def test_create_user_success(self, mock_create):
        from services.auth_service import FirebaseAuthService

        mock_user = MagicMock()
        mock_user.uid = "new_uid"
        mock_user.email = "new@example.com"
        mock_create.return_value = mock_user
        service = FirebaseAuthService()
        result = service.create_user("new@example.com", "password123", "New User")
        assert result["uid"] == "new_uid"

    @patch("services.auth_service.auth.create_user")
    def test_create_user_email_exists(self, mock_create):
        from services.auth_service import FirebaseAuthService
        from firebase_admin import auth

        mock_create.side_effect = auth.EmailAlreadyExistsError("Email exists")
        service = FirebaseAuthService()
        with pytest.raises(ValueError):
            service.create_user("existing@example.com", "password123")

    @patch("services.auth_service.auth.update_user")
    def test_update_user_success(self, mock_update):
        from services.auth_service import FirebaseAuthService

        mock_user = MagicMock()
        mock_user.uid = "u1"
        mock_user.email = "a@b.com"
        mock_update.return_value = mock_user
        service = FirebaseAuthService()
        result = service.update_user("u1", display_name="Updated")
        assert result is not None

    @patch("services.auth_service.auth.update_user")
    def test_update_user_failure(self, mock_update):
        from services.auth_service import FirebaseAuthService

        mock_update.side_effect = ValueError("Invalid")
        service = FirebaseAuthService()
        result = service.update_user("u1", display_name="Updated")
        assert result is None

    @patch("services.auth_service.auth.delete_user")
    def test_delete_user_success(self, mock_delete):
        from services.auth_service import FirebaseAuthService

        mock_delete.return_value = None
        service = FirebaseAuthService()
        assert service.delete_user("u1") is True

    @patch("services.auth_service.auth.delete_user")
    def test_delete_user_failure(self, mock_delete):
        from services.auth_service import FirebaseAuthService
        from firebase_admin import auth

        mock_delete.side_effect = auth.FirebaseError("Error")
        service = FirebaseAuthService()
        assert service.delete_user("u1") is False

    @patch("services.auth_service.auth.set_custom_user_claims")
    def test_set_claims_success(self, mock_set):
        from services.auth_service import FirebaseAuthService

        mock_set.return_value = None
        service = FirebaseAuthService()
        assert service.set_custom_user_claims("u1", {"role": "admin"}) is True

    @patch("services.auth_service.auth.set_custom_user_claims")
    def test_set_claims_failure(self, mock_set):
        from services.auth_service import FirebaseAuthService

        mock_set.side_effect = ValueError("Invalid")
        service = FirebaseAuthService()
        assert service.set_custom_user_claims("u1", {"role": "admin"}) is False

    @patch("services.auth_service.auth.get_user")
    def test_get_custom_claims_success(self, mock_get):
        from services.auth_service import FirebaseAuthService

        mock_user = MagicMock()
        mock_user.custom_claims = {"role": "admin"}
        mock_get.return_value = mock_user
        service = FirebaseAuthService()
        result = service.get_custom_user_claims("u1")
        assert result == {"role": "admin"}

    @patch("services.auth_service.auth.get_user")
    def test_get_custom_claims_failure(self, mock_get):
        from services.auth_service import FirebaseAuthService

        mock_get.side_effect = ValueError("Invalid")
        service = FirebaseAuthService()
        assert service.get_custom_user_claims("u1") is None


class TestUserProfileServiceExtended:
    ", ", "Test UserProfileService.", ", "

    def test_create_profile_no_db(self):
        from services.auth_service import UserProfileService

        service = UserProfileService()
        with patch("services.firestore_service.save_user", return_value=None):
            result = service.create_user_profile("u1", "a@b.com", {})
            assert result is False

    def test_update_profile_no_db(self):
        from services.auth_service import UserProfileService

        service = UserProfileService()
        with patch("services.firestore_service.save_user", return_value=None):
            result = service.update_user_profile("u1", {"name": "Test"})
            assert result is False

    def test_update_last_login_no_db(self):
        from services.auth_service import UserProfileService

        service = UserProfileService()
        with patch("services.firestore_service.save_user", return_value=None):
            result = service.update_last_login("u1")
            assert result is False


class TestMapsServiceExtended:
    ", ", "Test MapsService thoroughly.", ", "

    @patch("services.maps_service.requests.get")
    def test_find_polling_booth_no_api_key(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = None
        result = service.find_polling_booth(1.0, 2.0)
        assert result is not None
        assert "booth_name" in result
        assert result["lat"] == 1.01

    @patch("services.maps_service.requests.get")
    def test_find_polling_booth_api_error(self, mock_get):
        from services.maps_service import MapsService
        import requests

        service = MapsService()
        service.api_key = "key"
        mock_get.side_effect = requests.RequestException("API Error")
        result = service.find_polling_booth(1.0, 2.0)
        assert result is not None
        assert result["booth_name"] == "Community Center Polling Station"

    @patch("services.maps_service.requests.get")
    def test_find_polling_booth_zero_results(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = "key"
        mock_get.return_value.json.return_value = {"status": "OK", "results": []}
        result = service.find_polling_booth(1.0, 2.0)
        assert result is not None
        assert "mock_place" in result["place_id"]

    @patch("services.maps_service.requests.get")
    def test_find_polling_booth_request_denied(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = "key"
        mock_get.return_value.json.return_value = {"status": "REQUEST_DENIED"}
        result = service.find_polling_booth(1.0, 2.0)
        assert result is not None
        assert "mock_place" in result["place_id"]

    @patch("services.maps_service.requests.get")
    def test_find_multiple_booths(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = "key"
        mock_get.return_value.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "name": "B1",
                    "geometry": {"location": {"lat": 1, "lng": 1}},
                    "vicinity": "V1",
                },
                {
                    "name": "B2",
                    "geometry": {"location": {"lat": 2, "lng": 2}},
                    "vicinity": "V2",
                },
            ],
        }
        result = service.find_multiple_booths(1.0, 2.0, max_results=5)
        assert len(result) == 2

    @patch("services.maps_service.requests.get")
    def test_find_multiple_booths_no_key(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = None
        result = service.find_multiple_booths(1.0, 2.0)
        assert len(result) == 1
        assert result[0]["booth_name"] == "Community Center Polling Station"

    @patch("services.maps_service.requests.get")
    def test_geocode_success(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = "key"
        mock_get.return_value.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "formatted_address": "123 Test St",
                    "geometry": {"location": {"lat": 1, "lng": 2}},
                }
            ],
        }
        result = service.geocode("123 Test St")
        assert result is not None
        assert result["lat"] == 1
        assert result["lng"] == 2

    @patch("services.maps_service.requests.get")
    def test_geocode_no_key(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = None
        result = service.geocode("123 Test St")
        assert result is None

    @patch("services.maps_service.requests.get")
    def test_geocode_zero_results(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = "key"
        mock_get.return_value.json.return_value = {"status": "OK", "results": []}
        result = service.geocode("Nonexistent Address")
        assert result is None

    @patch("services.maps_service.requests.get")
    def test_reverse_geocode_success(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = "key"
        mock_get.return_value.json.return_value = {
            "status": "OK",
            "results": [{"formatted_address": "123 Test St"}],
        }
        result = service.reverse_geocode(1.0, 2.0)
        assert result == "123 Test St"

    @patch("services.maps_service.requests.get")
    def test_reverse_geocode_no_key(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = None
        result = service.reverse_geocode(1.0, 2.0)
        assert result == "Location coordinates provided"

    @patch("services.maps_service.requests.get")
    def test_get_directions_success(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = "key"
        mock_get.return_value.json.return_value = {
            "status": "OK",
            "routes": [
                {
                    "legs": [
                        {
                            "distance": {"text": "1 km"},
                            "duration": {"text": "10 mins"},
                            "start_address": "Start",
                            "end_address": "End",
                            "steps": [
                                {
                                    "distance": {"text": "500 m"},
                                    "duration": {"text": "5 mins"},
                                    "html_instructions": "Go straight",
                                }
                            ],
                        }
                    ]
                }
            ],
        }
        result = service.get_directions(1.0, 2.0, 3.0, 4.0)
        assert result is not None
        assert result["distance"] == "1 km"

    @patch("services.maps_service.requests.get")
    def test_get_directions_no_key(self, mock_get):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = None
        result = service.get_directions(1.0, 2.0, 3.0, 4.0)
        assert result is not None
        assert result["distance"] == "1.2 km"

    def test_get_static_map_url(self):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = "key"
        url = service.get_static_map_url(1.0, 2.0)
        assert "staticmap" in url
        assert "key=key" in url

    def test_get_static_map_url_no_key(self):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = None
        url = service.get_static_map_url(1.0, 2.0)
        assert "maps.google.com" in url

    def test_get_embed_html(self):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = "key"
        html = service.get_embed_html(1.0, 2.0)
        assert "<iframe" in html
        assert "google.com/maps/embed" in html

    def test_get_embed_html_no_key(self):
        from services.maps_service import MapsService

        service = MapsService()
        service.api_key = None
        html = service.get_embed_html(1.0, 2.0)
        assert "<iframe" in html
        assert "svembed" in html

    def test_format_booth_data(self):
        from services.maps_service import MapsService

        service = MapsService()
        place = {
            "name": "Test Booth",
            "vicinity": "123 Main St",
            "place_id": "test123",
            "geometry": {"location": {"lat": 1.0, "lng": 2.0}},
            "rating": 4.5,
            "user_ratings_total": 100,
            "opening_hours": {"weekday_text": ["Mon: 9-5"]},
            "types": ["school"],
        }
        result = service._format_booth_data(place, 0.0, 0.0)
        assert result["booth_name"] == "Test Booth"
        assert result["rating"] == 4.5

    def test_mock_directions(self):
        from services.maps_service import MapsService

        service = MapsService()
        result = service._mock_directions(1.0, 2.0, 3.0, 4.0)
        assert "distance" in result
        assert "steps" in result
        assert len(result["steps"]) == 3


class TestTranslateServiceExtended:
    ", ", "Test TranslateService and ElectionContentTranslator.", ", "

    def test_translate_same_language(self):
        from services.translate_service import TranslateService

        service = TranslateService()
        result = service.translate("Hello", "en", "en")
        assert result["translated_text"] == "Hello"

    def test_translate_mock_fallback(self):
        from services.translate_service import TranslateService

        service = TranslateService()
        service._initialized = False
        result = service.translate("How do I register to vote?", "hi")
        assert "translated_text" in result

    def test_translate_mock_fallback_unknown_text(self):
        from services.translate_service import TranslateService

        service = TranslateService()
        service._initialized = False
        result = service.translate("Random text", "hi")
        assert "[HI]" in result["translated_text"]

    def test_translate_batch(self):
        from services.translate_service import TranslateService

        service = TranslateService()
        service._initialized = False
        result = service.translate_batch(["Hello", "World"], "hi")
        assert len(result) == 2
        assert "translated_text" in result[0]

    def test_get_supported_languages(self):
        from services.translate_service import TranslateService

        service = TranslateService()
        langs = service.get_supported_languages()
        assert len(langs) > 0
        assert any(lang["code"] == "en" for lang in langs)

    def test_detect_language_english(self):
        from services.translate_service import TranslateService

        service = TranslateService()
        result = service._detect_with_rules("Hello world")
        assert result == "en"

    def test_translate_election_content(self):
        from services.translate_service import TranslateService

        service = TranslateService()
        service._initialized = False
        content = {"title": "Election Info", "description": "Voting details"}
        result = service.translate_election_content(content, "hi")
        assert "title" in result
        assert "translated_text" in result.get("title", ", ") or "title" in result

    def test_translate_election_content_with_steps(self):
        from services.translate_service import TranslateService

        service = TranslateService()
        service._initialized = False
        content = {
            "title": "Steps",
            "steps": [
                {"step": 1, "description": "Register"},
                {"step": 2, "description": "Vote"},
            ],
        }
        result = service.translate_election_content(content, "hi")
        assert "steps" in result

    def test_translate_election_content_with_tips(self):
        from services.translate_service import TranslateService

        service = TranslateService()
        service._initialized = False
        content = {"title": "Tips", "tips": ["Tip 1", "Tip 2"]}
        result = service.translate_election_content(content, "hi")
        assert "tips" in result

    def test_election_translator_translate_faqs(self):
        from services.translate_service import ElectionContentTranslator

        translator = ElectionContentTranslator()
        faqs = [
            {
                "id": "1",
                "question": "Q1",
                "answer": "A1",
                "category": "test",
                "tags": [],
            }
        ]
        result = translator.translate_faqs(faqs, "hi")
        assert len(result) == 1
        assert "question" in result[0]

    def test_election_translator_translate_timeline(self):
        from services.translate_service import ElectionContentTranslator

        translator = ElectionContentTranslator()
        timeline = {
            "id": "1",
            "title": "Timeline",
            "description": "Desc",
            "registration_start": "2026-01-01",
            "polling_date": "2026-05-01",
        }
        result = translator.translate_timeline(timeline, "hi")
        assert "title" in result
        assert "registration_start" in result

    def test_election_translator_translate_steps(self):
        from services.translate_service import ElectionContentTranslator

        translator = ElectionContentTranslator()
        steps = [{"title": "Step 1", "description": "Desc 1", "extra": "data"}]
        result = translator.translate_election_steps(steps, "hi")
        assert len(result) == 1
        assert "title" in result[0]
        assert "description" in result[0]

    def test_election_translator_get_language_name(self):
        from services.translate_service import ElectionContentTranslator

        translator = ElectionContentTranslator()
        name = translator.get_language_name("hi")
        assert name == "Hindi"


class TestSpeechServiceExtended:
    ", ", "Test SpeechToTextService.", ", "

    def test_recognize_no_init(self):
        from services.speech_service import SpeechToTextService

        service = SpeechToTextService()
        service._initialized = False
        result = service.recognize(b"audio")
        assert result is None

    def test_recognize_exception(self):
        from services.speech_service import SpeechToTextService

        service = SpeechToTextService()
        service._initialized = True
        service.client = MagicMock()
        service.client.recognize.side_effect = Exception("API Error")
        result = service.recognize(b"audio")
        assert result is None

    def test_recognize_no_alternatives(self):
        from services.speech_service import SpeechToTextService

        service = SpeechToTextService()
        service._initialized = True
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.alternatives = []
        mock_client.recognize.return_value = MagicMock(results=[mock_result])
        service.client = mock_client
        result = service.recognize(b"audio")
        assert result is None

    def test_recognize_success(self):
        from services.speech_service import SpeechToTextService

        service = SpeechToTextService()
        service._initialized = True
        mock_alt = MagicMock()
        mock_alt.transcript = "Hello world"
        mock_result = MagicMock()
        mock_result.alternatives = [mock_alt]
        mock_response = MagicMock()
        mock_response.results = [mock_result]
        mock_speech = MagicMock()
        mock_speech.RecognitionAudio = MagicMock()
        mock_speech.RecognitionConfig = MagicMock()
        mock_speech.RecognitionConfig.AudioEncoding.LINEAR16 = 1
        mock_client = MagicMock()
        mock_client.recognize.return_value = mock_response
        with patch.dict("sys.modules", {"google.cloud.speech": mock_speech}):
            service.client = mock_client
            result = service.recognize(b"audio")
            assert result == "Hello world"

    def test_get_audio_config(self):
        from services.speech_service import SpeechToTextService

        service = SpeechToTextService()
        config = service.get_audio_config()
        assert "sample_rate" in config
        assert "language_codes" in config
        assert "encoding" in config

    def test_recognize_from_base64(self):
        from services.speech_service import SpeechToTextService

        service = SpeechToTextService()
        service._initialized = True
        mock_alt = MagicMock()
        mock_alt.transcript = "Hello"
        mock_result = MagicMock()
        mock_result.alternatives = [mock_alt]
        mock_response = MagicMock()
        mock_response.results = [mock_result]
        mock_speech = MagicMock()
        mock_speech.RecognitionAudio = MagicMock()
        mock_speech.RecognitionConfig = MagicMock()
        mock_speech.RecognitionConfig.AudioEncoding.LINEAR16 = 1
        mock_client = MagicMock()
        mock_client.recognize.return_value = mock_response
        with patch.dict("sys.modules", {"google.cloud.speech": mock_speech}):
            service.client = mock_client
            audio = base64.b64encode(b"audio data").decode()
            result = service.recognize_from_base64(audio)
            assert result == "Hello"

    def test_recognize_from_base64_invalid(self):
        from services.speech_service import SpeechToTextService

        service = SpeechToTextService()
        result = service.recognize_from_base64("not-valid-base64!!!")
        assert result is not None

    def test_transcribe_streaming_no_init(self):
        from services.speech_service import SpeechToTextService

        service = SpeechToTextService()
        service._initialized = False
        result = service.transcribe_streaming(iter([]))
        assert result is not None


class TestTTSServiceExtended:
    ", ", "Test TextToSpeechService and AudioGuidancePlayer.", ", "

    def test_synthesize_no_init(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        service._initialized = False
        result = service.synthesize("Hello")
        assert result is not None
        assert result["mock"] is True

    def test_synthesize_exception(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        service._initialized = True
        service.client = MagicMock()
        service.client.synthesize_speech.side_effect = Exception("API Error")
        result = service.synthesize("Hello")
        assert result is not None
        assert result["mock"] is True

    def test_synthesize_custom_language(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        service._initialized = True
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.audio_content = b"audio"
        mock_client.synthesize_speech.return_value = mock_response
        service.client = mock_client
        result = service.synthesize("Test", language="hi")
        assert result["audio_format"] == "mp3"

    def test_synthesize_ssml_no_init(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        service._initialized = False
        result = service.synthesize_ssml("<speak>Hello</speak>")
        assert result is None

    def test_synthesize_ssml_success(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        service._initialized = True
        mock_response = MagicMock()
        mock_response.audio_content = b"audio"
        mock_tts = MagicMock()
        mock_tts.SynthesisInput = MagicMock()
        mock_tts.VoiceSelectionParams = MagicMock()
        mock_tts.AudioConfig = MagicMock()
        mock_tts.AudioConfig.MP3 = 1
        mock_client = MagicMock()
        mock_client.synthesize_speech.return_value = mock_response
        with patch.dict("sys.modules", {"google.cloud.texttospeech": mock_tts}):
            service.client = mock_client
            result = service.synthesize_ssml("<speak>Hello</speak>")
            assert result is not None
            assert result["audio_format"] == "mp3"

    def test_speak_election_steps(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        service._initialized = False
        steps = [{"title": "Step 1", "description": "First step"}]
        result = service.speak_election_steps(steps, "en")
        assert result is not None
        assert "Step 1" in result["text"]

    def test_speak_faq_answer(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        service._initialized = False
        result = service.speak_faq_answer("Q?", "A.", "en")
        assert result is not None
        assert "Question:" in result["text"]

    def test_speak_timeline_event(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        service._initialized = False
        event = {"title": "Election", "date": "2026-01-01", "description": "Details"}
        result = service.speak_timeline_event(event, "en")
        assert result is not None
        assert "Important date" in result["text"]

    def test_format_steps_for_speech(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        steps = [{"title": "Step 1", "description": "First step"}]
        text = service._format_steps_for_speech(steps)
        assert "Step 1" in text

    def test_format_steps_for_speech_empty(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        text = service._format_steps_for_speech([])
        assert text == ", "

    def test_format_steps_for_speech_string(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        text = service._format_steps_for_speech(["Step A", "Step B"])
        assert "Step 1: Step A" in text

    def test_get_available_voices(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        voices = service.get_available_voices()
        assert len(voices) > 0

    def test_mock_synthesize(self):
        from services.tts_service import TextToSpeechService

        service = TextToSpeechService()
        result = service._mock_synthesize("Hello", "en", "mp3")
        assert result["mock"] is True
        assert result["audio_format"] == "mp3"

    def test_audio_player_play_faq(self):
        from services.tts_service import AudioGuidancePlayer

        player = AudioGuidancePlayer()
        player.service = MagicMock()
        player.service.speak_faq_answer.return_value = {"text": "FAQ audio"}
        result = player.play_election_info("faq", {"question": "Q", "answer": "A"})
        assert result == {"text": "FAQ audio"}

    def test_audio_player_play_steps(self):
        from services.tts_service import AudioGuidancePlayer

        player = AudioGuidancePlayer()
        player.service = MagicMock()
        player.service.speak_election_steps.return_value = {"text": "Steps audio"}
        result = player.play_election_info("steps", [{"title": "Step 1"}])
        assert result == {"text": "Steps audio"}

    def test_audio_player_play_timeline(self):
        from services.tts_service import AudioGuidancePlayer

        player = AudioGuidancePlayer()
        player.service = MagicMock()
        player.service.speak_timeline_event.return_value = {"text": "Timeline audio"}
        result = player.play_election_info("timeline", {"title": "Event"})
        assert result == {"text": "Timeline audio"}

    def test_audio_player_play_default(self):
        from services.tts_service import AudioGuidancePlayer

        player = AudioGuidancePlayer()
        player.service = MagicMock()
        player.service.synthesize.return_value = {"text": "Default audio"}
        result = player.play_election_info("unknown", "some data")
        assert result == {"text": "Default audio"}

    def test_get_playback_url_mp3(self):
        from services.tts_service import AudioGuidancePlayer

        player = AudioGuidancePlayer()
        audio = base64.b64encode(b"test_audio").decode()
        url = player.get_playback_url(audio, "mp3")
        assert url.startswith("data:audio/mp3;base64,")

    def test_get_playback_url_ogg(self):
        from services.tts_service import AudioGuidancePlayer

        player = AudioGuidancePlayer()
        url = player.get_playback_url("base64data", "ogg_opus")
        assert "audio/ogg" in url

    def test_get_playback_url_default(self):
        from services.tts_service import AudioGuidancePlayer

        player = AudioGuidancePlayer()
        url = player.get_playback_url("base64data", "unknown")
        assert "audio/mp3" in url


class TestCacheServiceExtended:
    ", ", "Test CacheService thoroughly.", ", "

    def test_cache_in_memory_get(self):
        from services.cache_service import CacheService

        service = CacheService()
        service._use_redis = False
        result = service.get("nonexistent")
        assert result is None

    def test_cache_in_memory_set_get(self):
        from services.cache_service import CacheService

        service = CacheService()
        service._use_redis = False
        service.set("key", "value")
        result = service.get("key")
        assert result == "value"

    def test_cache_in_memory_delete(self):
        from services.cache_service import CacheService

        service = CacheService()
        service._use_redis = False
        service.set("key", "value")
        result = service.delete("key")
        assert result is True
        assert service.get("key") is None

    def test_cache_redis_get_error(self):
        from services.cache_service import CacheService

        service = CacheService()
        service._use_redis = True
        service._redis_client = MagicMock()
        service._redis_client.get.side_effect = Exception("Redis error")
        result = service.get("key")
        assert result is None

    def test_cache_redis_set_error(self):
        from services.cache_service import CacheService

        service = CacheService()
        service._use_redis = True
        service._redis_client = MagicMock()
        service._redis_client.setex.side_effect = Exception("Redis error")
        result = service.set("key", "value")
        assert result is True

    def test_cache_redis_delete_error(self):
        from services.cache_service import CacheService

        service = CacheService()
        service._use_redis = True
        service._redis_client = MagicMock()
        service._redis_client.delete.side_effect = Exception("Redis error")
        result = service.delete("key")
        assert result is True

    def test_clear_pattern_in_memory(self):
        from services.cache_service import CacheService

        service = CacheService()
        service._use_redis = False
        service.set("cache:test:item1", "val1")
        service.set("cache:test:item2", "val2")
        service.set("other:key", "val3")
        count = service.clear_pattern("test")
        assert count == 2
        assert service.get("cache:test:item1") is None
        assert service.get("other:key") == "val3"

    def test_clear_pattern_redis_error(self):
        from services.cache_service import CacheService

        service = CacheService()
        service._use_redis = True
        service._redis_client = MagicMock()
        service._redis_client.keys.side_effect = Exception("Redis error")
        result = service.clear_pattern("key")
        assert result == 0

    def test_module_level_functions(self):
        from services.cache_service import cache_get, cache_set, cache_delete

        cache_set("test_key", "test_value")
        result = cache_get("test_key")
        assert result == "test_value"
        cache_delete("test_key")
        result = cache_get("test_key")
        assert result is None

    def test_cached_decorator(self):
        from services.cache_service import cached

        call_count = 0

        @cached(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(5)
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1

    def test_get_cache_service(self):
        from services.cache_service import get_cache_service, CacheService

        service = get_cache_service()
        assert isinstance(service, CacheService)


class TestCalendarServiceExtended:
    ", ", "Test CalendarService and LocalCalendarService.", ", "

    @patch("services.calendar_service.requests.post")
    def test_create_reminder_failure(self, mock_post):
        from services.calendar_service import CalendarService

        service = CalendarService()
        service.access_token = "token"
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"error": "Bad request"}
        result = service.create_election_reminder("Election", "2026-01-01")
        assert result is not None
        assert "icalUID" in result

    @patch("services.calendar_service.requests.post")
    def test_create_reminder_no_token(self, mock_post):
        from services.calendar_service import CalendarService

        service = CalendarService()
        service.access_token = None
        result = service.create_election_reminder("Election", "2026-01-01")
        assert result is not None
        assert "icalUID" in result

    @patch("services.calendar_service.requests.post")
    def test_create_reminder_exception(self, mock_post):
        from services.calendar_service import CalendarService
        import requests

        service = CalendarService()
        service.access_token = "token"
        mock_post.side_effect = requests.RequestException("Network error")
        result = service.create_election_reminder("Election", "2026-01-01")
        assert result is not None
        assert "icalUID" in result

    @patch("services.calendar_service.requests.get")
    def test_get_upcoming_events(self, mock_get):
        from services.calendar_service import CalendarService

        service = CalendarService()
        service.access_token = "token"
        mock_get.return_value.json.return_value = {
            "items": [
                {"summary": "Event 1", "start": {"dateTime": "2026-01-01T00:00:00"}}
            ]
        }
        mock_get.return_value.status_code = 200
        result = service.get_upcoming_events()
        assert len(result) == 1

    @patch("services.calendar_service.requests.get")
    def test_get_upcoming_events_no_token(self, mock_get):
        from services.calendar_service import CalendarService

        service = CalendarService()
        service.access_token = None
        result = service.get_upcoming_events()
        assert result == []

    @patch("services.calendar_service.requests.get")
    def test_get_upcoming_events_exception(self, mock_get):
        from services.calendar_service import CalendarService
        import requests

        service = CalendarService()
        service.access_token = "token"
        mock_get.side_effect = requests.RequestException("Network error")
        result = service.get_upcoming_events()
        assert result == []

    @patch("services.calendar_service.requests.post")
    def test_create_registration_reminder(self, mock_post):
        from services.calendar_service import CalendarService

        service = CalendarService()
        service.access_token = "token"
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "reg1"}
        result = service.create_registration_reminder("2026-03-01")
        assert result is not None

    @patch("services.calendar_service.requests.post")
    def test_create_result_reminder(self, mock_post):
        from services.calendar_service import CalendarService

        service = CalendarService()
        service.access_token = "token"
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "result1"}
        result = service.create_result_reminder("2026-05-01")
        assert result is not None

    def test_local_generate_ics(self):
        from services.calendar_service import LocalCalendarService

        service = LocalCalendarService()
        ics = service.generate_voting_calendar("Election Day", "2026-01-01")
        assert "BEGIN:VCALENDAR" in ics
        assert "Election Day" in ics

    def test_local_generate_ics_registration(self):
        from services.calendar_service import LocalCalendarService, CalendarService

        with patch.object(
            CalendarService,
            "generate_ics_file",
            return_value="BEGIN:VCALENDAR\nRegistration",
        ):
            ics = LocalCalendarService.generate_voting_calendar(
                "Registration", "2026-03-01"
            )
            assert "BEGIN:VCALENDAR" in ics

    @patch("services.calendar_service.requests.post")
    def test_module_create_voting_reminder(self, mock_post):
        from services.calendar_service import create_voting_reminder

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "rem1"}
        result = create_voting_reminder("Election", "2026-01-01")
        assert result is not None


class TestFirestoreServiceExtended:
    ", ", "Test firestore_service module-level functions.", ", "

    def test_verify_connection_success(self):
        from services.firestore_service import verify_firestore_connection

        mock_db = MagicMock()
        mock_db.collection().document().get.return_value = MagicMock()
        with patch(
            "services.firestore_service.get_firestore_client", return_value=mock_db
        ):
            result = verify_firestore_connection()
            assert result["connected"] is True

    def test_verify_connection_failure(self):
        from services.firestore_service import verify_firestore_connection

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = verify_firestore_connection()
            assert result["connected"] is False

    def test_verify_connection_exception(self):
        from services.firestore_service import verify_firestore_connection

        mock_db = MagicMock()
        mock_db.collection().document().set.side_effect = RuntimeError(
            "Connection failed"
        )
        with patch(
            "services.firestore_service.get_firestore_client", return_value=mock_db
        ):
            result = verify_firestore_connection()
            assert result["connected"] is False

    def test_get_election_process_data_no_db(self):
        from services.firestore_service import get_election_process_data

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = get_election_process_data()
            assert result == []

    def test_get_faqs_data_no_db(self):
        from services.firestore_service import get_faqs_data

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = get_faqs_data()
            assert result == []

    def test_get_timeline_data_no_db(self):
        from services.firestore_service import get_timeline_data

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = get_timeline_data()
            assert result == []

    def test_save_user(self):
        from services.firestore_service import save_user

        mock_db = MagicMock()
        with patch(
            "services.firestore_service.get_firestore_client", return_value=mock_db
        ):
            result = save_user("u1", {"name": "Test"})
            assert result == "u1"

    def test_save_user_no_db(self):
        from services.firestore_service import save_user

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = save_user("u1", {"name": "Test"})
            assert result is None

    def test_get_user_from_service(self):
        from services.firestore_service import get_user

        mock_db = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "u1"
        doc_mock.to_dict.return_value = {"name": "Test"}
        mock_db.collection().document().get.return_value = doc_mock
        with patch(
            "services.firestore_service.get_firestore_client", return_value=mock_db
        ):
            result = get_user("u1")
            assert result is not None

    def test_get_user_no_db(self):
        from services.firestore_service import get_user

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = get_user("u1")
            assert result is None

    def test_get_reminders_no_db(self):
        from services.firestore_service import get_reminders

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = get_reminders("u1")
            assert result == []

    def test_save_reminder_no_db(self):
        from services.firestore_service import save_reminder

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = save_reminder("u1", {"title": "Test"})
            assert result is None

    def test_update_reminder_no_db(self):
        from services.firestore_service import update_reminder

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = update_reminder("u1", "r1", {"title": "Updated"})
            assert result is None

    def test_delete_reminder_no_db(self):
        from services.firestore_service import delete_reminder

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = delete_reminder("u1", "r1")
            assert result is False

    def test_save_bookmark_no_db(self):
        from services.firestore_service import save_bookmark

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = save_bookmark("u1", {"title": "Test"})
            assert result is None

    def test_get_bookmarks_no_db(self):
        from services.firestore_service import get_bookmarks

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = get_bookmarks("u1")
            assert result == []

    def test_get_bookmark_by_resource_no_db(self):
        from services.firestore_service import get_bookmark_by_resource

        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            result = get_bookmark_by_resource("u1", "faq", "f1")
            assert result is None
