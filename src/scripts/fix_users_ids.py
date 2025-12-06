
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.repositories.users import get_users_repository

if __name__ == "__main__":
    try:
        repo = get_users_repository()
        users = repo.get_all_users(active_only=False)
        
        count = 0
        for u in users:
            if not u.get('internal_id'):
                print(f"Updating user {u.get('username', 'unknown')}...")
                repo.update_user(u['_id'], {"internal_id": "1234"})
                count += 1
                
        print(f"Fixed {count} users. All users now have internal_id='1234'.")
    except Exception as e:
        print(f"Error: {e}")
