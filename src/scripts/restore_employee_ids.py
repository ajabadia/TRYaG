
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.repositories.users import get_users_repository

if __name__ == "__main__":
    try:
        repo = get_users_repository()
        users = repo.get_all_users()
        
        # Sort users by ID (creation time usually) to ensure deterministic assignment
        # Assuming ObjectIds are sortable by time
        users.sort(key=lambda u: u['_id'])
        
        print(f"Found {len(users)} users. Restoring IDs...")
        
        for i, user in enumerate(users):
            new_id = f"EMP{i+1:03d}" # EMP001, EMP002...
            
            # Update
            repo.update_user(user['_id'], {
                "internal_id": new_id
            })
            
            role_code = user.get('rol', 'N/A')
            name = f"{user.get('nombre', '')} {user.get('apellidos', '')}".strip()
            print(f"User: {name} ({role_code}) -> New ID: {new_id}")

        print("All user IDs restored to EMPxxx pattern.")

    except Exception as e:
        print(f"Error: {e}")
