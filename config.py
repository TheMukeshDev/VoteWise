", ", "Configuration management for VoteWise AI.", ", "

import json
import logging
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)


def _get_firebase_admin_json() -> dict[str, Any] | None:
    ", ", "Get Firebase Admin JSON from env or construct from individual fields.", ", "
    firebase_json_str = os.environ.get("FIREBASE_ADMIN_JSON")

    if firebase_json_str:
        try:
            return json.loads(firebase_json_str)
        except json.JSONDecodeError as e:
            logger.error("FIREBASE_ADMIN_JSON is not valid JSON")
            raise ValueError(
                "FIREBASE_ADMIN_JSON environment variable is not valid JSON"
            ) from e

    private_key = os.environ.get("FIREBASE_PRIVATE_KEY", ", ")
    if private_key:
        private_key = private_key.replace("\\n", "\n")

    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
    private_key_id = os.environ.get("FIREBASE_PRIVATE_KEY_ID")

    if project_id and private_key and client_email:
        return {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": client_email,
            "token_uri": "https://oauth2.googleapis.com/token",
        }

    return None


def _resolve_cors_origins(env: str) -> str:
    ", ", "Resolve CORS origins based on environment.", ", "
    cors = os.environ.get("CORS_ORIGINS")
    if env == "production":
        return cors if cors and cors != "*" else ", "
    return cors or "*"


class Config:
    ", ", "Base configuration.", ", "

    SECRET_KEY = os.environ.get("SECRET_KEY") or (
        "dev-only-insecure-key-do-not-use-in-prod"
        if os.environ.get("FLASK_ENV") != "production"
        else None
    )
    if not SECRET_KEY and os.environ.get("FLASK_ENV") == "production":
        raise ValueError("SECRET_KEY environment variable must be set in production")
    DEBUG = False
    TESTING = False
    PORT = int(os.environ.get("PORT", 8080))
    ENV_FILE = os.environ.get("ENV_FILE", ".env")

    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    ENV = FLASK_ENV
    CORS_ORIGINS = _resolve_cors_origins(FLASK_ENV)
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
    REDIS_URL = os.environ.get("REDIS_URL")

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


class DevelopmentConfig(Config):
    ", ", "Development configuration with relaxed settings.", ", "

    DEBUG = True
    ENV = "development"
    FLASK_ENV = "development"
    CORS_ORIGINS = "*"


class ProductionConfig(Config):
    ", ", "Production configuration.", ", "

    DEBUG = False
    ENV = "production"
    FLASK_ENV = "production"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "https://your-domain.com")


class TestConfig(Config):
    ", ", "Test configuration with mock values.", ", "

    TESTING = True
    DEBUG = True
    ENV = "testing"
    FLASK_ENV = "testing"
    SECRET_KEY = "test-secret-key-for-testing-only"
    CORS_ORIGINS = "*"
    GOOGLE_CLOUD_PROJECT = "test-project"
    GEMINI_API_KEY = "test-key"


config_by_name: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestConfig,
    "default": ProductionConfig,
}


def get_config() -> type[Config]:
    ", ", "Get configuration class based on FLASK_ENV.", ", "
    env = os.environ.get("FLASK_ENV", "production")
    return config_by_name.get(env, ProductionConfig)
