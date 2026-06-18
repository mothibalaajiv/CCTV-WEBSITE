from app import create_app
from app.repositories.user_repo import UserRepository
from app.repositories.site_repo import SiteRepository
from app.repositories.server_repo import LocalServerRepository
from app.repositories.camera_repo import CameraRepository
from app.services.auth_service import AuthService
from pymongo import MongoClient
import os

app = create_app()

def seed_data():
    with app.app_context():
        # Clear existing
        UserRepository.get_collection().delete_many({})
        SiteRepository.get_collection().delete_many({})
        LocalServerRepository.get_collection().delete_many({})
        CameraRepository.get_collection().delete_many({})
        
        # Streams collection
        db = MongoClient(os.getenv("MONGO_URI")).get_database()
        if "streams" in db.list_collection_names():
            db.streams.delete_many({})

        print("Cleared existing data.")

        # Seed Users
        admin_pass = AuthService.hash_password("admin")
        security_pass = AuthService.hash_password("security")
        
        admin_id = UserRepository.create({
            "username": "admin",
            "password_hash": admin_pass,
            "role": "admin",
            "assigned_sites": [],
            "status": "active"
        })['_id']
        
        security_id = UserRepository.create({
            "username": "security",
            "password_hash": security_pass,
            "role": "security",
            "assigned_sites": [],
            "status": "active"
        })['_id']

        print("Created Users.")

        # Seed Local Servers
        server1 = LocalServerRepository.create({
            "server_id": "200001",
            "mac_address": "0A:45:6E:12:9B:F0",
            "is_active": True
        })
        
        server2 = LocalServerRepository.create({
            "server_id": "200002",
            "mac_address": "0A:45:6E:12:9B:F1",
            "is_active": True
        })

        print("Created Local Servers.")

        # Seed Sites
        site1 = SiteRepository.create({
            "site_id": "SITE1",
            "site_name": "SAKTHI MASALA FACTORY A",
            "local_server_id": "200001",
            "status": "active"
        })
        
        site2 = SiteRepository.create({
            "site_id": "SITE2",
            "site_name": "SAKTHI MASALA FACTORY B",
            "local_server_id": "200002",
            "status": "active"
        })
        
        # Assign site to user
        UserRepository.update(str(admin_id), {"assigned_sites": ["SITE1", "SITE2"]})
        UserRepository.update(str(security_id), {"assigned_sites": ["SITE1"]})

        print("Created Sites and Assigned Users.")

        # Seed Cameras
        cam1 = CameraRepository.create({
            "camera_code": "100001",
            "mac_address": "02:11:22:33:44:55",
            "location_name": "Main Gate",
            "current_site": "SITE1",
            "current_ip": "192.168.1.101",
            "stream_status": "active",
            "is_active": True
        })
        
        cam2 = CameraRepository.create({
            "camera_code": "100002",
            "mac_address": "02:11:22:33:44:56",
            "location_name": "Loading Bay",
            "current_site": "SITE1",
            "current_ip": "192.168.1.102",
            "stream_status": "active",
            "is_active": True
        })
        
        cam3 = CameraRepository.create({
            "camera_code": "100003",
            "mac_address": "02:11:22:33:44:57",
            "location_name": "unknown",
            "current_site": "SITE2",
            "current_ip": "192.168.1.103",
            "stream_status": "active",
            "is_active": True
        })

        print("Created Cameras.")

        # Seed Streams
        db.streams.insert_many([
            {
                "camera_code": "100001",
                "hls_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "status": "active",
                "local_server_mac": "0A:45:6E:12:9B:F0"
            },
            {
                "camera_code": "100002",
                "hls_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "status": "active",
                "local_server_mac": "0A:45:6E:12:9B:F0"
            },
            {
                "camera_code": "100003",
                "hls_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "status": "active",
                "local_server_mac": "0A:45:6E:12:9B:F1"
            }
        ])

        print("Created Streams.")
        print("Done!")

if __name__ == "__main__":
    seed_data()
