import sys
import os
from app import create_app
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService

def set_admin_password(password):
    app = create_app()
    with app.app_context():
        admin = UserRepository.find_by_username("admin")
        hashed = AuthService.hash_password(password)
        if admin:
            UserRepository.update(str(admin["_id"]), {
                "password_hash": hashed,
                "status": "active"
            })
            print(f"SUCCESS: Admin password successfully updated in MongoDB for user 'admin'.")
        else:
            UserRepository.create({
                "username": "admin",
                "password_hash": hashed,
                "role": "admin",
                "assigned_sites": [],
                "status": "active"
            })
            print(f"SUCCESS: Admin user created in MongoDB with the specified password.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pwd = sys.argv[1]
    else:
        pwd = input("Enter new admin password: ").strip()

    if not pwd:
        print("ERROR: Password cannot be empty.")
        sys.exit(1)

    set_admin_password(pwd)
