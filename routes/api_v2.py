import os
from urllib.parse import unquote, urlparse

from flask import Blueprint, jsonify
import pymysql


api_bp = Blueprint("api_v2", __name__)


def get_db_connection():
    """
    Connect to MySQL using DATABASE_URL when deployed,
    otherwise use local MySQL.
    """

    url = os.getenv("DATABASE_URL")

    if url:
        parsed = urlparse(url)

        settings = {
            "host": parsed.hostname,
            "port": parsed.port or 3306,
            "user": unquote(parsed.username or ""),
            "password": unquote(parsed.password or ""),
            "database": parsed.path.lstrip("/"),
            "cursorclass": pymysql.cursors.DictCursor,
        }
    else:
        settings = {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "mydb",
            "cursorclass": pymysql.cursors.DictCursor,
        }

    return pymysql.connect(**settings)


def success(data, status=200):
    return jsonify(data), status


def error(message, status=400):
    return jsonify({
        "error": message,
        "message": message
    }), status


@api_bp.route("/health", methods=["GET"])
def health():
    try:
        connection = get_db_connection()
        connection.close()

        return success({
            "status": "ok",
            "database": "mysql"
        })

    except Exception as e:
        return error(str(e), 500)


