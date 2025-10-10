"""Default configuration module for the Flask application."""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration with sane defaults for all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Configuration tuned for local development."""

    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    """Configuration tuned for production deployments."""

    DEBUG = False
    ENV = "production"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": Config,
}

