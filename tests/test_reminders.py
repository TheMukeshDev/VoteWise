"""
Tests for reminder routes.
"""

import pytest
import json
from unittest.mock import patch
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

@pytest.fixture(autouse=True)
def mock_jwt_auth():
    with patch("flask_jwt_extended.view_decorators.verify_jwt_in_request"), \
         patch("routes.reminder.get_jwt_identity") as mock_identity:
        mock_identity.return_value = {"user_id": "test-user-id", "role": "voter"}
        yield

class TestReminderRoutes:
    """Test reminder API endpoints."""

    def test_set_reminder_missing_fields(self, client, auth_headers):
        """Test setting reminder with missing fields."""
        response = client.post(
            "/api/reminders",
            data=json.dumps({"title": "Test Event"}),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    def test_set_reminder_invalid_date(self, client, auth_headers):
        """Test setting reminder with invalid date format."""
        response = client.post(
            "/api/reminders",
            data=json.dumps({"title": "Test Event", "reminder_date": "invalid-date"}),
            content_type="application/json",
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_set_reminder_success(self, client, sample_reminder_data, auth_headers):
        """Test successful reminder creation."""
        with (
            patch("services.firestore_service.save_reminder") as mock_save,
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_save.return_value = "reminder-id"
            mock_ics.return_value = "BEGIN:VCALENDAR\nEND:VCALENDAR"

            data_with_ics = {**sample_reminder_data, "generate_ics": True}
            response = client.post(
                "/api/reminders",
                data=json.dumps(data_with_ics),
                content_type="application/json",
                headers=auth_headers,
            )

            assert response.status_code == 200
            mock_save.assert_called_once()
            mock_ics.assert_called_once()

    def test_set_reminder_ics_download(self, client, sample_reminder_data, auth_headers):
        """Test reminder returns ICS file."""
        with (
            patch("services.firestore_service.save_reminder"),
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_ics.return_value = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"

            data_with_ics = {**sample_reminder_data, "generate_ics": True}
            response = client.post(
                "/api/reminders",
                data=json.dumps(data_with_ics),
                content_type="application/json",
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert response.content_type == "text/calendar; charset=utf-8"

    def test_set_reminder_calendar_failure(self, client, sample_reminder_data, auth_headers):
        """Test reminder handles calendar generation failure."""
        with (
            patch("services.firestore_service.save_reminder"),
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_ics.return_value = None

            data_with_ics = {**sample_reminder_data, "generate_ics": True}
            response = client.post(
                "/api/reminders",
                data=json.dumps(data_with_ics),
                content_type="application/json",
                headers=auth_headers,
            )

            assert response.status_code == 400


class TestReminderSecurity:
    """Test reminder security."""

    def test_reminder_user_isolation(self, client, sample_reminder_data, auth_headers):
        """Test users can only access their own reminders."""
        with (
            patch("services.firestore_service.save_reminder") as mock_save,
            patch("services.firestore_service.get_reminders") as mock_get,
        ):
            mock_save.return_value = "reminder-id"
            mock_get.return_value = []

            user1_data = {**sample_reminder_data, "user_id": "user-1"}
            user2_data = {**sample_reminder_data, "user_id": "user-2"}

            client.post(
                "/api/reminders",
                data=json.dumps(user1_data),
                content_type="application/json",
                headers=auth_headers,
            )
            client.post(
                "/api/reminders",
                data=json.dumps(user2_data),
                content_type="application/json",
                headers=auth_headers,
            )

            assert mock_save.call_count == 2

    def test_reminder_xss_prevention(self, client, auth_headers):
        """Test reminder prevents XSS in event name."""
        with (
            patch("services.firestore_service.save_reminder") as mock_save,
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_save.return_value = "reminder-id"
            mock_ics.return_value = "BEGIN:VCALENDAR\nEND:VCALENDAR"

            xss_data = {
                "title": "<script>alert('xss')</script>",
                "reminder_date": "2026-03-15",
                "generate_ics": True,
            }

            response = client.post(
                "/api/reminders",
                data=json.dumps(xss_data),
                content_type="application/json",
                headers=auth_headers,
            )

            assert response.status_code == 200


class TestReminderValidation:
    """Test reminder validation."""

    def test_reminder_date_format_validation(self, client, auth_headers):
        """Test date format validation."""
        valid_dates = ["2026-03-15", "2026-12-25", "2026-01-01"]
        invalid_dates = ["03-15-2026", "2026/03/15", "invalid", ""]

        for date in valid_dates:
            with (
                patch("services.firestore_service.save_reminder"),
                patch("services.calendar_service.create_voting_reminder") as mock_ics,
            ):
                mock_ics.return_value = "BEGIN:VCALENDAR\nEND:VCALENDAR"

                response = client.post(
                    "/api/reminders",
                    data=json.dumps({"title": "Test", "reminder_date": date, "generate_ics": True}),
                    content_type="application/json",
                    headers=auth_headers,
                )
                assert response.status_code == 200, f"Date {date} should be valid"

    def test_reminder_event_name_length(self, client, auth_headers):
        """Test event name length validation."""
        long_name = "A" * 500

        with (
            patch("services.firestore_service.save_reminder"),
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_ics.return_value = "BEGIN:VCALENDAR\nEND:VCALENDAR"

            response = client.post(
                "/api/reminders",
                data=json.dumps({"title": long_name, "reminder_date": "2026-03-15"}),
                content_type="application/json",
                headers=auth_headers,
            )

            assert response.status_code == 400
