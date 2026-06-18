from app.repositories.stream_repo import StreamRepository
from app.exceptions import APIError
from datetime import datetime, timezone

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
        streams = StreamRepository.find_all()
        from app.repositories.camera_repo import CameraRepository
        from app.repositories.server_repo import LocalServerRepository
        
        valid_streams = []
        for s in streams:
            # 1. Check if camera is registered
            camera = CameraRepository.find_by_camera_code(s.get('camera_code'))
            if not camera or not camera.get('mac_address'):
                continue
                
            # 2. Check if local server MAC is registered
            server_mac = s.get('local_server_mac')
            if not server_mac:
                continue
            server = LocalServerRepository.find_one({"mac_address": server_mac})
            if not server:
                continue
                
            s['_id'] = str(s['_id'])
            valid_streams.append(s)
            
        return valid_streams
