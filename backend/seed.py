from app import create_app
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService

app = create_app()

with app.app_context():
    # Check if admin exists
    if not UserRepository.find_by_username("admin"):
        UserRepository.create({
            "username": "admin",
            "password_hash": AuthService.hash_password("admin"),
            "role": "admin",
            "status": "active"
        })
        print("Admin user created")
    else:
        print("Admin user already exists")
    
    # Check if security exists
    if not UserRepository.find_by_username("security"):
        UserRepository.create({
            "username": "security",
            "password_hash": AuthService.hash_password("security"),
            "role": "security",
            "status": "active"
        })
        print("Security user created")
    else:
        print("Security user already exists")
