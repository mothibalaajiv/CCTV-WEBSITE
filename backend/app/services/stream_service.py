from app.repositories.stream_repo import StreamRepository
from app.exceptions import APIError
from datetime import datetime, timezone

import urllib.request
import urllib.parse
import json
import os

class StreamService:
    @classmethod
    def register_stream(cls, data):
        stream = StreamRepository.find_by_camera_code(data['camera_code'])
        stream_data = {
            "camera_code": data['camera_code'],
            "stream_name": data.get('stream_name', data['camera_code']),
            "hls_url": data['hls_url'],
            "status": "active",
            "last_seen": datetime.now(timezone.utc)
        }

        if stream:
            updated = StreamRepository.update(stream['_id'], stream_data)
            updated['_id'] = str(updated['_id'])
            return updated
        else:
            new_stream = StreamRepository.create(stream_data)
            new_stream['_id'] = str(new_stream['_id'])
            return new_stream

    @classmethod
    def pause_stream(cls, camera_code):
        stream = StreamRepository.find_by_camera_code(camera_code)
        if not stream:
            raise APIError("Stream not found", 404)
            
        updated = StreamRepository.update(stream['_id'], {"status": "paused"})
        updated['_id'] = str(updated['_id'])
        return updated

    @classmethod
    def resume_stream(cls, camera_code):
        stream = StreamRepository.find_by_camera_code(camera_code)
        if not stream:
            raise APIError("Stream not found", 404)
            
        updated = StreamRepository.update(stream['_id'], {"status": "active"})
        updated['_id'] = str(updated['_id'])
        return updated

    @classmethod
    def get_all_streams(cls):
        cloud_url = os.getenv("CLOUD_STREAMS_URL", os.getenv("CLOUD_SERVER_URL", "http://104.251.214.177:8000/api/streams"))
        if "/api/diagnostics" in cloud_url:
            cloud_url = cloud_url.replace("/api/diagnostics", "/api/streams")
        elif not cloud_url.endswith("/api/streams"):
            cloud_url = cloud_url.rstrip("/") + "/api/streams"
            
        try:
            req = urllib.request.Request(cloud_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                cloud_data = json.loads(response.read().decode()).get('streams', [])
        except Exception as e:
            print(f"Error fetching streams: {e}")
            cloud_data = []

        # Fallback: If cloud streams endpoint returned nothing, construct active streams from diagnostics
        if not cloud_data:
            from app.utils.telemetry import fetch_cloud_diagnostics, parse_timestamp, is_telemetry_fresh
            diags = fetch_cloud_diagnostics()
            now_utc = datetime.now(timezone.utc)
            all_ts = [parse_timestamp(d.get('timestamp')) for d in diags]
            max_ts = max(all_ts) if all_ts else None
            for d in diags:
                d_time = parse_timestamp(d.get('timestamp'))
                if is_telemetry_fresh(d_time, now_utc, max_ts, window_seconds=300):
                    s_mac = d.get('local_server_mac', '')
                    for cam in d.get('cameras', []):
                        c_mac = cam.get('camera_mac', '')
                        clean_mac = c_mac.replace(':', '').lower()
                        cloud_data.append({
                            "local_server_mac": s_mac,
                            "local_server_ip": d.get('local_server_ip', 'unknown'),
                            "camera_mac": c_mac,
                            "camera_ip": cam.get('camera_ip'),
                            "hls_url": f"http://104.251.214.177:8888/{clean_mac}/index.m3u8"
                        })

        from app.repositories.camera_repo import CameraRepository
        from app.repositories.server_repo import LocalServerRepository
        from app.repositories.stream_repo import StreamRepository
        
        all_cameras = list(CameraRepository.find_all())
        all_servers = list(LocalServerRepository.find_all())
        
        seen_cameras = set()
        valid_streams = []
        
        # Sort so that streams from the active local server are processed first
        active_server_macs = [srv.get('mac_address', '').lower() for srv in all_servers if srv.get('is_active')]
        cloud_data_sorted = sorted(
            cloud_data, 
            key=lambda s: 0 if (s.get('local_server_mac') or '').lower() in active_server_macs else 1
        )
        
        for s in cloud_data_sorted:
            camera_mac = (s.get('camera_mac') or '').lower()
            server_mac = s.get('local_server_mac')
            
            if not camera_mac or not server_mac:
                continue
                
            # 1. Check if camera is registered (checking mac_address and mac_aliases case-insensitively)
            camera = next((
                c for c in all_cameras 
                if (c.get('mac_address') or '').lower() == camera_mac 
                or camera_mac in [(a or '').lower() for a in c.get('mac_aliases', [])]
            ), None)
            
            if not camera or not camera.get('is_active'):
                continue
                
            camera_code = camera.get('camera_code')
            if camera_code in seen_cameras:
                continue
                
            # 2. Check if local server MAC is registered or fallback to active registered server
            server = next((srv for srv in all_servers if srv.get('mac_address', '').lower() == server_mac.lower() and srv.get('is_active')), None)
            if not server:
                server = next((srv for srv in all_servers if srv.get('is_active')), None)
            if not server:
                continue
                
            hls_url = s.get('hls_url')
            if not hls_url:
                continue

            existing_stream = StreamRepository.find_by_camera_code(camera_code)
            
            stream_data = {
                "camera_code": camera_code,
                "stream_name": camera.get('location_name', camera_code),
                "hls_url": hls_url,
                "local_server_mac": server_mac,
                "camera_mac": camera.get('mac_address', camera_mac),
                "camera_ip": s.get('camera_ip') or camera.get('current_ip'),
                "last_seen": datetime.now(timezone.utc)
            }
            
            if existing_stream:
                stream_data["status"] = existing_stream.get("status", "active")
                updated = StreamRepository.update(existing_stream['_id'], stream_data)
                updated['_id'] = str(updated['_id'])
                valid_streams.append(updated)
            else:
                stream_data["status"] = "active"
                new_stream = StreamRepository.create(stream_data)
                new_stream['_id'] = str(new_stream['_id'])
                valid_streams.append(new_stream)
                
            seen_cameras.add(camera_code)
            
        return valid_streams
