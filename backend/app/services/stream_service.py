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
        cloud_url = os.getenv("CLOUD_SERVER_URL", "http://104.251.214.177:8000/api/streams")
        try:
            req = urllib.request.Request(cloud_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                cloud_data = json.loads(response.read().decode()).get('streams', [])
        except Exception as e:
            print(f"Error fetching streams: {e}")
            cloud_data = []

        from app.repositories.camera_repo import CameraRepository
        from app.repositories.server_repo import LocalServerRepository
        from app.repositories.stream_repo import StreamRepository
        
        valid_streams = []
        for s in cloud_data:
            camera_mac = s.get('camera_mac')
            server_mac = s.get('local_server_mac')
            
            if not camera_mac or not server_mac:
                continue
                
            # 1. Check if camera is registered
            camera = CameraRepository.find_one({"mac_address": camera_mac})
            if not camera or not camera.get('is_active'):
                continue
                
            # 2. Check if local server MAC is registered or fallback to active registered server
            all_servers = list(LocalServerRepository.find_all())
            server = next((srv for srv in all_servers if srv.get('mac_address', '').lower() == server_mac.lower() and srv.get('is_active')), None)
            if not server:
                server = next((srv for srv in all_servers if srv.get('is_active')), None)
            if not server:
                continue
                
            hls_url = s.get('hls_url')
            if not hls_url:
                continue

            camera_code = camera.get('camera_code')
            existing_stream = StreamRepository.find_by_camera_code(camera_code)
            
            stream_data = {
                "camera_code": camera_code,
                "stream_name": camera.get('location_name', camera_code),
                "hls_url": hls_url,
                "local_server_mac": server_mac,
                "camera_mac": camera_mac,
                "camera_ip": s.get('camera_ip'),
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
            
        return valid_streams
