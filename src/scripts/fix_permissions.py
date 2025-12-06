
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.repositories.users import get_users_repository
from db.connection import get_database

if __name__ == "__main__":
    try:
        # 1. Inspect Roles
        db = get_database()
        roles_coll = db.roles
        roles = list(roles_coll.find({}))
        print("Available Roles:")
        for r in roles:
            print(f"- {r.get('code')} ({r.get('nombre')})")
            
        print("-" * 30)

        # 2. Fix User
        repo = get_users_repository()
        users = repo.get_all_users()
        
        target = users[0]
        print(f"Targeting User: {target.get('nombre')} {target.get('apellidos')} ({target.get('_id')})")
        
        # Explicitly set to Super Admin
        admin_role = "superadministrador"
        
        print(f"Applying Role: {admin_role}")
        
        repo.update_user(target['_id'], {
            "rol": admin_role,
            "nombre": "Usuario",
            "apellidos": "Principal (Restaurado)",
            "internal_id": "1234" # Ensure password matches what we told the user
        })
        
        print("Permissions restored. Name updated.")

    except Exception as e:
        print(f"Error: {e}")
