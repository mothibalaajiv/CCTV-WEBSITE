from flask import Blueprint, request, jsonify
from app.services.server_service import LocalServerService
from app.utils.decorators import admin_required
from flask_jwt_extended import jwt_required

server_bp = Blueprint('servers', __name__)

@server_bp.route('', methods=['POST'])
@admin_required()
def register_server():
    data = request.get_json()
    server = LocalServerService.register_server(data)
    return jsonify({"status": "success", "data": server}), 201

@server_bp.route('', methods=['GET'])
@jwt_required()
def get_servers():
    servers = LocalServerService.get_all_servers()
    return jsonify({"status": "success", "data": servers})

@server_bp.route('/<server_id>/status', methods=['PUT'])
@admin_required()
def set_server_status(server_id):
    data = request.get_json()
    is_active = data.get('is_active', True)
    server = LocalServerService.set_server_status(server_id, is_active)
    return jsonify({"status": "success", "data": server})

@server_bp.route('/<server_id>', methods=['DELETE'])
@admin_required()
def delete_server(server_id):
    LocalServerService.delete_server(server_id)
    return jsonify({"status": "success", "message": "Server deleted"})
