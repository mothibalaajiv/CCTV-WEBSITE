from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_jwt_extended import jwt_required
from app.services.stream_service import StreamService
from app.utils.decorators import admin_required
import os
import urllib.request
import urllib.error

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

    # Construct secure proxy base URL matching the incoming request scheme & host
    proto = request.headers.get('X-Forwarded-Proto', request.scheme)
    host = request.headers.get('X-Forwarded-Host', request.host)
    proxy_base = f"{proto}://{host}/api/streams/hls"

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
            # Rewrite hls_url to route through the backend's HTTPS proxy (avoids mixed-content blocks)
            clean_mac = (stream.get('camera_mac') or '').replace(':', '').lower().strip()
            if clean_mac:
                stream['hls_url'] = f"{proxy_base}/{clean_mac}/index.m3u8"
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

@stream_bp.route('/hls/<path:stream_path>', methods=['GET'])
def proxy_hls_stream(stream_path):
    """
    Proxies HLS manifest and video segments from the MediaMTX server.
    Ensures streams load over HTTPS on hosted websites without browser mixed-content restrictions.
    """
    media_base = os.getenv("CLOUD_MEDIA_URL", "http://104.251.214.177:8888").rstrip("/")
    target_url = f"{media_base}/{stream_path}"
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"
        
    try:
        req = urllib.request.Request(
            target_url,
            headers={
                'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': request.headers.get('Accept', '*/*')
            }
        )
        resp = urllib.request.urlopen(req, timeout=10)
        content_type = resp.headers.get('Content-Type', 'application/vnd.apple.mpegurl')
        
        def generate():
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                yield chunk
                
        response = Response(stream_with_context(generate()), status=resp.status, content_type=content_type)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except urllib.error.HTTPError as he:
        return Response(he.read(), status=he.code, content_type=he.headers.get('Content-Type', 'text/plain; charset=utf-8'))
    except Exception as e:
        return jsonify({"error": f"Stream proxy error: {str(e)}"}), 502

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
