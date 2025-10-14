from app import create_app 
from _db import get_db


app = create_app()


if __name__ == "__main__":
    print("Starting Flask app...")
    print("Initializing database connection...")
    get_db()
    app.run()
    
