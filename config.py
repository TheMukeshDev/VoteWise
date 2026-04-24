import os
import json
import logging

from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)


def _get_required_env(name, fallback=None):
    """Get required environment variable with optional fallback."""
    value = os.environ.get(name, fallback)
    if not value and name not in os.environ:
        if fallback:
            return fallback
        if name in ("SECRET_KEY",):
            return None
    return value


def _get_firebase_admin_json():
    """Get Firebase Admin JSON from env variable (from Secret Manager on Cloud Run)."""
    firebase_json_str = os.environ.get("FIREBASE_ADMIN_JSON")
    if not firebase_json_str:
        return None
    try:
        return json.loads(firebase_json_str)
    except json.JSONDecodeError as e:
        logger.error("FIREBASE_ADMIN_JSON is not valid JSON")
        raise ValueError(
            "FIREBASE_ADMIN_JSON environment variable is not valid JSON"
        ) from e


class Config:
    """Base configuration."""

    SECRET_KEY = _get_required_env(
        "SECRET_KEY", "dev-only-insecure-key-do-not-use-in-prod"
    )
    DEBUG = False
    PORT = int(os.environ.get("PORT", 8080))
    ENV_FILE = os.environ.get("ENV_FILE", ".env")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    ENV = os.environ.get("FLASK_ENV", "production")
    VERSION = "1.0.0"

    FIREBASE_ADMIN_JSON = _get_firebase_admin_json()
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
    GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")

    FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID")

    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


class DevelopmentConfig(Config):
    """Development configuration with relaxed settings."""

    DEBUG = True
    ENV = "development"
    CORS_ORIGINS = "*"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    ENV = "production"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "https://your-domain.com")


class TestConfig(Config):
    """Test configuration with mock values."""

    TESTING = True
    DEBUG = True
    ENV = "testing"
    SECRET_KEY = "test-secret-key-for-testing-only"
    CORS_ORIGINS = "*"
    GOOGLE_CLOUD_PROJECT = "test-project"
    GEMINI_API_KEY = "test-key"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestConfig,
    "default": ProductionConfig,
}


def get_config():
    """Get configuration based on FLASK_ENV or default to production."""
    env = os.environ.get("FLASK_ENV", "production")
    return config_by_name.get(env, ProductionConfig)
