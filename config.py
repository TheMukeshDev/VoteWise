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
    SECRET_KEY = _get_required_env("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY environment variable is required. Create a .env file or set SECRET_KEY in your environment."
        )

    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    PORT = int(os.environ.get("PORT", 5000))
    ENV_FILE = os.environ.get("ENV_FILE", ".env")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # Environment
    ENV = os.environ.get("FLASK_ENV", "production")
    VERSION = "1.0.0"

    # Firebase settings
    FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID")
    FIREBASE_CLIENT_EMAIL = os.environ.get("FIREBASE_CLIENT_EMAIL")
    FIREBASE_PRIVATE_KEY_ID = os.environ.get("FIREBASE_PRIVATE_KEY_ID")
    GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")

    # Frontend Firebase config (for JS injection)
    FIREBASE_API_KEY = os.environ.get("GEMINI_API_KEY")  # Reuse for Firebase
    FIREBASE_AUTH_DOMAIN = (
        f"{FIREBASE_PROJECT_ID}.firebaseapp.com" if FIREBASE_PROJECT_ID else None
    )
    FIREBASE_STORAGE_BUCKET = (
        f"{FIREBASE_PROJECT_ID}.appspot.com" if FIREBASE_PROJECT_ID else None
    )
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get(
        "FIREBASE_MESSAGING_SENDER_ID", "114550420950547549433"
    )

    # Google API Keys
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GOOGLE_SPEECH_API_KEY = os.environ.get("GOOGLE_SPEECH_API_KEY")
    GOOGLE_TRANSLATE_API_KEY = os.environ.get("GOOGLE_TRANSLATE_API_KEY")

    # Google Calendar OAuth
    GOOGLE_CALENDAR_CLIENT_ID = os.environ.get("GOOGLE_CALENDAR_CLIENT_ID")
    GOOGLE_CALENDAR_CLIENT_SECRET = os.environ.get("GOOGLE_CALENDAR_CLIENT_SECRET")

    # Optional: Firebase Analytics
    FIREBASE_MEASUREMENT_ID = os.environ.get("FIREBASE_MEASUREMENT_ID")

    # Cloud Run settings
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "votewise-ai")
    MIN_INSTANCES = int(os.environ.get("MIN_INSTANCES", 0))
    MAX_INSTANCES = int(os.environ.get("MAX_INSTANCES", 10))

    # Admin credentials (from environment)
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


class DevelopmentConfig(Config):
    """Development configuration with relaxed settings."""

    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    ENV = "production"


class TestConfig(Config):
    """Test configuration with mock values."""

    TESTING = True
    DEBUG = True
    ENV = "testing"
    SECRET_KEY = "test-secret-key-for-testing-only"
    CORS_ORIGINS = "*"
    FIREBASE_CREDENTIALS_PATH = ""
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
