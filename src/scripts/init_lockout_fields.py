# path: src/scripts/init_lockout_fields.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.connection import get_database

def init_fields():
    db = get_database()
    print("Inicializando campos de bloqueo en usuarios...")
    
    # Update all users that don't have the fields
    result = db.users.update_many(
        {},
        {
            "$set": {
                "failed_login_attempts": 0,
                "lockout_level": 0,
                "locked_until": None
            }
        }
    )
    
    print(f"Actualizados {result.modified_count} usuarios.")
    print("Campos inicializados: failed_login_attempts=0, lockout_level=0, locked_until=None")

if __name__ == "__main__":
    init_fields()
