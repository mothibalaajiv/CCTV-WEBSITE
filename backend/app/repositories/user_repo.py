from .base_repo import BaseRepository

class UserRepository(BaseRepository):
    collection_name = 'users'

    @classmethod
    def find_by_username(cls, username):
        return cls.find_one({"username": username})
