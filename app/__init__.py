from flask import Flask

from .routes import register_routes


def create_app(config_object: str = "config.Config") -> Flask:
    """Application factory that initializes the Flask app with configuration and routes."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    register_routes(app)

    return app
