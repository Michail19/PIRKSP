from flask import Blueprint, jsonify, request
from app.services.user_service import get_users, create_user

user_bp = Blueprint("users", __name__)

@user_bp.route("/", methods=["GET"])
def users():
    return jsonify(get_users())

@user_bp.route("/", methods=["POST"])
def add_user():
    data = request.json
    return jsonify(create_user(data))
