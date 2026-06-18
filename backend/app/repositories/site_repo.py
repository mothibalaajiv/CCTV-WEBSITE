from .base_repo import BaseRepository

class SiteRepository(BaseRepository):
    collection_name = 'sites'

    @classmethod
    def find_by_site_id(cls, site_id):
        return cls.find_one({"site_id": site_id})
