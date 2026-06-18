from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.camera_service import CameraService
from app.utils.decorators import admin_required

camera_bp = Blueprint('cameras', __name__)

@camera_bp.route('/', methods=['POST'])
@admin_required()
def register_camera():
    """
    Register Camera
    ---
    tags:
      - Cameras
    """
    data = request.get_json()
    camera = CameraService.register_camera(data)
    return jsonify({"status": "success", "data": camera}), 201

@camera_bp.route('/', methods=['GET'])
@jwt_required()
def get_cameras():
    """
    List all cameras
    ---
    tags:
      - Cameras
    """
    cameras = CameraService.get_all_cameras()
    return jsonify({"status": "success", "data": cameras})

@camera_bp.route('/<camera_id>', methods=['PUT'])
@admin_required()
def update_camera(camera_id):
    data = request.get_json()
    camera = CameraService.update_camera(camera_id, data)
    return jsonify({"status": "success", "data": camera})

@camera_bp.route('/<camera_id>/status', methods=['PUT'])
@admin_required()
def set_camera_status(camera_id):
    data = request.get_json()
    is_active = data.get('is_active', True)
    camera = CameraService.set_camera_status(camera_id, is_active)
    return jsonify({"status": "success", "data": camera})

@camera_bp.route('/<camera_id>', methods=['DELETE'])
@admin_required()
def delete_camera(camera_id):
    CameraService.delete_camera(camera_id)
    return jsonify({"status": "success", "message": "Camera deleted"})
