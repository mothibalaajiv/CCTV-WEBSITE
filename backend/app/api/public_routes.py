from flask import Blueprint, request, jsonify
from app.services.camera_service import CameraService

public_bp = Blueprint('public', __name__)

@public_bp.route('/cameras', methods=['GET'])
def get_public_cameras():
    cameras = CameraService.get_all_cameras()
    # Filter to only return necessary fields for security
    public_cameras = [
        {
            "camera_code": c.get("camera_code"),
            "location_name": c.get("location_name")
        }
        for c in cameras
    ]
    return jsonify({"status": "success", "data": public_cameras})

@public_bp.route('/cameras/<camera_code>/location', methods=['PUT'])
def update_camera_location(camera_code):
    data = request.get_json()
    location_name = data.get('location_name')
    if not location_name:
        return jsonify({"status": "error", "message": "Location name is required"}), 400
        
    camera = CameraService.update_camera_location_by_code(camera_code, location_name)
    return jsonify({"status": "success", "data": camera})
