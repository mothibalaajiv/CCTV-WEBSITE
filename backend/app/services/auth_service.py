import bcrypt
from app.repositories.user_repo import UserRepository
from flask_jwt_extended import create_access_token
from app.exceptions import APIError

class AuthService:
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @classmethod
    def authenticate(cls, username, password):
        user = UserRepository.find_by_username(username)
        if not user or not cls.check_password(password, user['password_hash']):
            raise APIError("Invalid credentials", 401)
        
        # Create token with claims
        additional_claims = {"role": user.get("role", "user")}
        access_token = create_access_token(identity=str(user['_id']), additional_claims=additional_claims)
        
        return {
            "token": access_token,
            "user": {
                "id": str(user['_id']),
                "username": user["username"],
                "role": user.get("role"),
                "assigned_sites": user.get("assigned_sites", [])
            }
        }
