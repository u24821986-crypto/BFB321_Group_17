import logging
import os

from flask import Flask, jsonify, render_template

try:
    from config import get_config
except Exception:  # config.py is optional for this setup
    get_config = None


def create_app():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"),
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = Flask(__name__)

    if get_config:
        app.config.from_object(get_config(os.getenv("FLASK_ENV", "production")))
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-insecure-key")

    # API routes live under /api (routes/api.py)
    from routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # ---- Pages ----
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login")
    def login():
        return render_template("login.html")

    @app.route("/operations")
    def operations():
        return render_template("operations.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # ---- JSON error handlers ----
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Server error"}), 500

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
