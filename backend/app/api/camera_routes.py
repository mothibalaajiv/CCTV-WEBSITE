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
    cameras = CameraService.get_all_cameras()
    
    import os, urllib.request, json
    from datetime import datetime, timezone, timedelta
    
    cloud_url = os.getenv("CLOUD_SERVER_URL", "http://104.251.214.177:8000/api/diagnostics")
    if cloud_url.endswith("/api/streams"):
        cloud_url = cloud_url.replace("/api/streams", "/api/diagnostics")
    try:
        req = urllib.request.Request(cloud_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            cloud_data = json.loads(response.read().decode()).get('data', [])
    except Exception:
        cloud_data = []

    for c in cameras:
        # A camera belongs to a local server based on its mac, but since cameras don't map perfectly in this endpoint,
        # we check if any telemetry reports this camera as active recently.
        c_mac = c.get('mac_address', '')
        
        is_online = False
        for diag in cloud_data:
            last_checked_str = diag.get('timestamp')
            is_recent = False
            if last_checked_str:
                try:
                    last_checked_dt = datetime.fromisoformat(last_checked_str.replace("Z", "+00:00"))
                    if last_checked_dt.tzinfo is None:
                        last_checked_dt = last_checked_dt.replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) - last_checked_dt < timedelta(minutes=1):
                        is_recent = True
                except Exception:
                    pass
            
            if is_recent and diag.get('cameras'):
                for cam in diag['cameras']:
                    if cam.get('camera_mac', '').lower() == c_mac.lower():
                        is_online = True
                        break
            if is_online:
                break
                
        c['stream_status'] = 'online' if is_online else 'offline'
        if '_id' in c:
            c['_id'] = str(c['_id'])
            
    from app.services.user_service import UserService
    from flask_jwt_extended import get_jwt_identity
    
    user = UserService.get_user(get_jwt_identity())
    if user.get('role') != 'admin':
        assigned = user.get('assigned_sites', [])
        cameras = [c for c in cameras if str(c.get('current_site') or c.get('site_id')) in map(str, assigned)]
        
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
