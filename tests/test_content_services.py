from unittest.mock import MagicMock, patch

import pytest

from services.election_process_service import ElectionProcessService
from services.faq_service import FAQService
from services.polling_guidance_service import PollingGuidanceService
from services.timeline_service import TimelineService


class TestContentServices:
    @pytest.fixture
    def mock_db(self):
        with patch("services.election_process_service.firestore.client") as mock:
            yield mock

    @pytest.fixture
    def mock_faq_db(self):
        with patch("services.faq_service.firestore.client") as mock:
            yield mock

    @pytest.fixture
    def mock_polling_db(self):
        with patch("services.polling_guidance_service.firestore.client") as mock:
            yield mock

    @pytest.fixture
    def mock_timeline_db(self):
        with patch("services.timeline_service.firestore.client") as mock:
            yield mock

    # --- ElectionProcessService ---
    def test_election_process_get_all(self, mock_db):
        service = ElectionProcessService()
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "p1"
        doc_mock.to_dict.return_value = {"title": "T1", "is_active": True}
        db_mock.collection().where().where().stream.return_value = [doc_mock]
        service._db = db_mock

        result = service.get_all()
        assert len(result) == 1
        assert result[0]["id"] == "p1"

    def test_election_process_get_by_id(self, mock_db):
        service = ElectionProcessService()
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "p1"
        doc_mock.to_dict.return_value = {"title": "T1"}
        db_mock.collection().document().get.return_value = doc_mock
        service._db = db_mock

        result = service.get_by_id("p1")
        assert result["id"] == "p1"

    def test_election_process_create(self, mock_db):
        service = ElectionProcessService()
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "p1"
        db_mock.collection().document.return_value = doc_mock
        service._db = db_mock

        result = service.create("T1", "Intro", [], [])
        assert result["id"] == "p1"
        doc_mock.set.assert_called_once()

    def test_election_process_update(self, mock_db):
        service = ElectionProcessService()
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"title": "T2"}
        db_mock.collection().document().get.return_value = doc_mock
        service._db = db_mock

        result = service.update("p1", {"title": "T2"})
        assert result is not None
        db_mock.collection().document().update.assert_called_once()

    def test_election_process_delete(self, mock_db):
        service = ElectionProcessService()
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        service._db = db_mock

        result = service.delete("p1", soft=True)
        assert result is True
        db_mock.collection().document().update.assert_called_once()

        result_hard = service.delete("p1", soft=False)
        assert result_hard is True
        db_mock.collection().document().delete.assert_called_once()

    def test_election_process_get_all_admin(self, mock_db):
        service = ElectionProcessService()
        db_mock = MagicMock()
        db_mock.collection().stream.return_value = []
        service._db = db_mock
        assert service.get_all_for_admin() == []

    # --- FAQService ---
    def test_faq_get_all(self, mock_faq_db):
        service = FAQService()
        db_mock = MagicMock()
        db_mock.collection().where().where().stream.return_value = []
        service._db = db_mock
        assert service.get_all() == []

    def test_faq_get_by_id(self, mock_faq_db):
        service = FAQService()
        db_mock = MagicMock()
        db_mock.collection().document().get.return_value.exists = False
        service._db = db_mock
        assert service.get_by_id("faq1") is None

    def test_faq_create(self, mock_faq_db):
        service = FAQService()
        db_mock = MagicMock()
        db_mock.collection().document().id = "f1"
        service._db = db_mock
        res = service.create("Q", "A", "cat")
        assert res["id"] == "f1"

    def test_faq_update(self, mock_faq_db):
        service = FAQService()
        db_mock = MagicMock()
        db_mock.collection().document().get.return_value.exists = False
        service._db = db_mock
        assert service.update("f1", {}) is None

    def test_faq_delete(self, mock_faq_db):
        service = FAQService()
        db_mock = MagicMock()
        db_mock.collection().document().update.side_effect = Exception("Not found")
        service._db = db_mock
        assert service.delete("f1") is False

    # --- PollingGuidanceService ---
    def test_polling_get_all(self, mock_polling_db):
        service = PollingGuidanceService()
        db_mock = MagicMock()
        db_mock.collection().where().where().stream.return_value = []
        service._db = db_mock
        assert service.get_all() == []

    def test_polling_get_by_id(self, mock_polling_db):
        service = PollingGuidanceService()
        db_mock = MagicMock()
        db_mock.collection().document().get.return_value.exists = False
        service._db = db_mock
        assert service.get_by_id("p1") is None

    def test_polling_create(self, mock_polling_db):
        service = PollingGuidanceService()
        db_mock = MagicMock()
        db_mock.collection().document().id = "pg1"
        service._db = db_mock
        res = service.create("T", "D", "reg")
        assert res["id"] == "pg1"

    def test_polling_update(self, mock_polling_db):
        service = PollingGuidanceService()
        db_mock = MagicMock()
        db_mock.collection().document().get.return_value.exists = False
        service._db = db_mock
        assert service.update("pg1", {}) is None

    def test_polling_delete(self, mock_polling_db):
        service = PollingGuidanceService()
        db_mock = MagicMock()
        db_mock.collection().document().get.return_value.exists = False
        service._db = db_mock
        assert service.delete("pg1") is False

    def test_polling_get_all_admin(self, mock_polling_db):
        service = PollingGuidanceService()
        db_mock = MagicMock()
        db_mock.collection().stream.return_value = []
        service._db = db_mock
        assert service.get_all_for_admin() == []

    # --- TimelineService ---
    def test_timeline_get_all(self, mock_timeline_db):
        service = TimelineService()
        db_mock = MagicMock()
        db_mock.collection().where().where().stream.return_value = []
        service._db = db_mock
        assert service.get_all() == []

    def test_timeline_get_by_id(self, mock_timeline_db):
        service = TimelineService()
        db_mock = MagicMock()
        db_mock.collection().document().get.return_value.exists = False
        service._db = db_mock
        assert service.get_by_id("t1") is None

    def test_timeline_create(self, mock_timeline_db):
        service = TimelineService()
        db_mock = MagicMock()
        db_mock.collection().document().id = "t1"
        service._db = db_mock
        res = service.create("T", "D", "2026-01-01", "reg")
        assert res["id"] == "t1"

    def test_timeline_update(self, mock_timeline_db):
        service = TimelineService()
        db_mock = MagicMock()
        db_mock.collection().document().get.return_value.exists = False
        service._db = db_mock
        assert service.update("t1", {}) is None

    def test_timeline_delete(self, mock_timeline_db):
        service = TimelineService()
        db_mock = MagicMock()
        db_mock.collection().document().get.return_value.exists = False
        service._db = db_mock
        assert service.delete("t1") is False

    def test_timeline_get_all_admin(self, mock_timeline_db):
        service = TimelineService()
        db_mock = MagicMock()
        db_mock.collection().stream.return_value = []
        service._db = db_mock
        assert service.get_all_for_admin() == []
