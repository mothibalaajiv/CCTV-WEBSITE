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
    
    from datetime import datetime, timezone
    from app.utils.telemetry import parse_timestamp, is_telemetry_fresh, fetch_cloud_diagnostics, camera_matches
    
    cloud_data = fetch_cloud_diagnostics()
    now_utc = datetime.now(timezone.utc)
    all_ts = [parse_timestamp(d.get('timestamp')) for d in cloud_data]
    max_cloud_ts = max(all_ts) if all_ts else None

    for c in cameras:
        is_online = False
        for diag in cloud_data:
            d_time = parse_timestamp(diag.get('timestamp'))
            is_recent = is_telemetry_fresh(d_time, now_utc, max_cloud_ts, window_seconds=300)
            
            if is_recent and diag.get('cameras'):
                for cam in diag['cameras']:
                    if camera_matches(c, cam.get('camera_mac'), cam.get('camera_code')):
                        # If camera is reporting active or reachable RTSP
                        if cam.get('cloud_push_status') == 'active' or cam.get('recording_status') == 'active' or cam.get('rtsp_reachable'):
                            is_online = True
                            break
            if is_online:
                break
                
        # If telemetry confirmed online or mongo had online without contrary offline report
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
