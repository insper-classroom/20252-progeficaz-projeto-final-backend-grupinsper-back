import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI') 
DB_NAME = os.getenv('DB_NAME') 
COLLECTION_USERS = os.getenv('COLLECTION_USERS')
COLLECTIONS_FATURAS = os.getenv('COLLECTION_FATURAS')
_client = None
_collection = None

def get_db():
    global _client, _collection
    
    if _collection is None:
        try:
            _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            _client.server_info() 
            db = _client[DB_NAME]
            _collection = db[COLLECTION_USERS]
            print(f"Conexão com o MongoDB no banco '{DB_NAME}' estabelecida com sucesso!")
            print(f"Coleção '{COLLECTION_USERS}' selecionada.")
        except ConnectionFailure as e:
            print(f"Erro: Não foi possível conectar ao MongoDB. Verifique sua MONGO_URI. \nDetalhes: {e}")
            exit()

    return _collection

def get_db_connection():
    """Retorna o banco de dados inteiro para acessar múltiplas coleções"""
    global _client
    if _client is None:
        get_db()  # Inicializa a conexão se necessário
    return _client[DB_NAME]

def get_faturas_collection():
    global _client
    if _client is None:
        get_db()  
    
    db = _client[DB_NAME]
    faturas_collection = db[COLLECTIONS_FATURAS]
    return faturas_collection