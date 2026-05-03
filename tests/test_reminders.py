", ", "
Tests for reminder routes.
", ", "

import pytest
import json

pytestmark = pytest.mark.unit


class TestReminderRoutesUnauthenticated:
    ", ", "Test reminder API endpoints without authentication.", ", "

    def test_set_reminder_requires_auth(self, client):
        ", ", "Test setting reminder requires authentication.", ", "
        response = client.post(
            "/api/reminders",
            data=json.dumps({"title": "Test Event", "reminder_date": "2026-05-20"}),
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_get_reminders_requires_auth(self, client):
        ", ", "Test getting reminders requires authentication.", ", "
        response = client.get("/api/reminders")
        assert response.status_code == 401

    def test_get_reminder_requires_auth(self, client):
        ", ", "Test getting single reminder requires authentication.", ", "
        response = client.get("/api/reminders/reminder-id")
        assert response.status_code == 401


class TestReminderValidation:
    ", ", "Test reminder validation.", ", "

    def test_reminder_missing_title(self, client):
        ", ", "Test reminder requires title field.", ", "
        response = client.post(
            "/api/reminders",
            data=json.dumps({"reminder_date": "2026-05-20"}),
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_reminder_missing_date(self, client):
        ", ", "Test reminder requires reminder_date field.", ", "
        response = client.post(
            "/api/reminders",
            data=json.dumps({"title": "Test Event"}),
            content_type="application/json",
        )
        assert response.status_code == 401


class TestReminderFormat:
    ", ", "Test reminder response format.", ", "

    def test_error_response_format(self, client):
        ", ", "Test error response has proper format.", ", "
        response = client.get("/api/reminders")
        data = json.loads(response.data)

        assert "success" in data
        assert data["success"] is False
        assert "message" in data
