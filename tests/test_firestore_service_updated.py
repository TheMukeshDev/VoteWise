"""
Tests for updated firestore_service.py with improved logging and type hints.
"""

from unittest.mock import MagicMock, patch


class TestSaveUserUpdated:
    """Test save_user with improved logging."""

    def test_save_user_success(self):
        """Test successful user save."""
        with patch("services.firestore_service.get_firestore_client") as mock_get_db:
            db_mock = MagicMock()
            mock_get_db.return_value = db_mock

            from services.firestore_service import save_user

            result = save_user("user1", {"name": "Test"})

            assert result == "user1"
            db_mock.collection().document().set.assert_called_once()

    def test_save_user_no_db(self):
        """Test save_user with no database."""
        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            from services.firestore_service import save_user

            result = save_user("user1", {"name": "Test"})
            assert result is None

    def test_save_user_exception(self):
        """Test save_user with database exception."""
        with patch("services.firestore_service.get_firestore_client") as mock_get_db:
            db_mock = MagicMock()
            db_mock.collection().document().set.side_effect = RuntimeError("DB Error")
            mock_get_db.return_value = db_mock

            from services.firestore_service import save_user

            result = save_user("user1", {"name": "Test"})
            assert result is None


class TestGetUserUpdated:
    """Test get_user with improved logging."""

    def test_get_user_success(self):
        """Test successful user retrieval."""
        with patch("services.firestore_service.get_firestore_client") as mock_get_db:
            db_mock = MagicMock()
            doc_mock = MagicMock()
            doc_mock.exists = True
            doc_mock.to_dict.return_value = {"name": "Test"}
            db_mock.collection().document().get.return_value = doc_mock
            mock_get_db.return_value = db_mock

            from services.firestore_service import get_user

            result = get_user("user1")

            assert result == {"name": "Test"}

    def test_get_user_not_found(self):
        """Test user not found."""
        with patch("services.firestore_service.get_firestore_client") as mock_get_db:
            db_mock = MagicMock()
            doc_mock = MagicMock()
            doc_mock.exists = False
            db_mock.collection().document().get.return_value = doc_mock
            mock_get_db.return_value = db_mock

            from services.firestore_service import get_user

            result = get_user("user1")
            assert result is None

    def test_get_user_no_db(self):
        """Test get_user with no database."""
        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            from services.firestore_service import get_user

            result = get_user("user1")
            assert result is None


class TestCreateOrUpdateUserProfileUpdated:
    """Test create_or_update_user_profile with fixed datetime.utcnow()."""

    def test_create_new_profile(self):
        """Test creating a new user profile."""
        with patch("services.firestore_service.get_firestore_client") as mock_get_db:
            db_mock = MagicMock()
            doc_mock_new = MagicMock()
            doc_mock_new.exists = False
            doc_mock_existing = MagicMock()
            doc_mock_existing.exists = True
            doc_mock_existing.id = "user1"
            doc_mock_existing.to_dict.return_value = {
                "firebase_uid": "user1",
                "email": "test@example.com",
                "name": "Test User",
            }
            db_mock.collection().document().get.side_effect = [
                doc_mock_new,
                doc_mock_existing,
            ]
            mock_get_db.return_value = db_mock

            from services.firestore_service import \
                create_or_update_user_profile

            result = create_or_update_user_profile(
                firebase_uid="user1",
                email="test@example.com",
                name="Test User",
            )

            assert result is not None

    def test_update_existing_profile(self):
        """Test updating an existing user profile."""
        with patch("services.firestore_service.get_firestore_client") as mock_get_db:
            db_mock = MagicMock()
            doc_mock = MagicMock()
            doc_mock.exists = True
            doc_mock.to_dict.return_value = {
                "name": "Old Name",
                "email": "test@example.com",
            }
            db_mock.collection().document().get.return_value = doc_mock
            mock_get_db.return_value = db_mock

            from services.firestore_service import \
                create_or_update_user_profile

            result = create_or_update_user_profile(
                firebase_uid="user1",
                email="test@example.com",
                name="New Name",
            )

            assert result is not None

    def test_no_db(self):
        """Test with no database available."""
        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            from services.firestore_service import \
                create_or_update_user_profile

            result = create_or_update_user_profile(
                firebase_uid="user1", email="test@example.com"
            )
            assert result is None


class TestReminderOperationsUpdated:
    """Test reminder operations with improved logging."""

    def test_save_reminder_success(self):
        """Test successful reminder save."""
        with patch("services.firestore_service.get_firestore_client") as mock_get_db:
            db_mock = MagicMock()
            doc_ref_mock = MagicMock()
            doc_ref_mock.id = "reminder1"
            db_mock.collection().document().collection().document.return_value = (
                doc_ref_mock
            )
            mock_get_db.return_value = db_mock

            from services.firestore_service import save_reminder

            result = save_reminder("user1", {"title": "Test"})

            assert result == "reminder1"

    def test_save_reminder_no_db(self):
        """Test save_reminder with no database."""
        with patch(
            "services.firestore_service.get_firestore_client", return_value=None
        ):
            from services.firestore_service import save_reminder

            result = save_reminder("user1", {"title": "Test"})
            assert result is None


class TestBookmarkOperationsUpdated:
    """Test bookmark operations with improved logging."""

    def test_save_bookmark_success(self):
        """Test successful bookmark save."""
        with patch("services.firestore_service.get_firestore_client") as mock_get_db:
            db_mock = MagicMock()
            doc_ref_mock = MagicMock()
            doc_ref_mock.id = "bookmark1"
            db_mock.collection().document().collection().document.return_value = (
                doc_ref_mock
            )
            mock_get_db.return_value = db_mock

            from services.firestore_service import save_bookmark

            result = save_bookmark("user1", {"resource_type": "faq"})

            assert result == "bookmark1"

    def test_get_bookmarks_success(self):
        """Test successful bookmarks retrieval."""
        with patch("services.firestore_service.get_firestore_client") as mock_get_db:
            db_mock = MagicMock()
            doc_mock = MagicMock()
            doc_mock.id = "bm1"
            doc_mock.to_dict.return_value = {"resource_type": "faq"}
            db_mock.collection().document().collection().stream.return_value = [
                doc_mock
            ]
            mock_get_db.return_value = db_mock

            from services.firestore_service import get_bookmarks

            result = get_bookmarks("user1")

            assert len(result) == 1
            assert result[0]["id"] == "bm1"


class TestDatetimeFix:
    """Test that datetime.utcnow() is fixed."""

    def test_datetime_timezone_utc_used(self):
        """Verify that datetime.now(timezone.utc) is used instead of datetime.utcnow()."""
        import inspect

        from services import firestore_service

        source = inspect.getsource(firestore_service.create_or_update_user_profile)

        # Verify the old deprecated method is not used
        assert "datetime.utcnow()" not in source
        # Verify the new method is used
        assert "datetime.now(timezone.utc)" in source
