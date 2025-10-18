import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI') 
DB_NAME = os.getenv('DB_NAME') 
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

_client = None
_collection = None

def get_db():
    global _client, _collection
    
    if _collection is None:
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            _client.server_info() 
            db = _client[DB_NAME]
            _collection = db[COLLECTION_NAME]
            print(f"Conexão com o MongoDB no banco '{DB_NAME}' estabelecida com sucesso!")
        except ConnectionFailure as e:
            print(f"Erro: Não foi possível conectar ao MongoDB. Verifique sua MONGO_URI. \nDetalhes: {e}")
            exit()
    
    return _collection