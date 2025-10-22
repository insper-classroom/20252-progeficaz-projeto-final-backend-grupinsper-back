from datetime import timedelta
from flask import Flask
from flask_jwt_extended import JWTManager

from app.routes import register_routes_user , register_routes_invoices
from app.auth_routes import register_routes_auth


def create_app():
    app = Flask(__name__)
    
    # Configurar JWT
    app.config['JWT_SECRET_KEY'] = 'sua-chave-secreta-muito-segura-alterar-em-producao'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    jwt = JWTManager(app)
    
    # Registrar rotas
    register_routes_auth(app)
    register_routes_user(app)
    register_routes_invoices(app)
    
    return app

    

