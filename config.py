import os

# Load .env file first before any config checks
from dotenv import load_dotenv

load_dotenv(override=True)


def _get_required_env(name, fallback=None):
    """Get required environment variable with optional fallback."""
    value = os.environ.get(name, fallback)
    if not value and name not in os.environ:
        if fallback:
            return fallback
        if name in ("SECRET_KEY",):
            return None
    return value


class Config:
    """Base configuration."""

    # Flask settings
    SECRET_KEY = _get_required_env(
        "SECRET_KEY", "dev-only-insecure-key-do-not-use-in-prod"
    )
    DEBUG = False
    PORT = int(os.environ.get("PORT", 5000))
    ENV_FILE = os.environ.get("ENV_FILE", ".env")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # Environment
    ENV = os.environ.get("FLASK_ENV", "production")
    VERSION = "1.0.0"

    # Firebase settings (direct from env)
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY = os.environ.get("FIREBASE_PRIVATE_KEY")
    FIREBASE_PRIVATE_KEY_ID = os.environ.get("FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_CLIENT_EMAIL = os.environ.get("FIREBASE_CLIENT_EMAIL")
    GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")

    # Firebase Frontend Config
    FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET")
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID")

    # Google API Keys
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    # Admin credentials
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
