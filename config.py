"""
Environment-specific configuration for SmartHarvest.

This keeps passwords and API keys out of the actual code, making it safer.

Environments:
- DevelopmentConfig : local development (debug on)
- TestingConfig     : pytest (in-memory / test DB)
- ProductionConfig  : Render / live (debug off)
"""

import os

# Load .env file if python-dotenv is installed
# (safe to skip if it's not available)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class BaseConfig:
    """Shared settings across all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-key")

    # MySQL connection string
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost/smartharvest"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    # Use a separate test database so tests never touch live data
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "mysql+pymysql://root:root@localhost/smartharvest_test"
    )


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"
    # We don't fail loudly here in case this is imported without a key yet
    # (The app will fail on startup if SECRET_KEY is truly missing)


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env: str | None = None):
    """Return the config class for the given environment name."""
    env = env or os.getenv("FLASK_ENV", "development")
    return CONFIG_MAP.get(env, DevelopmentConfig)
