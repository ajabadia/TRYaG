# path: src/scripts/inspect_users_lockout.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.connection import get_database
from pprint import pprint

def inspect_users():
    db = get_database()
    users = list(db.users.find({}, {
        "username": 1, 
        "failed_login_attempts": 1, 
        "lockout_level": 1, 
        "locked_until": 1
    }))
    
    print(f"Found {len(users)} users.")
    for u in users:
        pprint(u)

if __name__ == "__main__":
    inspect_users()
