from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService
from app.utils.decorators import admin_required

user_bp = Blueprint('users', __name__)

@user_bp.route('/', methods=['POST'])
@admin_required()
def create_user():
    """
    Create User (Admin Only)
    ---
    tags:
      - Users
    """
    data = request.get_json()
    user = UserService.create_user(data)
    return jsonify({"status": "success", "data": user}), 201

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """
    List all users
    ---
    tags:
      - Users
    """
    users = UserService.get_all_users()
    return jsonify({"status": "success", "data": users})

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """
    Get current logged-in user
    ---
    tags:
      - Users
    """
    user_id = get_jwt_identity()
    user = UserService.get_user(user_id)
    return jsonify({"status": "success", "data": {"user": user}})

@user_bp.route('/<user_id>', methods=['PUT'])
@admin_required()
def update_user(user_id):
    data = request.get_json()
    UserService.update_user(user_id, data)
    return jsonify({"status": "success", "message": "User updated"})

@user_bp.route('/<user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    UserService.delete_user(user_id)
    return jsonify({"status": "success", "message": "User deleted"})
