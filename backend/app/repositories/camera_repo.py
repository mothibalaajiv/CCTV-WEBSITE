from .base_repo import BaseRepository

class CameraRepository(BaseRepository):
    collection_name = 'cameras'

    @classmethod
    def find_by_code(cls, camera_code):
        return cls.find_one({"camera_code": camera_code})

    @classmethod
    def find_by_mac(cls, mac_address):
        return cls.find_one({"mac_address": mac_address})

    @classmethod
    def find_by_site(cls, site_id):
        return cls.find_all({"current_site": site_id})
