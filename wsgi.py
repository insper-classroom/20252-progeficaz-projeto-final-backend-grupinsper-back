from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

load_dotenv() 

from app.routes import register_routes_user, register_routes_invoices
from app.auth_routes import register_routes_auth 
from _db import get_db

app = Flask(__name__)

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
CORS(app, supports_credentials=True, resources={r"/*": {"origins": FRONTEND_ORIGIN}})

# CONFIGURAÇÃO DO JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "seu-segredo-de-teste") 
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_COOKIE_SECURE"] = False # False para localhost
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False 
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_REFRESH_COOKIE_PATH"] = "/auth/refresh"
# Nomes explícitos dos cookies, para compatibilidade com o frontend
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"
jwt = JWTManager(app)

# REGISTRO DAS ROTAS
register_routes_auth(app)     
register_routes_user(app)      
register_routes_invoices(app) 

if __name__ == "__main__":
    print("Iniciando Flask app...")
    try:
        get_db()
        print("Conexão com o banco de dados OK.")
    except Exception as e:
        print(f"ERRO AO CONECTAR COM O BANCO: {e}")

    app.run(debug=True, port=5000)