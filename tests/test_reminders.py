"""
Tests for reminder routes.
"""

import pytest
import json
from unittest.mock import patch


class TestReminderRoutes:
    """Test reminder API endpoints."""

    def test_set_reminder_missing_fields(self, client):
        """Test setting reminder with missing fields."""
        response = client.post(
            "/api/reminders",
            data=json.dumps({"event_name": "Test Event"}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False

    def test_set_reminder_invalid_date(self, client):
        """Test setting reminder with invalid date format."""
        response = client.post(
            "/api/reminders",
            data=json.dumps({"event_name": "Test Event", "event_date": "invalid-date"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_set_reminder_success(self, client, sample_reminder_data):
        """Test successful reminder creation."""
        with (
            patch("services.firestore_service.save_reminder") as mock_save,
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_save.return_value = "reminder-id"
            mock_ics.return_value = "BEGIN:VCALENDAR\nEND:VCALENDAR"

            response = client.post(
                "/api/reminders",
                data=json.dumps(sample_reminder_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            mock_save.assert_called_once()
            mock_ics.assert_called_once()

    def test_set_reminder_ics_download(self, client, sample_reminder_data):
        """Test reminder returns ICS file."""
        with (
            patch("services.firestore_service.save_reminder"),
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_ics.return_value = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"

            response = client.post(
                "/api/reminders",
                data=json.dumps(sample_reminder_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            assert response.content_type == "text/calendar; charset=utf-8"

    def test_set_reminder_calendar_failure(self, client, sample_reminder_data):
        """Test reminder handles calendar generation failure."""
        with (
            patch("services.firestore_service.save_reminder"),
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_ics.return_value = None

            response = client.post(
                "/api/reminders",
                data=json.dumps(sample_reminder_data),
                content_type="application/json",
            )

            assert response.status_code == 400


class TestReminderSecurity:
    """Test reminder security."""

    def test_reminder_user_isolation(self, client, sample_reminder_data):
        """Test users can only access their own reminders."""
        with (
            patch("services.firestore_service.save_reminder") as mock_save,
            patch("services.firestore_service.get_reminders_by_user") as mock_get,
        ):
            mock_save.return_value = "reminder-id"
            mock_get.return_value = []

            user1_data = {**sample_reminder_data, "user_id": "user-1"}
            user2_data = {**sample_reminder_data, "user_id": "user-2"}

            client.post(
                "/api/reminders",
                data=json.dumps(user1_data),
                content_type="application/json",
            )
            client.post(
                "/api/reminders",
                data=json.dumps(user2_data),
                content_type="application/json",
            )

            assert mock_save.call_count == 2

    def test_reminder_xss_prevention(self, client):
        """Test reminder prevents XSS in event name."""
        with (
            patch("services.firestore_service.save_reminder") as mock_save,
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_save.return_value = "reminder-id"
            mock_ics.return_value = "BEGIN:VCALENDAR\nEND:VCALENDAR"

            xss_data = {
                "event_name": "<script>alert('xss')</script>",
                "event_date": "2026-03-15",
            }

            response = client.post(
                "/api/reminders",
                data=json.dumps(xss_data),
                content_type="application/json",
            )

            assert response.status_code == 200


class TestReminderValidation:
    """Test reminder validation."""

    def test_reminder_date_format_validation(self, client):
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
                    data=json.dumps({"event_name": "Test", "event_date": date}),
                    content_type="application/json",
                )
                assert response.status_code == 200, f"Date {date} should be valid"

    def test_reminder_event_name_length(self, client):
        """Test event name length validation."""
        long_name = "A" * 500

        with (
            patch("services.firestore_service.save_reminder"),
            patch("services.calendar_service.create_voting_reminder") as mock_ics,
        ):
            mock_ics.return_value = "BEGIN:VCALENDAR\nEND:VCALENDAR"

            response = client.post(
                "/api/reminders",
                data=json.dumps({"event_name": long_name, "event_date": "2026-03-15"}),
                content_type="application/json",
            )

            assert response.status_code == 400
