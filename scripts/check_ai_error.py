import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.db.connection import get_database
import pymongo
from pprint import pprint

def check_latest_error():
    db = get_database()
    repo = db.get_collection("ai_audit_logs")
    
    # Buscar el último log de shift_handoff
    last_log = repo.find_one(
        {"prompt_type": "shift_handoff"},
        sort=[("timestamp_start", pymongo.DESCENDING)]
    )
    
    if last_log:
        print("--- ÚLTIMO INTENTO SHIFT HANDOFF ---")
        print(f"Timestamp: {last_log.get('timestamp_start')}")
        print(f"Status: {last_log.get('status')}")
        print(f"Model: {last_log.get('model_name')}")
        print(f"Error Msg: {last_log.get('error_msg')}")
        print("-" * 30)
    else:
        print("No se encontraron logs de shift_handoff.")

if __name__ == "__main__":
    check_latest_error()
