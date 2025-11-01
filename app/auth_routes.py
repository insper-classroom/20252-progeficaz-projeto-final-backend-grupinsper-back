import re
from flask import jsonify, request, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from _db import get_db
from validate_docbr import CPF

COLLECTION_USERS = "usuarios_collection"

def normalize_cpf(cpf):
    """Remove pontuação do CPF deixando apenas números"""
    return re.sub(r'\D', '', cpf)

def register_routes_auth(app):
    """Registra todas as rotas de autenticação - Richardson Nível 2"""
    # Configurar JWT para aceitar tokens em HEADERS e COOKIES
    # Isso permite: navegadores (cookies), mobile (headers), testes (headers)
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_COOKIE_SECURE"] = False          # True em produção (HTTPS)
    app.config["JWT_COOKIE_SAMESITE"] = "Lax"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False    # True se adicionar CSRF
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/auth/refresh"
    
    @app.route("/auth/login", methods=["POST"])
    def login():
        """POST /auth/login - Fazer login e retornar tokens"""
        try:
            data = request.get_json() or {}

            if not data.get("email") or not data.get("password"):
                return jsonify({"error": "email e password são obrigatórios"}), 400

            collection = get_db()
            user = collection.find_one({"email": data["email"]})

            if not user or not check_password_hash(user["password"], data["password"]):
                return jsonify({"error": "Credenciais inválidas"}), 401

            user_id = str(user["_id"])
            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)

            # Response com tokens no JSON (para frontend/mobile)
            response = make_response(jsonify({
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": 3600,  # segundos
                "user": {
                    "_id": user_id,
                    "name": user["name"],
                    "email": user["email"],
                    "phone": user["phone"],
                    "cpf": user["cpf"]
                }
            }), 200)
            
            # Tokens também em cookies (para navegadores)
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/auth/register", methods=["POST"])
    def register():
        """POST /auth/register - Registrar novo usuário"""
        try:
            data = request.get_json() or {}

            required_fields = ["name", "email", "password", "phone", "cpf"]
            if not all(data.get(field) for field in required_fields):
                return jsonify({
                    "error": "Campos obrigatórios: name, email, password, phone, cpf"
                }), 400

            cpf = normalize_cpf(data["cpf"])
            if not CPF().validate(cpf):
                return jsonify({"error": "CPF inválido"}), 400

            collection = get_db()
            if collection.find_one({"email": data["email"]}):
                return jsonify({"error": "Email já cadastrado"}), 409
            if collection.find_one({"cpf": cpf}):
                return jsonify({"error": "CPF já cadastrado"}), 409

            user_data = {
                "name": data["name"],
                "email": data["email"],
                "password": generate_password_hash(data["password"]),
                "phone": data["phone"],
                "cpf": cpf,
                "faturas": [],
                "created_at": data.get("created_at")
            }

            result = collection.insert_one(user_data)
            user_id = str(result.inserted_id)

            access_token = create_access_token(identity=user_id)
            refresh_token = create_refresh_token(identity=user_id)

            response = make_response(jsonify({
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": 3600,
                "user": {
                    "_id": user_id,
                    "name": user_data["name"],
                    "email": user_data["email"],
                    "phone": user_data["phone"],
                    "cpf": user_data["cpf"]
                }
            }), 201)
            
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/auth/refresh", methods=["POST"])
    @jwt_required(refresh=True)
    def refresh():
        """POST /auth/refresh - Renovar access token usando refresh token"""
        try:
            identity = get_jwt_identity()
            access_token = create_access_token(identity=identity)

            response = make_response(jsonify({
                "success": True,
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 3600
            }), 200)
            
            set_access_cookies(response, access_token)
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    @app.route("/auth/me", methods=["GET"])
    @jwt_required()
    def get_current_user():
        """GET /auth/me - Obter dados do usuário autenticado"""
        try:
            identity = get_jwt_identity()
            collection = get_db()
            user = collection.find_one({"_id": ObjectId(identity)}, {"password": 0})

            if not user:
                return jsonify({"error": "Usuário não encontrado"}), 404

            user["_id"] = str(user["_id"])
            return jsonify({
                "success": True,
                "user": user
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    @app.route("/auth/logout", methods=["POST"])
    @jwt_required()
    def logout():
        """POST /auth/logout - Fazer logout e remover tokens"""
        response = make_response(jsonify({
            "success": True,
            "message": "Logout realizado com sucesso"
        }), 200)
        unset_jwt_cookies(response)
        return response

    @app.route("/auth/validate-token", methods=["POST"])
    @jwt_required()
    def validate_token():
        """POST /auth/validate-token - Validar se o token é válido"""
        try:
            identity = get_jwt_identity()
            return jsonify({
                "success": True,
                "valid": True,
                "user_id": identity
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "valid": False,
                "error": "Token inválido ou expirado"
            }), 401