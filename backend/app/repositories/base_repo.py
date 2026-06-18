from bson import ObjectId
from app.extensions import db
from datetime import datetime, timezone

class BaseRepository:
    collection_name = None

    @classmethod
    def get_collection(cls):
        # We need to import db dynamically if it's set later, 
        # but since we initialized it in create_app, it should be available.
        # However, to be safe against circular imports or initialization order,
        # we can fetch it from app.extensions
        from app.extensions import db as current_db
        if current_db is None:
            raise Exception("Database not initialized")
        return current_db[cls.collection_name]

    @classmethod
    def find_all(cls, filter_query=None):
        return list(cls.get_collection().find(filter_query or {}))

    @classmethod
    def find_by_id(cls, object_id):
        if not ObjectId.is_valid(object_id):
            return None
        return cls.get_collection().find_one({"_id": ObjectId(object_id)})

    @classmethod
    def find_one(cls, filter_query):
        return cls.get_collection().find_one(filter_query)

    @classmethod
    def create(cls, data):
        data['created_at'] = datetime.now(timezone.utc)
        result = cls.get_collection().insert_one(data)
        data['_id'] = result.inserted_id
        return data

    @classmethod
    def update(cls, object_id, data):
        if not ObjectId.is_valid(object_id):
            return None
        data['updated_at'] = datetime.now(timezone.utc)
        cls.get_collection().update_one(
            {"_id": ObjectId(object_id)},
            {"$set": data}
        )
        return cls.find_by_id(object_id)

    @classmethod
    def delete(cls, object_id):
        if not ObjectId.is_valid(object_id):
            return False
        result = cls.get_collection().delete_one({"_id": ObjectId(object_id)})
        return result.deleted_count > 0
