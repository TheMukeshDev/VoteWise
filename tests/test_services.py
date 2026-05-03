from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from services.data_access_layer import FirestoreDB


@pytest.fixture
def mock_db_property():
    with patch(
        "services.data_access_layer.FirestoreDB.db", new_callable=PropertyMock
    ) as mock_db:
        yield mock_db


class TestFirestoreDB:
    def test_create_user_success(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()

        result = dal.create_user("test_user_id", {"name": "Test"})
        assert result is True
        db_mock.collection.assert_called_with("users")
        db_mock.collection().document.assert_called_with("test_user_id")
        db_mock.collection().document().set.assert_called_once()

    def test_create_user_failure(self, mock_db_property):
        db_mock = MagicMock()
        db_mock.collection().document().set.side_effect = Exception("DB Error")
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()

        result = dal.create_user("test_user_id", {"name": "Test"})
        assert result is False

    def test_get_user_success(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "test_user_id"
        doc_mock.to_dict.return_value = {"name": "Test"}
        db_mock.collection().document().get.return_value = doc_mock
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()

        result = dal.get_user("test_user_id")
        assert result == {"id": "test_user_id", "name": "Test"}

    def test_get_user_not_found(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()

        result = dal.get_user("test_user_id")
        assert result is None

    def test_update_user(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()

        result = dal.update_user("test_user_id", {"name": "Test2"})
        assert result is True
        db_mock.collection().document().update.assert_called_once()

    def test_delete_user(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()

        result = dal.delete_user("test_user_id")
        assert result is True
        db_mock.collection().document().delete.assert_called_once()

    def test_get_all_users(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock1 = MagicMock()
        doc_mock1.id = "u1"
        doc_mock1.to_dict.return_value = {"name": "User 1"}
        doc_mock2 = MagicMock()
        doc_mock2.id = "u2"
        doc_mock2.to_dict.return_value = {"name": "User 2"}

        db_mock.collection().limit().stream.return_value = [doc_mock1, doc_mock2]
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()

        result = dal.get_all_users()
        assert len(result) == 2
        assert result[0] == {"id": "u1", "name": "User 1"}

    # Testing election process
    def test_create_election_process(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        result = dal.create_election_process("proc1", {"step": 1})
        assert result is True

    def test_get_election_process(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "proc1"
        doc_mock.to_dict.return_value = {"step": 1}
        db_mock.collection().document().get.return_value = doc_mock
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_election_process("proc1")["step"] == 1

    def test_get_all_election_processes(self, mock_db_property):
        db_mock = MagicMock()
        db_mock.collection().where().stream.return_value = []
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        result = dal.get_all_election_processes(language="en")
        assert result == []

    def test_update_election_process(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.update_election_process("proc1", {"step": 2}) is True

    def test_delete_election_process(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.delete_election_process("proc1") is True

    # Timelines
    def test_create_timeline(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.create_timeline("time1", {"event": "A"}) is True

    def test_get_timeline(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "time1"
        doc_mock.to_dict.return_value = {"event": "A"}
        db_mock.collection().document().get.return_value = doc_mock
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_timeline("time1")["event"] == "A"

    def test_get_timelines(self, mock_db_property):
        db_mock = MagicMock()
        db_mock.collection().where().stream.return_value = []
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_timelines() == []

    def test_update_timeline(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.update_timeline("time1", {"event": "B"}) is True

    def test_delete_timeline(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.delete_timeline("time1") is True

    # FAQs
    def test_create_faq(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.create_faq("faq1", {"q": "What?"}) is True

    def test_get_faq(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "faq1"
        doc_mock.to_dict.return_value = {"q": "What?"}
        db_mock.collection().document().get.return_value = doc_mock
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_faq("faq1")["q"] == "What?"

    def test_get_faqs(self, mock_db_property):
        db_mock = MagicMock()
        db_mock.collection().where().stream.return_value = []
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_faqs() == []

    def test_update_faq(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.update_faq("faq1", {"q": "Why?"}) is True

    def test_delete_faq(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.delete_faq("faq1") is True

    # Reminders
    def test_create_reminder(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.create_reminder("u1", "rem1", {"msg": "Hi"}) is True

    def test_get_reminder(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "rem1"
        doc_mock.to_dict.return_value = {"msg": "Hi"}
        db_mock.collection().document().collection().document().get.return_value = (
            doc_mock
        )
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_reminder("u1", "rem1")["msg"] == "Hi"

    def test_get_user_reminders(self, mock_db_property):
        db_mock = MagicMock()
        db_mock.collection().document().collection().stream.return_value = []
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_user_reminders("u1") == []

    def test_update_reminder(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.update_reminder("u1", "rem1", {"msg": "Hello"}) is True

    def test_delete_reminder(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.delete_reminder("u1", "rem1") is True

    # Announcements
    def test_create_announcement(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.create_announcement("ann1", {"text": "A"}) is True

    def test_get_announcement(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "ann1"
        doc_mock.to_dict.return_value = {"text": "A"}
        db_mock.collection().document().get.return_value = doc_mock
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_announcement("ann1")["text"] == "A"

    def test_get_announcements(self, mock_db_property):
        db_mock = MagicMock()
        db_mock.collection().where().order_by().stream.return_value = []
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_announcements() == []

    def test_update_announcement(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.update_announcement("ann1", {"text": "B"}) is True

    def test_delete_announcement(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.delete_announcement("ann1") is True

    # Bookmarks
    def test_create_bookmark(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.create_bookmark("u1", "bm1", {"item": "A"}) is True

    def test_get_user_bookmarks(self, mock_db_property):
        db_mock = MagicMock()
        db_mock.collection().document().collection().stream.return_value = []
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_user_bookmarks("u1") == []

    def test_delete_bookmark(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.delete_bookmark("u1", "bm1") is True

    # Analytics
    def test_create_analytics(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.create_analytics("an1", {"m": "A"}) is True

    def test_get_analytics(self, mock_db_property):
        db_mock = MagicMock()
        db_mock.collection().stream.return_value = []
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_analytics() == []

    def test_increment_analytics(self, mock_db_property):
        import datetime

        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.increment_analytics("logins", datetime.datetime.now()) is True

    # Polling Guidance
    def test_create_polling_guidance(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.create_polling_guidance("pg1", {"x": "y"}) is True

    def test_get_polling_guidance(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "pg1"
        doc_mock.to_dict.return_value = {"x": "y"}
        db_mock.collection().document().get.return_value = doc_mock
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_polling_guidance("pg1")["x"] == "y"

    def test_get_polling_guidances(self, mock_db_property):
        db_mock = MagicMock()
        db_mock.collection().where().stream.return_value = []
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_polling_guidances() == []

    def test_update_polling_guidance(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.update_polling_guidance("pg1", {"x": "z"}) is True

    # Settings
    def test_create_setting(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.create_setting("key1", "val1") is True

    def test_get_setting(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"value": "val1"}
        db_mock.collection().document().get.return_value = doc_mock
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_setting("key1") == "val1"

    def test_get_all_settings(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "key1"
        doc_mock.to_dict.return_value = {"value": "val1"}
        db_mock.collection().stream.return_value = [doc_mock]
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_all_settings() == {"key1": "val1"}

    # Preferences
    def test_create_or_update_preferences(self, mock_db_property):
        db_mock = MagicMock()
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.create_or_update_preferences("u1", {"p": "v"}) is True

    def test_get_preferences(self, mock_db_property):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "main"
        doc_mock.to_dict.return_value = {"p": "v"}
        db_mock.collection().document().collection().document().get.return_value = (
            doc_mock
        )
        mock_db_property.return_value = db_mock
        dal = FirestoreDB()
        assert dal.get_preferences("u1")["p"] == "v"
