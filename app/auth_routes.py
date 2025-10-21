from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from _db import get_db
from validate_docbr import CPF
import re

COLLECTION_USERS = "usuarios_collection"

def normalize_cpf(cpf):
    """Remove pontuação do CPF deixando apenas números"""
    return re.sub(r'\D', '', cpf)

def register_routes_auth(app):
    """Registra todas as rotas de autenticação"""
    
    @app.route("/auth/register", methods=["POST"])
    def register():
        """POST /auth/register - Registrar novo usuário"""
        try:
            data = request.get_json()
            
            # Validar campos obrigatórios
            required_fields = ["name", "email", "password", "phone", "cpf"]
            if not data or not all(field in data for field in required_fields):
                return jsonify({"error": "name, email, password, phone e cpf são obrigatórios"}), 400
            
            # Normalizar e validar CPF
            cpf = normalize_cpf(data.get("cpf"))
            if not CPF().validate(cpf):
                return jsonify({"error": "CPF inválido"}), 400
            
            collection = get_db()
            
            # Verificar se email já existe
            if collection.find_one({"email": data["email"]}):
                return jsonify({"error": "Email já cadastrado"}), 409
            
            # Verificar se CPF já existe (usando CPF normalizado)
            if collection.find_one({"cpf": cpf}):
                return jsonify({"error": "CPF já cadastrado"}), 409
            
            # Criar novo usuário com senha hash
            user_data = {
                "name": data["name"],
                "email": data["email"],
                "password": generate_password_hash(data["password"]),
                "phone": data["phone"],
                "cpf": cpf,
                "faturas": []
            }
            
            result = collection.insert_one(user_data)
            
            user = {
                "_id": str(result.inserted_id),
                "name": data["name"],
                "email": data["email"],
                "phone": data["phone"],
                "cpf": cpf
            }
            
            return jsonify({"message": "Usuário registrado com sucesso", "user": user}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/auth/login", methods=["POST"])
    def login():
        """POST /auth/login - Fazer login"""
        try:
            data = request.get_json()
            
            if not data or not data.get("email") or not data.get("password"):
                return jsonify({"error": "email e password são obrigatórios"}), 400
            
            collection = get_db()
            user = collection.find_one({"email": data["email"]})
            
            if not user or not check_password_hash(user["password"], data["password"]):
                return jsonify({"error": "Email ou senha inválidos"}), 401
            
            # Gerar tokens
            access_token = create_access_token(identity=str(user["_id"]))
            refresh_token = create_refresh_token(identity=str(user["_id"]))
            
            return jsonify({
                "message": "Login realizado com sucesso",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "_id": str(user["_id"]),
                    "name": user["name"],
                    "email": user["email"]
                }
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/auth/refresh", methods=["POST"])
    @jwt_required(refresh=True)
    def refresh():
        """POST /auth/refresh - Renovar access token"""
        try:
            identity = get_jwt_identity()
            access_token = create_access_token(identity=identity)
            return jsonify({"access_token": access_token}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/auth/me", methods=["GET"])
    @jwt_required()
    def get_current_user():
        """GET /auth/me - Obter dados do usuário logado"""
        try:
            user_id = get_jwt_identity()
            obj_id = ObjectId(user_id)
            
            collection = get_db()
            user = collection.find_one({"_id": obj_id})
            
            if not user:
                return jsonify({"error": "Usuário não encontrado"}), 404
            
            return jsonify({
                "_id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone"],
                "cpf": user["cpf"],
                "password": user["password"]
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500