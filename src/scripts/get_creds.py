
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.repositories.users import get_users_repository
from db.connection import get_database

if __name__ == "__main__":
    try:
        repo = get_users_repository()
        users = repo.get_all_users()
        print(f"Found {len(users)} users.")
        for u in users:
            print(f"User: {u.get('nombre')} {u.get('apellidos')} | Username: {u.get('username')} | ID: {u.get('internal_id')} | Role: {u.get('rol')}")
    except Exception as e:
        print(f"Error: {e}")
