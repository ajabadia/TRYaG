# path: src/scripts/check_login_logs.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.connection import get_database
from pprint import pprint

def check_logs():
    db = get_database()
    
    # List collections
    collections = db.list_collection_names()
    print(f"Collections found: {collections}")
    
    if "login_logs" not in collections:
        print("❌ Collection 'login_logs' DOES NOT EXIST.")
    else:
        print("✅ Collection 'login_logs' exists.")
        
        count = db.login_logs.count_documents({})
        print(f"Total documents in login_logs: {count}")
        
        if count > 0:
            print("Last 5 logs:")
            cursor = db.login_logs.find().sort("timestamp", -1).limit(5)
            for doc in cursor:
                pprint(doc)
        else:
            print("⚠️ Collection is empty.")

if __name__ == "__main__":
    check_logs()
