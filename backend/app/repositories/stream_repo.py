from .base_repo import BaseRepository

class StreamRepository(BaseRepository):
    collection_name = 'streams'

    @classmethod
    def find_by_camera_code(cls, camera_code):
        return cls.find_one({"camera_code": camera_code})
