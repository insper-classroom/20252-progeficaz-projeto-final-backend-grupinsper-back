import asyncio
from datetime import datetime
from io import BytesIO
import os
import re

from bson import ObjectId
from bson.errors import InvalidId
from validate_docbr import CPF
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from pymongo import ReturnDocument

from app.controller.utils_formatar_extrato import formatar_extratos
from _db import get_db , get_db_connection

COLLECTION_USERS = os.getenv("COLLECTION_USERS")
COLLECTION_FATURAS = os.getenv("COLLECTION_FATURAS")


def register_routes_user(app):
    """Registra todas as rotas de usuários - Richardson Nível 2"""
    
    # Criar índices na primeira inicialização
    @app.before_request
    def create_indexes():
        collection = get_db()
        collection.create_index("email", unique=True)
    

    @app.route("/usuarios", methods=["GET"])
    @jwt_required()
    def list_users():
        """GET /usuarios - Listar apenas dados do usuário autenticado"""
        try:
            user_id = get_jwt_identity()  # ← Pega ID do token
            collection = get_db()
            
            # Busca apenas o usuário logado
            user = collection.find_one(
                {"_id": ObjectId(user_id)}, 
                {"password": 0}  # Nunca retornar senha
            )
            
            if not user:
                return jsonify({
                    "success": False,
                    "message": "Usuário não encontrado"
                }), 404
            
            user["_id"] = str(user["_id"])
            return jsonify({
                "success": True,
                "user": user
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500


    @app.route("/usuarios", methods=["POST"])
    @jwt_required()
    def create_user():
        """POST /users - Criar novo usuário"""
        try:
            data = request.get_json() or {}
            required_fields = ["name", "email", "phone", "cpf", "password"]
            if not all(data.get(field) for field in required_fields):
                return jsonify({"error": "name, email, phone, cpf e password são obrigatórios"}), 400

            cpf = re.sub(r"\D", "", data["cpf"])
            if not CPF().validate(cpf):
                return jsonify({"error": "CPF inválido"}), 400

            collection = get_db()
            if collection.find_one({"email": data["email"]}):
                return jsonify({"error": "Email já cadastrado"}), 409
            if collection.find_one({"cpf": cpf}):
                return jsonify({"error": "CPF já cadastrado"}), 409

            result = collection.insert_one({
                "name": data["name"],
                "email": data["email"],
                "cpf": cpf,
                "phone": data["phone"],
                "password": generate_password_hash(data["password"]),
                "faturas": []
            })

            user = {
                "_id": str(result.inserted_id),
                "name": data["name"],
                "email": data["email"],
                "cpf": cpf,
                "phone": data["phone"],
                "faturas": []
            }
            return jsonify(user), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route("/usuarios/<user_id>", methods=["GET"])
    @jwt_required()
    def get_user(user_id):
        """GET /usuarios/<user_id> - Obter usuário (apenas se for ele mesmo)"""
        try:
            current_user_id = get_jwt_identity()
            requested_user_id = user_id
            
            # ← VERIFICAÇÃO: Usuário só pode ver seus próprios dados
            if current_user_id != requested_user_id:
                return jsonify({
                    "success": False,
                    "message": "Acesso negado. Você só pode ver seus próprios dados"
                }), 403
            
            obj_id = ObjectId(user_id)
        except InvalidId:
            return jsonify({
                "success": False,
                "message": "ID inválido"
            }), 400
        
        try:
            collection = get_db()
            user = collection.find_one({"_id": obj_id}, {"password": 0})
            
            if not user:
                return jsonify({
                    "success": False,
                    "message": "Usuário não encontrado"
                }), 404
            
            user["_id"] = str(user["_id"])
            return jsonify({
                "success": True,
                "user": user
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500


    @app.route("/usuarios/<user_id>", methods=["PUT"])
    @jwt_required()
    def update_user(user_id):
        """PUT /usuarios/<user_id> - Atualizar usuário (apenas si mesmo)"""
        try:
            current_user_id = get_jwt_identity()
            
            # ← VERIFICAÇÃO: Usuário só pode atualizar seus próprios dados
            if current_user_id != user_id:
                return jsonify({
                    "success": False,
                    "message": "Acesso negado. Você só pode atualizar seus próprios dados"
                }), 403
            
            obj_id = ObjectId(user_id)
        except InvalidId:
            return jsonify({
                "success": False,
                "message": "ID inválido"
            }), 400
        
        try:
            data = request.get_json() 
            
            if not data:
                return jsonify({
                    "success": False,
                    "message": "Dados são obrigatórios"
                }), 400
            
            collection = get_db()

            if "cpf" in data:
                novo_cpf = re.sub(r"\D", "", data["cpf"])
                if not CPF().validate(novo_cpf):
                    return jsonify({
                        "success": False,
                        "message": "CPF inválido"
                    }), 400
                if collection.find_one({"cpf": novo_cpf, "_id": {"$ne": obj_id}}):
                    return jsonify({
                        "success": False,
                        "message": "CPF já cadastrado"
                    }), 409
                data["cpf"] = novo_cpf

            if "email" in data:
                if collection.find_one({"email": data["email"], "_id": {"$ne": obj_id}}):
                    return jsonify({
                        "success": False,
                        "message": "Email já cadastrado"
                    }), 409

            if "password" in data:
                data["password"] = generate_password_hash(data["password"])

            user = collection.find_one_and_update(
                {"_id": obj_id},
                {"$set": data},
                return_document=ReturnDocument.AFTER
            )
            
            if not user:
                return jsonify({
                    "success": False,
                    "message": "Usuário não encontrado"
                }), 404
            
            user["_id"] = str(user["_id"])
            return jsonify({
                "success": True,
                "message": "Usuário atualizado com sucesso",
                "user": user
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500


    @app.route("/usuarios/<user_id>", methods=["DELETE"])
    @jwt_required()
    def delete_user(user_id):
        """DELETE /usuarios/<user_id> - Deletar usuário (apenas si mesmo)"""
        try:
            current_user_id = get_jwt_identity()
            
            # ← VERIFICAÇÃO: Usuário só pode deletar sua própria conta
            if current_user_id != user_id:
                return jsonify({
                    "success": False,
                    "message": "Acesso negado. Você só pode deletar sua própria conta"
                }), 403
            
            obj_id = ObjectId(user_id)
        except InvalidId:
            return jsonify({
                "success": False,
                "message": "ID inválido"
            }), 400
        
        try:
            collection = get_db()
            result = collection.delete_one({"_id": obj_id})
            
            if result.deleted_count == 0:
                return jsonify({
                    "success": False,
                    "message": "Usuário não encontrado"
                }), 404
            
            return jsonify({
                "success": True,
                "message": "Usuário deletado com sucesso"
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500


    @app.route("/usuarios-dev", methods=["GET"])
    def get_usuarios_desenvolvimento():
        """GET /usuarios-dev - Listar TODOS os usuários (APENAS DESENVOLVIMENTO)"""
        try:
            # Verificar se está em ambiente de desenvolvimento
            if os.getenv("FLASK_ENV") != "development":
                return jsonify({
                    "success": False,
                    "message": "Esta rota está disponível apenas em desenvolvimento"
                }), 403

            collection = get_db()
            users = list(collection.find({}, {"password": 0}))  # Nunca retornar senha
            
            # Converter ObjectId para string
            for user in users:
                user["_id"] = str(user["_id"])
            
            return jsonify({
                "success": True,
                "total": len(users),
                "usuarios": users
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500


def register_routes_invoices(app):
    """Registra todas as rotas de extratos - Richardson Nível 2"""
    
    @app.route("/faturas/", methods=["GET"])
    @jwt_required()
    def get_faturas():
        """GET /faturas - Listar apenas faturas do usuário autenticado"""
        try:
            user_id = get_jwt_identity()  # ← Pega ID do token
            db = get_db_connection()
            faturas_collection = db[COLLECTION_FATURAS]
            
            # ← Filtra apenas faturas do usuário logado
            faturas = list(faturas_collection.find({"user_id": user_id}))
            for fatura in faturas:
                fatura["_id"] = str(fatura["_id"])
            
            return jsonify({
                "success": True,
                "faturas": faturas
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500


    @app.route("/faturas/usuario/<user_id>", methods=["GET"])
    @jwt_required()
    def get_user_faturas(user_id):
        """GET /faturas/usuario/<user_id> - Listar faturas (apenas próprias)"""
        try:
            current_user_id = get_jwt_identity()
            
            # ← VERIFICAÇÃO: Usuário só vê suas próprias faturas
            if current_user_id != user_id:
                return jsonify({
                    "success": False,
                    "message": "Acesso negado. Você só pode ver suas próprias faturas"
                }), 403
            
            obj_id = ObjectId(user_id)
        except InvalidId:
            return jsonify({
                "success": False,
                "message": "ID de usuário inválido"
            }), 400
        
        try:
            db = get_db_connection()
            users_collection = db[COLLECTION_USERS]
            faturas_collection = db[COLLECTION_FATURAS]
            
            # Verificar se o usuário existe
            user = users_collection.find_one({"_id": obj_id})
            if not user:
                return jsonify({
                    "success": False,
                    "message": "Usuário não encontrado"
                }), 404
            
            # Buscar faturas do usuário
            faturas = list(faturas_collection.find({"user_id": str(obj_id)}))
            for fatura in faturas:
                fatura["_id"] = str(fatura["_id"])
            
            return jsonify({
                "success": True,
                "faturas": faturas
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500


    @app.route("/faturas/usuario/<user_id>", methods=["POST"])
    @jwt_required()
    def post_extrato(user_id):
        """POST /faturas/usuario/<user_id> - Adicionar extrato (apenas próprio)"""
        try:
            current_user_id = get_jwt_identity()
            
            # ← VERIFICAÇÃO: Usuário só pode adicionar faturas suas
            if current_user_id != user_id:
                return jsonify({
                    "success": False,
                    "message": "Acesso negado. Você só pode adicionar suas próprias faturas"
                }), 403
            
            user_id_obj = ObjectId(user_id)
        except InvalidId:
            return jsonify({
                "success": False,
                "message": "ID de usuário inválido"
            }), 400
        
        try:
            db = get_db_connection()
            users_collection = db[COLLECTION_USERS]
            faturas_collection = db[COLLECTION_FATURAS]
        except Exception as e:
            print(f"Erro ao conectar no db: {str(e)}")
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500
        
        try:
            files = request.files.getlist("file")
            if not files:
                return jsonify({
                    "success": False,
                    "message": "Nenhum arquivo enviado"
                }), 400
            
            buffers = []
            for f in files:
                data = f.read()
                f.stream.seek(0)
                buffer = BytesIO(data)
                buffer.name = f.filename
                buffers.append(buffer)
        
            extratos = [extrato.to_dict() for extrato in asyncio.run(formatar_extratos(buffers))]
            mes_ano = extratos[0]["data"]

            fatura = faturas_collection.find_one({"user_id": str(user_id_obj), "mes_ano": mes_ano})
            if not fatura:
                fatura_data = {
                    "user_id": str(user_id_obj),
                    "mes_ano": mes_ano,
                    "extratos": []
                }
                result = faturas_collection.insert_one(fatura_data)
                fatura_id = result.inserted_id
                users_collection.update_one(
                    {"_id": user_id_obj},
                    {"$push": {"faturas": str(fatura_id)}}
                )
            else:
                fatura_id = fatura["_id"]

            # Adicionar extrato à lista de extratos da faturaExtrato
            faturas_collection.update_one(
                {"_id": fatura_id},
                {"$push": {"extratos": {"$each": extratos}}}
            )
            
            return jsonify({
                "success": True,
                "message": "Extrato adicionado com sucesso",
                "extrato": extratos
            }), 201
        except Exception as e:
            print(f"Erro ao adicionar extrato: {str(e)}")
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def _bson_to_json_compatible(obj):
        """Converte recursivamente ObjectId e datetime para tipos JSON-serializáveis."""
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {k: _bson_to_json_compatible(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_bson_to_json_compatible(v) for v in obj]
        return obj

    @app.route("/faturas/<fatura_id>", methods=["GET"])
    @jwt_required()
    def get_fatura(fatura_id):
        """GET /faturas/<fatura_id> - Retorna fatura (apenas se for do usuário)"""
        current_user_id = get_jwt_identity()
        
        try:
            fatura_obj_id = ObjectId(fatura_id)
        except InvalidId:
            return jsonify({
                "success": False,
                "message": "ID de fatura inválido"
            }), 400

        try:
            db = get_db_connection()
            faturas_collection = db[COLLECTION_FATURAS]

            fatura = faturas_collection.find_one({"_id": fatura_obj_id})
            if not fatura:
                return jsonify({
                    "success": False,
                    "message": "Fatura não encontrada"
                }), 404

            # ← VERIFICAÇÃO: Usuário só vê suas próprias faturas
            if fatura["user_id"] != current_user_id:
                return jsonify({
                    "success": False,
                    "message": "Acesso negado. Você só pode ver suas próprias faturas"
                }), 403

            # converte campos BSON não serializáveis
            fatura_serializavel = _bson_to_json_compatible(fatura)

            return jsonify({
                "success": True,
                "fatura": fatura_serializavel
            }), 200

        except Exception as e:
            app.logger.exception("Erro ao buscar fatura")
            return jsonify({
                "success": False,
                "message": "Erro interno ao buscar fatura"
            }), 500

    @app.route("/faturas-dev", methods=["GET"])
    def get_faturas_desenvolvimento():
        """GET /faturas-dev - Listar TODAS as faturas (APENAS DESENVOLVIMENTO)"""
        try:
            # Verificar se está em ambiente de desenvolvimento
            if os.getenv("FLASK_ENV") != "development":
                return jsonify({
                    "success": False,
                    "message": "Esta rota está disponível apenas em desenvolvimento"
                }), 403

            db = get_db_connection()
            faturas_collection = db[COLLECTION_FATURAS]
            
            faturas = list(faturas_collection.find({}))
            
            # Converter ObjectId para string
            for fatura in faturas:
                fatura["_id"] = str(fatura["_id"])
            
            return jsonify({
                "success": True,
                "total": len(faturas),
                "faturas": faturas
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

