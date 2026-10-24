from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.stream_service import StreamService
from app.utils.decorators import admin_required

stream_bp = Blueprint('streams', __name__)

@stream_bp.route('/', methods=['GET'])
@jwt_required()
def get_streams():
    streams = StreamService.get_all_streams()
    
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

    active_streams = []
    for stream in streams:
        s_mac = stream.get('local_server_mac', '')
        matching_diag = next((d for d in cloud_data if d.get('local_server_mac', '').lower() == s_mac.lower()), None)
        if not matching_diag and len(cloud_data) > 0:
            matching_diag = cloud_data[0]
            
        is_online = False
        if matching_diag:
            last_checked_str = matching_diag.get('timestamp')
            if last_checked_str:
                try:
                    last_checked_dt = datetime.fromisoformat(last_checked_str.replace("Z", "+00:00"))
                    if last_checked_dt.tzinfo is None:
                        last_checked_dt = last_checked_dt.replace(tzinfo=timezone.utc)
                    if datetime.now(timezone.utc) - last_checked_dt < timedelta(minutes=1):
                        is_online = True
                except Exception:
                    pass
        
        if is_online:
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
