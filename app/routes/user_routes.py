from flask import Blueprint, jsonify, request
from app.services.user_service import get_all_users, add_user

user_bp = Blueprint("users", __name__)

@user_bp.route("/users", methods=["GET"])
def get_users():
    return jsonify({
        "users": get_all_users()
    })

@user_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)

    if not data or "name" not in data or not data["name"].strip():
        return jsonify({
            "error": "Поле 'name' обязательно"
        }), 400

    user = add_user(data["name"].strip())
    return jsonify(user), 201
