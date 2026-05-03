"""Additional service tests to push coverage to 85%+."""

from unittest.mock import MagicMock, patch

import pytest


class TestTimelineServiceExtended:
    @pytest.fixture
    def service(self):
        from services.timeline_service import TimelineService

        return TimelineService()

    def test_get_all_empty(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert service.get_all() == []

    def test_get_all_with_filters(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "t1"
        doc_mock.to_dict.return_value = {"title": "T1", "polling_date": "2026-01-01"}
        db_mock.collection().where().where().where().stream.return_value = [doc_mock]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all(election_type="general", status="upcoming")
            assert len(result) == 1

    def test_get_all_fallback(self, service):
        db_mock = MagicMock()
        db_mock.collection().where().stream.side_effect = Exception("Query failed")
        doc_mock = MagicMock()
        doc_mock.id = "t1"
        doc_mock.to_dict.return_value = {"title": "T1", "is_deleted": False}
        db_mock.collection().stream.return_value = [doc_mock]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all()
            assert len(result) == 1

    def test_get_all_fallback_double_exception(self, service):
        db_mock = MagicMock()
        db_mock.collection().where().stream.side_effect = Exception("Query failed")
        db_mock.collection().stream.side_effect = Exception("Stream failed")
        with patch.object(type(service), "db", new=db_mock):
            assert service.get_all() == []

    def test_get_by_id_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "t1"
        doc_mock.to_dict.return_value = {"title": "T1", "is_deleted": False}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_by_id("t1")
            assert result is not None

    def test_get_by_id_deleted(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"title": "T1", "is_deleted": True}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            assert service.get_by_id("t1") is None

    def test_get_by_id_not_found(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            assert service.get_by_id("missing") is None

    def test_create_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "new_id"
        db_mock.collection().document.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.create("general", "Test", "2026-01-01")
            assert result["id"] == "new_id"

    def test_create_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            with pytest.raises(Exception, match="Database not available"):
                service.create("general", "Test", "2026-01-01")

    def test_update_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"title": "Updated"}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.update("t1", {"title": "Updated"})
            assert result is not None

    def test_update_not_found(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            assert service.update("missing", {"title": "New"}) is None

    def test_update_exception(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        db_mock.collection().document().update.side_effect = Exception("Update failed")
        with patch.object(type(service), "db", new=db_mock):
            assert service.update("t1", {"title": "New"}) is None

    def test_delete_soft(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            assert service.delete("t1", soft=True) is True

    def test_delete_hard(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            assert service.delete("t1", soft=False) is True

    def test_delete_not_found(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            assert service.delete("missing") is False

    def test_delete_exception(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        db_mock.collection().document().update.side_effect = Exception("Delete failed")
        with patch.object(type(service), "db", new=db_mock):
            assert service.delete("t1") is False

    def test_get_all_for_admin(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "t1"
        doc_mock.to_dict.return_value = {"title": "T1"}
        db_mock.collection().stream.return_value = [doc_mock]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all_for_admin()
            assert len(result) == 1

    def test_get_all_for_admin_exception(self, service):
        db_mock = MagicMock()
        db_mock.collection().stream.side_effect = Exception("Stream failed")
        with patch.object(type(service), "db", new=db_mock):
            assert service.get_all_for_admin() == []


class TestFAQServiceExtended:
    @pytest.fixture
    def service(self):
        with patch("services.faq_service.firestore.client"):
            from services.faq_service import FAQService

            return FAQService()

    def test_get_all_cached(self, service):
        with patch("services.faq_service.get_cached") as mock_cached:
            mock_cached.return_value = [{"id": "cached"}]
            result = service.get_all()
            assert result == [{"id": "cached"}]

    def test_get_all_from_db(self, service):
        with patch("services.faq_service.get_cached", return_value=None):
            db_mock = MagicMock()
            doc_mock = MagicMock()
            doc_mock.id = "f1"
            doc_mock.to_dict.return_value = {"question": "Q1", "is_published": True}
            db_mock.collection().stream.return_value = [doc_mock]
            with patch.object(type(service), "db", new=db_mock):
                with patch("services.faq_service.set_cached"):
                    result = service.get_all()
                    assert len(result) == 1

    def test_get_all_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            with patch("services.faq_service.get_cached", return_value=None):
                assert service.get_all() == []

    def test_get_all_paginated(self, service):
        with patch.object(
            service,
            "_get_all_no_cache",
            return_value=[{"id": "1"}, {"id": "2"}, {"id": "3"}],
        ):
            result, total = service.get_all_paginated(page=1, limit=2)
            assert len(result) == 2
            assert total == 3

    def test_get_by_id_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "f1"
        doc_mock.to_dict.return_value = {"question": "Q1"}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_by_id("f1")
            assert result is not None

    def test_get_by_id_not_found(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            assert service.get_by_id("missing") is None

    def test_get_by_id_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert service.get_by_id("f1") is None

    def test_create_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "new_id"
        db_mock.collection().document.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            with patch("services.faq_service.delete_cached"):
                result = service.create("Q1", "A1", "general", "en", True)
                assert result["id"] == "new_id"

    def test_create_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = service.create("Q", "A", "general")
            assert result is None

    def test_update_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"question": "Updated"}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            with patch("services.faq_service.delete_cached"):
                result = service.update("f1", {"question": "Updated"})
                assert result is not None

    def test_update_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert service.update("f1", {"question": "New"}) is None

    def test_delete_soft(self, service):
        db_mock = MagicMock()
        db_mock.collection().document().delete.return_value = None
        with patch.object(type(service), "db", new=db_mock):
            with patch("services.faq_service.delete_cached"):
                assert service.delete("f1", soft=True) is True

    def test_delete_hard(self, service):
        db_mock = MagicMock()
        db_mock.collection().document().delete.return_value = None
        with patch.object(type(service), "db", new=db_mock):
            with patch("services.faq_service.delete_cached"):
                assert service.delete("f1", soft=False) is True

    def test_delete_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            assert service.delete("missing") is False

    def test_get_all_no_cache_with_filters(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "f1"
        doc_mock.to_dict.return_value = {
            "question": "Q1",
            "is_published": True,
            "category": "general",
            "language": "en",
        }
        db_mock.collection().stream.return_value = [doc_mock]
        with patch.object(type(service), "db", new=db_mock):
            result = service._get_all_no_cache(category="general", language="en")
            assert len(result) == 1
