from app.repositories.user_repo import UserRepository
from app.repositories.site_repo import SiteRepository
from app.repositories.camera_repo import CameraRepository
from app.repositories.stream_repo import StreamRepository
from app.repositories.server_repo import LocalServerRepository
from app.repositories.log_repo import MigrationRepository
from datetime import datetime, timezone

class SystemService:
    @classmethod
    def get_dashboard_stats(cls):
        recent_migrations = MigrationRepository.find_all()
        # Sort manually since BaseRepository find_all doesn't have sort param yet
        recent_migrations.sort(key=lambda x: x.get('moved_at', datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
        recent_migrations = recent_migrations[:5] # Get top 5

        for rm in recent_migrations:
            rm['_id'] = str(rm['_id'])

        return {
            "total_users": len(UserRepository.find_all()),
            "total_sites": len(SiteRepository.find_all()),
            "total_cameras": len(CameraRepository.find_all()),
            "active_streams": len(StreamRepository.find_all({"status": "active"})),
            "total_servers": len(LocalServerRepository.find_all()),
            "recent_movements": recent_migrations
        }

    @classmethod
    def process_heartbeat(cls, server_id):
        server = LocalServerRepository.find_by_server_id(server_id)
        if server:
            LocalServerRepository.update(server['_id'], {"last_seen": datetime.now(timezone.utc), "status": "online"})
            return {"status": "updated"}
        else:
            new_server = LocalServerRepository.create({
                "server_id": server_id,
                "status": "online",
                "last_seen": datetime.now(timezone.utc)
            })
            return {"status": "created", "id": str(new_server['_id'])}
