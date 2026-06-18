from app.repositories.user_repo import UserRepository
from app.exceptions import APIError
from app.services.auth_service import AuthService

class UserService:
    @classmethod
    def create_user(cls, data):
        if UserRepository.find_by_username(data['username']):
            raise APIError("Username already exists", 400)
            
        password_hash = AuthService.hash_password(data['password'])
        
        user_data = {
            "username": data['username'],
            "password_hash": password_hash,
            "role": data.get('role', 'user'),
            "assigned_sites": data.get('assigned_sites', []),
            "status": "active"
        }
        
        user = UserRepository.create(user_data)
        user['_id'] = str(user['_id'])
        del user['password_hash']
        return user

    @classmethod
    def get_all_users(cls):
        users = UserRepository.find_all()
        for u in users:
            u['_id'] = str(u['_id'])
            u.pop('password_hash', None)
        return users

    @classmethod
    def get_user(cls, user_id):
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise APIError("User not found", 404)
        user['_id'] = str(user['_id'])
        user.pop('password_hash', None)
        return user

    @classmethod
    def update_user(cls, user_id, data):
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise APIError("User not found", 404)
        
        update_data = {}
        if 'role' in data: update_data['role'] = data['role']
        if 'assigned_sites' in data: update_data['assigned_sites'] = data['assigned_sites']
        if 'status' in data: update_data['status'] = data['status']
        if 'password' in data and data['password']:
            update_data['password_hash'] = AuthService.hash_password(data['password'])
            
        UserRepository.update(user_id, update_data)
        return True

    @classmethod
    def delete_user(cls, user_id):
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise APIError("User not found", 404)
        UserRepository.delete(user_id)
        return True
