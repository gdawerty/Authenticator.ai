from flask import Blueprint, request, jsonify
from services.user_service import login_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if login_user(username, password):
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401
