"""
app.py

SmartHarvest Flask application entry point.

Responsibilities:
- Load environment-specific config from config.py
- Configure Python logging to app.log with timestamps
- Centralised error handlers (400, 404, 500) returning JSON
- Database connection via SQLAlchemy, read from .env
- Health-check endpoint for Render
"""

import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from config import get_config

db = SQLAlchemy()


def create_app(env: str | None = None) -> Flask:
    """Application factory."""
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(get_config(env))

    _configure_logging(app)
    db.init_app(app)

      # --- Register blueprints (Routes) ---
    from routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    _register_error_handlers(app)

    @app.route("/health")
    def health():
        """Render health check."""
        return jsonify(status="ok"), 200

    app.logger.info("SmartHarvest app started (env=%s)", app.config.get("ENV"))
    return app


def _configure_logging(app: Flask) -> None:
    """Log to app.log with rotation; also log to console."""
    level = getattr(logging, app.config["LOG_LEVEL"].upper(), logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        app.config["LOG_FILE"], maxBytes=1_000_000, backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(level)

    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console)
    app.logger.setLevel(level)


def _register_error_handlers(app: Flask) -> None:
    """Return clean JSON errors and log them — never show stack traces."""

    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning("400 Bad Request: %s", e)
        return jsonify(error="Bad request", message=str(e)), 400

    @app.errorhandler(404)
    def not_found(e):
        app.logger.warning("404 Not Found: %s", e)
        return jsonify(error="Not found", message=str(e)), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("500 Internal Server Error")
        db.session.rollback()  # rollback any failed write
        return jsonify(error="Internal server error"), 500


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
