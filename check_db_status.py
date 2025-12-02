
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from db.connection import get_database

def check_counts():
    db = get_database()
    
    collections = {
        "audit_log": db.audit_log,
        "vital_signs_references": db.vital_signs_references,
        "patient_flow": db.patient_flow,
        "people": db.people,
        "users": db.users
    }
    
    print("--- Database Counts ---")
    for name, col in collections.items():
        count = col.count_documents({})
        print(f"{name}: {count}")
        
        if name == "vital_signs_references" and count > 0:
            print("  Sample Vital Sign:", col.find_one({}, {'_id': 0, 'parametro': 1}))

if __name__ == "__main__":
    check_counts()
