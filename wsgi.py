from app import create_app
from _db import get_db
from flask_cors import CORS
from flask import Flask

app = create_app()
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

if __name__ == "__main__":
    
    print("Starting Flask app...")
    print("Initializing database connection...")
    get_db()
    app.run(debug=True)