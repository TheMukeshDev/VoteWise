from unittest.mock import MagicMock, patch

# Auth Service
from services.auth_service import FirebaseAuthService, UserProfileService

# Cache Service
from services.cache_service import CacheService

# Calendar Service
from services.calendar_service import CalendarService, LocalCalendarService

# Maps Service
from services.maps_service import MapsService

# Speech & TTS
from services.speech_service import SpeechToTextService

# Translate Service
from services.translate_service import ElectionContentTranslator, TranslateService
from services.tts_service import AudioGuidancePlayer, TextToSpeechService


class TestAuthService:
    @patch("services.auth_service.auth.verify_id_token")
    def test_verify_token(self, mock_verify):
        service = FirebaseAuthService()
        mock_verify.return_value = {"uid": "u1"}
        res = service.verify_id_token("token")
        assert res == {"uid": "u1"}

    @patch("services.auth_service.auth.create_custom_token")
    def test_create_custom_token(self, mock_create):
        service = FirebaseAuthService()
        mock_create.return_value = b"token"
        res = service.create_custom_token("u1")
        assert res == "token"

    @patch("services.auth_service.auth.get_user")
    def test_get_user(self, mock_get_user):
        service = FirebaseAuthService()
        mock_user = MagicMock()
        mock_user.uid = "u1"
        mock_user.email = "test@example.com"
        mock_user.display_name = "Test"
        mock_user.photo_url = "url"
        mock_user.disabled = False
        mock_user.email_verified = True
        mock_user.provider_data = []
        mock_get_user.return_value = mock_user
        res = service.get_user("u1")
        assert res["uid"] == "u1"


class TestUserProfileService:
    def test_get_user_profile(self):
        with patch("services.auth_service.get_user") as mock_get:
            mock_get.return_value = {"email": "test@test.com"}
            service = UserProfileService()
            result = service.get_user_profile("u1")
            assert result["id"] == "u1"
            assert result["email"] == "test@test.com"

    def test_create_profile(self):
        with patch("services.firestore_service.save_user") as mock_save:
            mock_save.return_value = "u1"
            service = UserProfileService()
            assert service.create_user_profile("u1", "a@b.com", {}) is True


class TestCacheService:
    def test_cache_methods(self):
        service = CacheService()
        service._use_redis = True
        service._redis_client = MagicMock()
        service._redis_client.get.return_value = b'{"k": "v"}'
        assert service.get("key") == {"k": "v"}
        service.set("key", {"k": "v"})
        service.delete("key")
        service._redis_client.keys.return_value = [b"cache:key:1"]
        service.clear_pattern("key*")

        # Ensure it works without redis
        service._use_redis = False
        assert service.get("key_not_exists") is None
        assert service.set("key", "v") is True
        assert service.get("key") == "v"


class TestCalendarService:
    @patch("services.calendar_service.requests.post")
    def test_create_reminder(self, mock_post):
        service = CalendarService()
        service.access_token = "token"
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "e1"}

        res = service.create_election_reminder("E", "2026-01-01")
        assert res["id"] == "e1"


class TestLocalCalendarService:
    def test_generate_ics(self):
        service = LocalCalendarService()
        res = service.generate_voting_calendar("T", "2026-01-01")
        assert "BEGIN:VCALENDAR" in res


class TestMapsService:
    @patch("services.maps_service.requests.get")
    def test_find_polling_booth(self, mock_get):
        service = MapsService()
        service.api_key = "key"
        mock_get.return_value.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "name": "Booth 1",
                    "geometry": {"location": {"lat": 1, "lng": 1}},
                    "vicinity": "V",
                }
            ],
        }
        res = service.find_polling_booth(1, 1)
        assert res["booth_name"] == "Booth 1"


class TestTranslateService:
    def test_translate(self):
        service = TranslateService()
        service._initialized = True
        mock_client = MagicMock()
        mock_client.translate.return_value = {
            "translatedText": "T",
            "detectedSourceLanguage": "en",
        }
        service.client = mock_client

        res = service.translate("Text", "hi")
        assert res["translated_text"] == "T"


class TestElectionContentTranslator:
    def test_translate_faqs(self):
        translator = ElectionContentTranslator()
        translator.translator = MagicMock()
        translator.translator.translate.return_value = {"translated_text": "Translated"}
        faqs = [{"question": "Q", "answer": "A"}]
        res = translator.translate_faqs(faqs, "hi")
        assert res[0]["question"] == "Translated"


class TestSpeechServices:
    @patch.dict("sys.modules", {"google.cloud.speech": MagicMock()})
    def test_recognize(self):
        service = SpeechToTextService()
        service._initialized = True
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.alternatives = [MagicMock(transcript="T", confidence=0.9)]
        mock_client.recognize.return_value = MagicMock(results=[mock_result])
        service.client = mock_client

        res = service.recognize(b"audio")
        assert res == "T"

    @patch.dict("sys.modules", {"google.cloud.texttospeech": MagicMock()})
    def test_synthesize(self):
        service = TextToSpeechService()
        service._initialized = True
        mock_client = MagicMock()
        mock_client.synthesize_speech.return_value = MagicMock(audio_content=b"audio")
        service.client = mock_client

        res = service.synthesize("Text")
        assert res["audio_format"] == "mp3"

    def test_playback(self):
        player = AudioGuidancePlayer()
        res = player.get_playback_url("base64")
        assert res.startswith("data:audio/mp3;base64,")
