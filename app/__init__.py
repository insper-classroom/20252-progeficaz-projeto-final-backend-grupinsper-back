from flask import Flask
from app.routes import register_routes_user , register_routes_invoices

def create_app(config_object: str = "config.Config") -> Flask:
    """Application factory that initializes the Flask app with configuration and routes."""
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    register_routes_user(app)
    register_routes_invoices(app)
    
    return app
