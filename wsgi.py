"""WSGI entry point for the Flask application."""

from app import create_app


app = create_app()


if __name__ == "__main__":
    # Useful when running `python wsgi.py` locally
    app.run()
