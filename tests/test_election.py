"""
Tests for election routes.
"""

import json

import pytest

pytestmark = pytest.mark.unit


class TestElectionRoutes:
    """Test election API endpoints."""

    def test_get_election_process(self, client):
        """Test getting election process."""
        response = client.get("/api/election/process")
        assert response.status_code == 200

    def test_get_election_timeline(self, client):
        """Test getting election timeline."""
        response = client.get("/api/election/timeline")
        assert response.status_code == 200

    def test_get_election_faqs(self, client):
        """Test getting election FAQs."""
        response = client.get("/api/election/faqs")
        assert response.status_code == 200

    def test_response_format(self, client):
        """Test response has proper format."""
        response = client.get("/api/election/process")
        data = json.loads(response.data)
        assert "success" in data


class TestElectionSecurity:
    """Test election security."""

    def test_election_no_sensitive_data(self, client):
        """Test election endpoints don't leak sensitive data."""
        response = client.get("/api/election/process")
        data = json.loads(response.data)

        # Should not contain sensitive fields
        for key in data.keys():
            assert "password" not in key.lower()
            assert "secret" not in key.lower()
            assert "key" not in key.lower()
