import asyncio
from datetime import datetime
from io import BytesIO

from bson import ObjectId
from bson.errors import InvalidId
from validate_docbr import CPF
from flask import jsonify, request

from app.controller.utils_formatar_extrato import formatar_extratos
from _db import get_db , get_db_connection

COLLECTION_USERS = "usuarios_collection"
COLLECTIONS_FATURAS = "faturas_collection"


def register_routes_user(app):
    """Registra todas as rotas de usuários - Richardson Nível 2"""
    
    # Criar índices na primeira inicialização
    @app.before_request
    def create_indexes():
        collection = get_db()
        collection.create_index("email", unique=True)
    
    @app.route("/users", methods=["GET"])
    def list_users():
        """GET /users - Listar todos os usuários"""
        try:
            collection = get_db()
            users = list(collection.find({}, {"name": 1, "email": 1, "cpf": 1, "phone": 1 , "faturas": 1}))
            # Converter ObjectId para string
            for user in users:
                user["_id"] = str(user["_id"])
            return jsonify(users), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/users", methods=["POST"])
    def create_user():
        """POST /users - Criar novo usuário"""
        try:
            data = request.get_json()
            cpf = data.get("cpf")
            if not data or not data.get("name") or not data.get("email") or not data.get("phone") or not cpf:
                return jsonify({"error": "name, email, phone e cpf são obrigatórios"}), 400
            if cpf and not CPF().validate(cpf):
                return jsonify({"error": "CPF inválido"}), 400
            
            collection = get_db()
            result = collection.insert_one({
                "name": data["name"],
                "email": data["email"],
                "cpf": data.get("cpf"),
                "phone": data.get("phone"),
                "faturas": []
            })
            
            user = {
                "_id": str(result.inserted_id),
                "name": data["name"],
                "email": data["email"],
                "cpf": data.get("cpf"),
                "phone": data.get("phone"),
                "faturas": []
            }
            return jsonify(user), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/users/<user_id>", methods=["GET"])
    def get_user(user_id):
        """GET /users/<id> - Obter usuário por ID"""
        try:
            obj_id = ObjectId(user_id)
        except InvalidId:
            return jsonify({"error": "ID inválido"}), 400
        
        try:
            collection = get_db()
            user = collection.find_one({"_id": obj_id})
            
            if not user:
                return jsonify({"error": "Usuário não encontrado"}), 404
            
            user["_id"] = str(user["_id"])
            return jsonify(user), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/users/<user_id>", methods=["PUT"])
    def update_user(user_id):
        """PUT /users/<id> - Atualizar usuário"""
        try:
            obj_id = ObjectId(user_id)
        except InvalidId:
            return jsonify({"error": "ID inválido"}), 400
        
        try:
            data = request.get_json() 
            
            if not data:
                return jsonify({"error": "Dados são obrigatórios"}), 400
            
            collection = get_db()
            user = collection.find_one_and_update(
                {"_id": obj_id},
                {"$set": data},
                return_document=True
            )
            
            if not user:
                return jsonify({"error": "Usuário não encontrado"}), 404
            
            user["_id"] = str(user["_id"])
            return jsonify(user), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/users/<user_id>", methods=["DELETE"])
    def delete_user(user_id):
        """DELETE /users/<id> - Deletar usuário"""
        try:
            obj_id = ObjectId(user_id)
        except InvalidId:
            return jsonify({"error": "ID inválido"}), 400
        
        try:
            collection = get_db()
            result = collection.delete_one({"_id": obj_id})
            
            if result.deleted_count == 0:
                return jsonify({"error": "Usuário não encontrado"}), 404
            
            return jsonify({"message": "Usuário deletado com sucesso"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def register_routes_invoices(app):
    """Registra todas as rotas de extratos - Richardson Nível 2"""
    
    @app.route("/faturas/", methods=["GET"])
    def get_faturas():
        """GET /faturas - Listar todos os extratos"""
        try:
            db = get_db_connection()
            faturas_collection = db[COLLECTIONS_FATURAS]
            faturas = list(faturas_collection.find())
            for fatura in faturas:
                fatura["_id"] = str(fatura["_id"])
            return jsonify(faturas), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/faturas/<user_id>", methods=["POST"])
    def post_fatura(user_id):
        """POST /faturas/<user_id> - Criar faturaExtrato para o mês atual"""
        try:
            obj_id = ObjectId(user_id)
        except InvalidId:
            return jsonify({"error": "ID de usuário inválido"}), 400
        
        try:
            db = get_db_connection()
            users_collection = db[COLLECTION_USERS]
            faturas_collection = db[COLLECTIONS_FATURAS]
            
            # Verificar se usuário existe
            user = users_collection.find_one({"_id": obj_id})
            if not user:
                return jsonify({"error": "Usuário não encontrado"}), 404
            
            mes_ano = datetime.now().strftime("%m/%Y")
            
            # Verificar se já existe faturaExtrato para este mês/ano
            fatura_existente = faturas_collection.find_one({
                "user_id": str(obj_id),
                "mes_ano": mes_ano
            })
            
            if fatura_existente:
                return jsonify({"error": "faturaExtrato já existe para este mês"}), 400
            
            # Criar nova faturaExtrato
            fatura_data = {
                "user_id": str(obj_id),
                "mes_ano": mes_ano,
                "extratos": []
            }
            
            result = faturas_collection.insert_one(fatura_data)
            fatura_id = str(result.inserted_id)
            
            # Adicionar faturaExtrato à lista do usuário
            users_collection.update_one(
                {"_id": obj_id},
                {"$push": {"faturas": fatura_id}}
            )
            
            return jsonify({"id": fatura_id, "mes_ano": mes_ano, "user_id": str(obj_id), "extratos": []}), 201
        except Exception as e:
            print(f"Erro no POST: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/faturas/<user_id>", methods=["GET"])
    def get_user_faturas(user_id):
        """GET /faturas/<user_id> - Listar extratos do usuário"""
        try:
            obj_id = ObjectId(user_id)
        except InvalidId:
            return jsonify({"error": "ID de usuário inválido"}), 400
        
        try:
            db = get_db_connection()
            users_collection = db[COLLECTION_USERS]
            faturas_collection = db[COLLECTIONS_FATURAS]
            
            # Verificar se o usuário existe
            user = users_collection.find_one({"_id": obj_id})
            if not user:
                return jsonify({"error": "Usuário não encontrado"}), 404
            
            # Buscar faturas do usuário
            faturas = list(faturas_collection.find({"user_id": str(obj_id)}))
            for fatura in faturas:
                fatura["_id"] = str(fatura["_id"])
            return jsonify(faturas), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/faturas/<fatura_id>/extratos", methods=["POST"])
    def post_extrato(fatura_id):
        """POST /faturas/<fatura_id>/extratos - Adicionar extrato à faturaExtrato"""
        try:
            fatura_obj_id = ObjectId(fatura_id)
        except InvalidId:
            return jsonify({"error": "ID de faturaExtrato inválido"}), 400
        
        try:
            files = request.files.getlist("file")
            if not files:
                return jsonify({"error": "Nenhum arquivo enviado"}), 400
            
            buffers = []
            for f in files:
                data = f.read()
                f.stream.seek(0)
                buffer = BytesIO(data)
                buffer.name = f.filename
                buffers.append(buffer)
        
            extratos = [extrato.to_dict() for extrato in asyncio.run(formatar_extratos(buffers))]

            db = get_db_connection()
            faturas_collection = db[COLLECTIONS_FATURAS]
            
            # Verificar se faturaExtrato existe
            fatura = faturas_collection.find_one({"_id": fatura_obj_id})
            if not fatura:
                return jsonify({"error": "faturaExtrato não encontrada"}), 404
            
            # Adicionar extrato à lista de extratos da faturaExtrato
            faturas_collection.update_one(
                {"_id": fatura_obj_id},
                {"$push": {"extratos": extratos}}
            )
            
            return jsonify({"extrato": extratos}), 201
        except Exception as e:
            print(f"Erro ao adicionar extrato: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/faturas/<fatura_id>/extratos", methods=["GET"])
    def get_extratos(fatura_id):
        """GET /faturas/<fatura_id>/extratos - Listar extratos de uma faturaExtrato"""
        try:
            fatura_obj_id = ObjectId(fatura_id)
        except InvalidId:
            return jsonify({"error": "ID de faturaExtrato inválido"}), 400
        
        try:
            db = get_db_connection()
            faturas_collection = db[COLLECTIONS_FATURAS]
            
            # Buscar faturaExtrato
            fatura = faturas_collection.find_one({"_id": fatura_obj_id})
            if not fatura:
                return jsonify({"error": "faturaExtrato não encontrada"}), 404
            
            return jsonify(fatura["extratos"]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500