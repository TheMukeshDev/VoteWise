"""
Pytest configuration and fixtures for VoteWise AI tests.
"""

import pytest
import os
from unittest.mock import MagicMock, patch

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DEBUG"] = "True"
os.environ["FIREBASE_CREDENTIALS_PATH"] = ""
os.environ["GEMINI_API_KEY"] = "test-key"


@pytest.fixture
def app():
    """Create application for testing."""
    from app import create_app
    from config import TestConfig

    application = create_app(TestConfig)
    application.config.update(
        {
            "TESTING": True,
        }
    )

    yield application


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {
        "Authorization": "Bearer test-access-token",
        "Content-Type": "application/json",
    }


@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase authentication."""
    with patch("services.auth_service.firebase_admin") as mock:
        mock.initialize_app.return_value = None
        mock.auth.verify_id_token.return_value = {
            "uid": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
        }
        yield mock


@pytest.fixture
def mock_firestore():
    """Mock Firestore database."""
    with patch("services.auth_service.db") as mock:
        mock.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
            "user_id": "test-user-id",
            "email": "test@example.com",
            "role": "voter",
        }
        yield mock


@pytest.fixture
def sample_user_data():
    """Sample user data for tests."""
    return {
        "user_id": "test-user-id",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "voter",
        "state": "Delhi",
        "language_preference": "en",
    }


@pytest.fixture
def sample_faq_data():
    """Sample FAQ data for tests."""
    return {
        "question": "Who is eligible to vote?",
        "answer": "Any Indian citizen aged 18 years or above.",
        "category": "eligibility",
        "language": "en",
    }


@pytest.fixture
def sample_reminder_data():
    """Sample reminder data for tests."""
    return {
        "event_name": "Voter Registration Deadline",
        "event_date": "2026-03-15",
        "description": "Last date to register for elections",
    }
