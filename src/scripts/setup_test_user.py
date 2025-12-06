
import sys
import os
from bson import ObjectId

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.repositories.users import get_users_repository

if __name__ == "__main__":
    try:
        repo = get_users_repository()
        users = repo.get_all_users()
        
        target_user = None
        if users:
            target_user = users[0]
            print(f"Updating user {target_user.get('username')}...")
            repo.update_user(target_user['_id'], {"internal_id": "1234", "nombre": "Test", "apellidos": "User", "rol": "medico"})
            print("User updated. Login with: 'Test User' -> ID: 1234")
        else:
            print("No users found. Creating one...")
            uid = repo.create_user({
                "username": "testdoc",
                "nombre": "Test",
                "apellidos": "Doctor",
                "rol": "medico",
                "internal_id": "1234",
                "activo": True
            })
            print(f"User created. Login with: 'Test Doctor' -> ID: 1234")
            
    except Exception as e:
        print(f"Error: {e}")
