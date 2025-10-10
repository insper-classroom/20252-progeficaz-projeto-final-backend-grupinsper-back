from typing import Any, Dict

from flask import jsonify
from flask.typing import ResponseReturnValue


def register_routes(app) -> None:
    """Attach route handlers to the given Flask app instance."""

    @app.get("/")
    def healthcheck() -> ResponseReturnValue:
        payload: Dict[str, Any] = {"status": "ok", "message": "Backend is running"}
        return jsonify(payload)
