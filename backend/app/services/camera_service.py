from app.repositories.camera_repo import CameraRepository
from app.repositories.site_repo import SiteRepository
from app.repositories.log_repo import MigrationRepository
from app.exceptions import APIError
from datetime import datetime, timezone

class CameraService:
    @classmethod
    def register_camera(cls, data):
        # Generate 1-series camera_code
        all_cameras = CameraRepository.find_all()
        max_code = 100000
        for c in all_cameras:
            try:
                code = int(c.get('camera_code', 0))
                if 100000 <= code < 200000 and code > max_code:
                    max_code = code
            except ValueError:
                pass
                
        new_camera_code = str(max_code + 1)
        
        if CameraRepository.find_by_mac(data['mac_address']):
            raise APIError("MAC address already registered", 400)

        camera_data = {
            "camera_code": new_camera_code,
            "mac_address": data['mac_address'],
            "location_name": "unknown",
            "current_site": data.get('current_site'),
            "current_ip": data.get('current_ip'),
            "stream_status": "offline",
            "is_active": True
        }
        
        camera = CameraRepository.create(camera_data)
        camera['_id'] = str(camera['_id'])
        return camera

    @classmethod
    def get_all_cameras(cls):
        cameras = CameraRepository.find_all()
        for c in cameras:
            c['_id'] = str(c['_id'])
        return cameras

    @classmethod
    def update_camera_site(cls, camera_code, new_site_id):
        # Migration Engine logic
        camera = CameraRepository.find_by_code(camera_code)
        if not camera:
            raise APIError("Camera not found", 404)
            
        old_site = camera.get('current_site')
        if old_site == new_site_id:
            return camera # No change

        if new_site_id and not SiteRepository.find_by_site_id(new_site_id):
            raise APIError("New site does not exist", 400)

        # Record migration history
        migration_data = {
            "camera_code": camera_code,
            "old_site": old_site,
            "new_site": new_site_id,
            "moved_at": datetime.now(timezone.utc)
        }
        MigrationRepository.create(migration_data)
        
        # Update camera
        updated = CameraRepository.update(camera['_id'], {"current_site": new_site_id})
        updated['_id'] = str(updated['_id'])
        return updated

    @classmethod
    def update_camera(cls, camera_id, data):
        camera = CameraRepository.find_by_id(camera_id)
        if not camera:
            raise APIError("Camera not found", 404)

        update_data = {}
        if 'location_name' in data:
            update_data['location_name'] = data['location_name']
        if 'current_site' in data:
            return cls.update_camera_site(camera['camera_code'], data['current_site'])

        if update_data:
            updated = CameraRepository.update(camera_id, update_data)
            updated['_id'] = str(updated['_id'])
            return updated
        return camera

    @classmethod
    def update_camera_location_by_code(cls, camera_code, location_name):
        camera = CameraRepository.find_by_code(camera_code)
        if not camera:
            raise APIError("Camera not found", 404)
        
        updated = CameraRepository.update(camera['_id'], {"location_name": location_name})
        if updated:
            updated['_id'] = str(updated['_id'])
            return updated
        return camera

    @classmethod
    def set_camera_status(cls, camera_id, is_active):
        updated = CameraRepository.update(camera_id, {"is_active": is_active})
        if updated:
            updated['_id'] = str(updated['_id'])
        return updated

    @classmethod
    def delete_camera(cls, camera_id):
        CameraRepository.delete(camera_id)
        return True
