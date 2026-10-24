from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.stream_service import StreamService
from app.utils.decorators import admin_required

stream_bp = Blueprint('streams', __name__)

@stream_bp.route('/', methods=['GET'])
@jwt_required()
def get_streams():
    streams = StreamService.get_all_streams()
    
    from datetime import datetime, timezone
    from app.utils.telemetry import parse_timestamp, is_telemetry_fresh, fetch_cloud_diagnostics
    
    cloud_data = fetch_cloud_diagnostics()
    now_utc = datetime.now(timezone.utc)
    all_ts = [parse_timestamp(d.get('timestamp')) for d in cloud_data]
    max_cloud_ts = max(all_ts) if all_ts else None

    active_streams = []
    for stream in streams:
        s_mac = stream.get('local_server_mac', '')
        matching_diag = next((d for d in cloud_data if d.get('local_server_mac', '').lower() == s_mac.lower()), None)
        if not matching_diag and len(cloud_data) > 0:
            matching_diag = cloud_data[0]
            
        is_online = False
        if matching_diag:
            d_time = parse_timestamp(matching_diag.get('timestamp'))
            is_online = is_telemetry_fresh(d_time, now_utc, max_cloud_ts, window_seconds=300)
        
        if is_online and stream.get('status') != 'paused':
            active_streams.append(stream)
            
    from app.services.user_service import UserService
    from flask_jwt_extended import get_jwt_identity
    user = UserService.get_user(get_jwt_identity())
    
    if user.get('role') != 'admin':
        from app.services.camera_service import CameraService
        assigned = user.get('assigned_sites', [])
        cameras = CameraService.get_all_cameras()
        allowed_camera_codes = [str(c.get('camera_code')) for c in cameras if str(c.get('current_site') or c.get('site_id')) in map(str, assigned)]
        active_streams = [s for s in active_streams if str(s.get('camera_code')) in allowed_camera_codes]
            
    return jsonify({"status": "success", "data": active_streams})

@stream_bp.route('/pause', methods=['POST'])
@admin_required()
def pause_stream():
    """
    Pause a live stream
    ---
    tags:
      - Streams
    """
    data = request.get_json()
    stream = StreamService.pause_stream(data['camera_code'])
    return jsonify({"status": "success", "data": stream})

@stream_bp.route('/resume', methods=['POST'])
@admin_required()
def resume_stream():
    """
    Resume a live stream
    ---
    tags:
      - Streams
    """
    data = request.get_json()
    stream = StreamService.resume_stream(data['camera_code'])
    return jsonify({"status": "success", "data": stream})
