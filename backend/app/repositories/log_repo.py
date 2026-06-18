from .base_repo import BaseRepository

class MigrationRepository(BaseRepository):
    collection_name = 'camera_migrations'

class NotificationRepository(BaseRepository):
    collection_name = 'notifications'

class AuditRepository(BaseRepository):
    collection_name = 'audit_logs'

class ActivityRepository(BaseRepository):
    collection_name = 'activity_logs'
