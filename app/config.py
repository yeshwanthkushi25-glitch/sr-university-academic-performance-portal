"""
SR University Academic Performance Portal - Configuration Module
Supports Development, Testing, and Production environments.
"""

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    """Base configuration with shared application parameters."""
    SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("AGY_SECRET_KEY", "sr-university-portal-secret-key-2026-prod"))
    BASE_DIR = BASE_DIR
    DB_PATH = os.getenv("DATABASE_URL", os.path.join(BASE_DIR, "academic_portal.db"))
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    STUDENTS_PER_PAGE = 20
    UNIVERSITY_NAME = "SR University"
    UNIVERSITY_DOMAIN = "sruniv.edu"


class DevelopmentConfig(Config):
    """Development environment configuration with debugging enabled."""
    DEBUG = True
    TESTING = False
    ENV = "development"


class TestingConfig(Config):
    """Testing environment configuration with isolated test database and CSRF disabled."""
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    DB_PATH = os.getenv("TEST_DATABASE_URL", os.path.join(BASE_DIR, "test_academic_portal.db"))
    ENV = "testing"


class ProductionConfig(Config):
    """Production environment configuration with hardened settings."""
    DEBUG = False
    TESTING = False
    ENV = "production"

    @classmethod
    def init_app(cls, app):
        secret = os.getenv("SECRET_KEY") or os.getenv("AGY_SECRET_KEY")
        if not secret:
            import warnings
            warnings.warn("SECRET_KEY environment variable is not explicitly set in Production!", RuntimeWarning)


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name=None):
    """Retrieves configuration class by name, environment variable, or default."""
    if not config_name:
        config_name = os.getenv("FLASK_CONFIG") or os.getenv("FLASK_ENV", "development").lower()
    return config_by_name.get(config_name, DevelopmentConfig)
