from unittest.mock import MagicMock, patch

import pytest

from services.firestore_service import (create_or_update_user_profile,
                                        delete_bookmark, delete_reminder,
                                        get_bookmark_by_resource,
                                        get_bookmarks,
                                        get_election_process_data,
                                        get_faqs_data, get_firestore_client,
                                        get_reminder, get_reminders,
                                        get_timeline_data, get_user,
                                        init_firebase, save_bookmark,
                                        save_reminder, save_user,
                                        update_reminder,
                                        verify_firestore_connection)


@pytest.fixture(autouse=True)
def reset_globals():
    import services.firestore_service as fs

    fs._firestore_client = None
    fs._firebase_initialized = False


class TestFirestoreService:
    @patch("services.firestore_service.firebase_admin")
    @patch("services.firestore_service.Config")
    @patch("services.firestore_service.credentials.Certificate")
    def test_init_firebase(self, mock_cert, mock_config, mock_admin):
        mock_config.FIREBASE_ADMIN_JSON = {"type": "service_account"}
        mock_config.FIREBASE_PROJECT_ID = "test-project"
        mock_admin._apps = []

        result = init_firebase()
        assert result is True
        mock_admin.initialize_app.assert_called_once()

    @patch("services.firestore_service.gcfirestore.Client")
    @patch("services.firestore_service.init_firebase", return_value=True)
    def test_get_firestore_client(self, mock_init, mock_client):
        mock_client.return_value = MagicMock()
        client = get_firestore_client()
        assert client is not None

    @patch("services.firestore_service.get_firestore_client")
    def test_verify_firestore_connection(self, mock_get_client):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.get.return_value.exists = True
        db_mock.collection().document().get.return_value = doc_mock.get.return_value
        mock_get_client.return_value = db_mock

        result = verify_firestore_connection()
        assert result["success"] is True

    @patch("services.firestore_service.get_firestore_client")
    def test_save_user(self, mock_get_client):
        db_mock = MagicMock()
        mock_get_client.return_value = db_mock
        result = save_user("u1", {"name": "Test"})
        assert result == "u1"
        db_mock.collection().document().set.assert_called_once()

    @patch("services.firestore_service.get_firestore_client")
    def test_get_user(self, mock_get_client):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"name": "Test"}
        db_mock.collection().document().get.return_value = doc_mock
        mock_get_client.return_value = db_mock

        result = get_user("u1")
        assert result == {"name": "Test"}

    @patch("services.firestore_service.get_user", return_value=None)
    @patch("services.firestore_service.get_firestore_client")
    def test_create_or_update_user_profile_new(self, mock_get_client, mock_get_user):
        db_mock = MagicMock()
        mock_get_client.return_value = db_mock

        create_or_update_user_profile("u1", "test@test.com")
        db_mock.collection().document().set.assert_called_once()

    @patch("services.firestore_service.get_firestore_client")
    def test_get_election_process_data(self, mock_get_client):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.to_dict.return_value = {"step": 1}
        db_mock.collection().document().collection().order_by().stream.return_value = [
            doc_mock
        ]
        mock_get_client.return_value = db_mock

        result = get_election_process_data()
        assert len(result) == 1
        assert result[0] == {"step": 1}

    @patch("services.firestore_service.get_firestore_client")
    def test_get_faqs_data(self, mock_get_client):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "faq1"
        doc_mock.to_dict.return_value = {"q": "What?"}
        db_mock.collection().stream.return_value = [doc_mock]
        mock_get_client.return_value = db_mock

        result = get_faqs_data()
        assert len(result) == 1
        assert result[0]["id"] == "faq1"

    @patch("services.firestore_service.get_firestore_client")
    def test_get_timeline_data(self, mock_get_client):
        db_mock = MagicMock()
        db_mock.collection().stream.return_value = []
        mock_get_client.return_value = db_mock
        assert get_timeline_data() == []

    @patch("services.firestore_service.get_firestore_client")
    def test_save_reminder(self, mock_get_client):
        db_mock = MagicMock()
        db_mock.collection().document().collection().document().id = "rem1"
        mock_get_client.return_value = db_mock
        result = save_reminder("u1", {"msg": "Hi"})
        assert result == "rem1"

    @patch("services.firestore_service.get_firestore_client")
    def test_get_reminders(self, mock_get_client):
        db_mock = MagicMock()
        db_mock.collection().document().collection().stream.return_value = []
        mock_get_client.return_value = db_mock
        assert get_reminders("u1") == []

    @patch("services.firestore_service.get_firestore_client")
    def test_get_reminder(self, mock_get_client):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "rem1"
        doc_mock.to_dict.return_value = {"msg": "Hi"}
        db_mock.collection().document().collection().document().get.return_value = (
            doc_mock
        )
        mock_get_client.return_value = db_mock
        result = get_reminder("u1", "rem1")
        assert result["id"] == "rem1"

    @patch("services.firestore_service.get_firestore_client")
    def test_update_reminder(self, mock_get_client):
        db_mock = MagicMock()
        mock_get_client.return_value = db_mock
        assert update_reminder("u1", "rem1", {"msg": "Upd"}) == "rem1"

    @patch("services.firestore_service.get_firestore_client")
    def test_delete_reminder(self, mock_get_client):
        db_mock = MagicMock()
        mock_get_client.return_value = db_mock
        assert delete_reminder("u1", "rem1") is True

    @patch("services.firestore_service.get_firestore_client")
    def test_save_bookmark(self, mock_get_client):
        db_mock = MagicMock()
        db_mock.collection().document().collection().document().id = "bm1"
        mock_get_client.return_value = db_mock
        assert save_bookmark("u1", {"item": "A"}) == "bm1"

    @patch("services.firestore_service.get_firestore_client")
    def test_get_bookmarks(self, mock_get_client):
        db_mock = MagicMock()
        db_mock.collection().document().collection().stream.return_value = []
        mock_get_client.return_value = db_mock
        assert get_bookmarks("u1") == []

    @patch("services.firestore_service.get_firestore_client")
    def test_get_bookmark_by_resource(self, mock_get_client):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "bm1"
        doc_mock.to_dict.return_value = {"item": "A"}
        db_mock.collection().document().collection().where().where().stream.return_value = [
            doc_mock
        ]
        mock_get_client.return_value = db_mock
        result = get_bookmark_by_resource("u1", "faq", "faq1")
        assert result["id"] == "bm1"

    @patch("services.firestore_service.get_firestore_client")
    def test_delete_bookmark(self, mock_get_client):
        db_mock = MagicMock()
        mock_get_client.return_value = db_mock
        assert delete_bookmark("u1", "bm1") is True
