from bson import ObjectId
from bson.errors import InvalidId
from flask import jsonify, request, url_for
from _db import get_db

def _user_to_dict(user):
    """Converte documento MongoDB para dict com HATEOAS"""
    if user:
        user["_id"] = str(user["_id"])
        user["_links"] = {
            "self": {"href": url_for("get_user", user_id=user["_id"], _external=True)},
            "all": {"href": url_for("list_users", _external=True)},
            "delete": {"href": url_for("delete_user", user_id=user["_id"], _external=True), "method": "DELETE"},
            "update": {"href": url_for("update_user", user_id=user["_id"], _external=True), "method": "PUT"}
        }
    return user

def register_routes(app):
    """Registra todas as rotas de usuários - Richardson Nível 3"""
    
    @app.route("/users", methods=["GET"])
    def list_users():
        """GET /users - Listar todos os usuários"""
        try:
            collection = get_db()
            users = list(collection.find({}, {"_id": 1, "name": 1, "email": 1}))
            users_with_links = [_user_to_dict(u) for u in users]
            return jsonify({
                "_embedded": {"users": users_with_links},
                "_links": {
                    "self": {"href": url_for("list_users", _external=True)},
                    "create": {"href": url_for("create_user", _external=True), "method": "POST"}
                }
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/users", methods=["POST"])
    def create_user():
        """POST /users - Criar novo usuário"""
        try:
            data = request.get_json()
            
            if not data or not data.get("name") or not data.get("email"):
                return jsonify({"error": "name e email são obrigatórios"}), 400
            
            collection = get_db()
            result = collection.insert_one({
                "name": data["name"],
                "email": data["email"]
            })
            
            user = collection.find_one({"_id": result.inserted_id})
            return jsonify(_user_to_dict(user)), 201
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
            
            return jsonify(_user_to_dict(user)), 200
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
            result = collection.update_one({"_id": obj_id}, {"$set": data})
            
            if result.matched_count == 0:
                return jsonify({"error": "Usuário não encontrado"}), 404
            
            user = collection.find_one({"_id": obj_id})
            return jsonify(_user_to_dict(user)), 200
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
            
            return jsonify({"_links": {"all": {"href": url_for("list_users", _external=True)}}}), 204
        except Exception as e:
            return jsonify({"error": str(e)}), 500