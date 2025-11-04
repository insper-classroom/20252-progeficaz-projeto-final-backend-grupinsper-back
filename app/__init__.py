from datetime import timedelta
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

from app.routes import register_routes_user , register_routes_invoices
from app.auth_routes import register_routes_auth


def create_app():
    app = Flask(__name__)
    
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": frontend_origin}})
    
    # Configurar JWT
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "sua-chave-secreta-muito-segura-alterar-em-producao")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    # Cookies JWT: nomes e flags padrão (em produção, defina Secure=True)
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_COOKIE_SECURE"] = os.getenv("JWT_COOKIE_SECURE", "False").lower() == "true"
    app.config["JWT_COOKIE_SAMESITE"] = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/auth/refresh"
    app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
    app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"
    
    jwt = JWTManager(app)
    
    # Registrar rotas
    register_routes_auth(app)
    register_routes_user(app)
    register_routes_invoices(app)
    
    return app

    

