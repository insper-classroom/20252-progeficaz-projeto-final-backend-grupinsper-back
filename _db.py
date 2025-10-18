import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId  # Importante para lidar com o ID do MongoDB
from dotenv import load_dotenv

import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI') 
DB_NAME = os.getenv('DB_NAME') 
COLLECTION_NAME = os.getenv('COLLECTION_NAME')


def get_db():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info() 
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
    except ConnectionFailure as e:
        print(f"Erro: Não foi possível conectar ao MongoDB. Verifique sua MONGO_URI. \nDetalhes: {e}")
        exit()

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info() 
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print(f"Conexão com o MongoDB no banco '{DB_NAME}' estabelecida com sucesso!")
    except ConnectionFailure as e:
        print(f"Erro: Não foi possível conectar ao MongoDB. Verifique sua MONGO_URI. \nDetalhes: {e}")
        exit()

    return collection