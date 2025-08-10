from flask import Blueprint, jsonify
from services.data_service import get_welcome_message

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["GET"])
def home():
    return jsonify({"message": get_welcome_message()})
