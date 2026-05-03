", ", "Comprehensive tests to improve coverage for announcement, polling_guidance, and election_process services.", ", "

import pytest
from unittest.mock import MagicMock, patch


class TestAnnouncementServiceExtended:
    @pytest.fixture
    def service(self):
        from services.announcement_service import AnnouncementService

        return AnnouncementService()

    def test_get_collection_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = service._get_collection()
            assert result is None

    def test_get_all_empty_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = service.get_all()
            assert result == []

    def test_get_all_with_filters(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "a1"
        doc_mock.to_dict.return_value = {
            "title": "Test",
            "is_active": True,
            "region": "north",
            "priority": "high",
        }
        db_mock.collection().where().where().where().where().stream.return_value = [
            doc_mock
        ]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all(region="north", priority="high")
            assert len(result) == 1

    def test_get_all_fallback_path(self, service):
        db_mock = MagicMock()
        db_mock.collection().where().where().stream.side_effect = Exception(
            "Query failed"
        )
        doc_mock = MagicMock()
        doc_mock.id = "a1"
        doc_mock.to_dict.return_value = {
            "title": "Test",
            "is_active": True,
            "is_deleted": False,
        }
        db_mock.collection().stream.return_value = [doc_mock]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all()
            assert len(result) == 1

    def test_get_all_fallback_filters_deleted(self, service):
        db_mock = MagicMock()
        db_mock.collection().where().where().stream.side_effect = Exception(
            "Query failed"
        )
        doc1 = MagicMock()
        doc1.id = "a1"
        doc1.to_dict.return_value = {
            "title": "Active",
            "is_active": True,
            "is_deleted": False,
        }
        doc2 = MagicMock()
        doc2.id = "a2"
        doc2.to_dict.return_value = {
            "title": "Deleted",
            "is_active": True,
            "is_deleted": True,
        }
        db_mock.collection().stream.return_value = [doc1, doc2]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all()
            assert len(result) == 1

    def test_get_all_fallback_double_exception(self, service):
        db_mock = MagicMock()
        db_mock.collection().where().where().stream.side_effect = Exception(
            "Query failed"
        )
        db_mock.collection().stream.side_effect = Exception("Stream failed")
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all()
            assert result == []

    def test_get_by_id_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "a1"
        doc_mock.to_dict.return_value = {"title": "Test", "is_deleted": False}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_by_id("a1")
            assert result is not None

    def test_get_by_id_not_found(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_by_id("missing")
            assert result is None

    def test_get_by_id_soft_deleted(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"title": "Test", "is_deleted": True}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_by_id("deleted")
            assert result is None

    def test_get_by_id_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = service.get_by_id("a1")
            assert result is None

    def test_get_by_id_exception(self, service):
        db_mock = MagicMock()
        db_mock.collection().document().get.side_effect = Exception("DB error")
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_by_id("a1")
            assert result is None

    def test_create_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "new_id"
        db_mock.collection().document.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.create("Title", "Message", "high", "north", True)
            assert result["id"] == "new_id"
            doc_mock.set.assert_called_once()

    def test_create_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            with pytest.raises(Exception, match="Database not available"):
                service.create("Title", "Message")

    def test_update_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"title": "Updated"}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.update("a1", {"title": "Updated"})
            assert result is not None

    def test_update_not_found(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.update("missing", {"title": "New"})
            assert result is None

    def test_update_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = service.update("a1", {"title": "New"})
            assert result is None

    def test_update_exception(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        db_mock.collection().document().update.side_effect = Exception("Update failed")
        with patch.object(type(service), "db", new=db_mock):
            result = service.update("a1", {"title": "New"})
            assert result is None

    def test_delete_soft(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.delete("a1", soft=True)
            assert result is True

    def test_delete_hard(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.delete("a1", soft=False)
            assert result is True

    def test_delete_not_found(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.delete("missing")
            assert result is False

    def test_delete_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = service.delete("a1")
            assert result is False

    def test_delete_exception(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        db_mock.collection().document().update.side_effect = Exception("Delete failed")
        with patch.object(type(service), "db", new=db_mock):
            result = service.delete("a1")
            assert result is False

    def test_get_all_for_admin_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "a1"
        doc_mock.to_dict.return_value = {"title": "Test", "is_active": False}
        db_mock.collection().stream.return_value = [doc_mock]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all_for_admin()
            assert len(result) == 1

    def test_get_all_for_admin_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = service.get_all_for_admin()
            assert result == []

    def test_get_all_for_admin_exception(self, service):
        db_mock = MagicMock()
        db_mock.collection().stream.side_effect = Exception("Stream failed")
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all_for_admin()
            assert result == []


class TestPollingGuidanceServiceExtended:
    @pytest.fixture
    def service(self):
        from services.polling_guidance_service import PollingGuidanceService

        return PollingGuidanceService()

    def test_get_all_empty(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            result = service.get_all()
            assert result == []

    def test_get_all_with_region_filter(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "g1"
        doc_mock.to_dict.return_value = {"title": "Test", "region": "north"}
        db_mock.collection().where().where().where().stream.return_value = [doc_mock]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all(region="north")
            assert len(result) == 1

    def test_get_all_fallback(self, service):
        db_mock = MagicMock()
        db_mock.collection().where().where().stream.side_effect = Exception(
            "Query failed"
        )
        doc_mock = MagicMock()
        doc_mock.id = "g1"
        doc_mock.to_dict.return_value = {
            "title": "Test",
            "is_active": True,
            "is_deleted": False,
        }
        db_mock.collection().stream.return_value = [doc_mock]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all()
            assert len(result) == 1

    def test_get_by_id_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.id = "g1"
        doc_mock.to_dict.return_value = {"title": "Test", "is_deleted": False}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_by_id("g1")
            assert result is not None

    def test_get_by_id_deleted(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"title": "Test", "is_deleted": True}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_by_id("deleted")
            assert result is None

    def test_create_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "new_id"
        db_mock.collection().document.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.create(
                "north", "Title", "Description", [{"url": "http://example.com"}], True
            )
            assert result["id"] == "new_id"

    def test_create_no_help_links(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "new_id"
        db_mock.collection().document.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.create("north", "Title", "Description")
            assert result["help_links"] == []

    def test_update_success(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"title": "Updated"}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.update("g1", {"title": "Updated"})
            assert result is not None

    def test_delete_soft(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.delete("g1", soft=True)
            assert result is True

    def test_delete_hard(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.delete("g1", soft=False)
            assert result is True

    def test_get_all_for_admin(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.id = "g1"
        doc_mock.to_dict.return_value = {"title": "Test"}
        db_mock.collection().stream.return_value = [doc_mock]
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all_for_admin()
            assert len(result) == 1


class TestElectionProcessServiceExtended:
    @pytest.fixture
    def service(self):
        from services.election_process_service import ElectionProcessService

        return ElectionProcessService()

    def test_get_all_fallback_double_exception(self, service):
        db_mock = MagicMock()
        db_mock.collection().where().where().stream.side_effect = Exception(
            "Query failed"
        )
        db_mock.collection().stream.side_effect = Exception("Stream failed")
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all()
            assert result == []

    def test_get_by_id_deleted(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        doc_mock.to_dict.return_value = {"title": "Test", "is_deleted": True}
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_by_id("deleted")
            assert result is None

    def test_create_no_db(self, service):
        with patch.object(
            type(service), "db", new_callable=lambda: property(lambda self: None)
        ):
            with pytest.raises(Exception, match="Database not available"):
                service.create("Title", "Intro", [])

    def test_update_not_found(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.update("missing", {"title": "New"})
            assert result is None

    def test_delete_not_found(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = False
        db_mock.collection().document().get.return_value = doc_mock
        with patch.object(type(service), "db", new=db_mock):
            result = service.delete("missing")
            assert result is False

    def test_delete_exception(self, service):
        db_mock = MagicMock()
        doc_mock = MagicMock()
        doc_mock.exists = True
        db_mock.collection().document().get.return_value = doc_mock
        db_mock.collection().document().update.side_effect = Exception("Delete failed")
        with patch.object(type(service), "db", new=db_mock):
            result = service.delete("p1")
            assert result is False

    def test_get_all_for_admin_exception(self, service):
        db_mock = MagicMock()
        db_mock.collection().stream.side_effect = Exception("Stream failed")
        with patch.object(type(service), "db", new=db_mock):
            result = service.get_all_for_admin()
            assert result == []
