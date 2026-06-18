from .base_repo import BaseRepository

class LocalServerRepository(BaseRepository):
    collection_name = 'local_servers'

    @classmethod
    def find_by_server_id(cls, server_id):
        return cls.find_one({"server_id": server_id})
