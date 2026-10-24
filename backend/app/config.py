import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-jwt-secret-key-change-in-production")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/vms_db")
    CLOUD_SERVER_URL = os.getenv("CLOUD_SERVER_URL", "http://104.251.214.177:8000/api/streams")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
    JWT_ACCESS_TOKEN_EXPIRES = 3600 * 24 # 1 day

