import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.db.repositories.triage import get_triage_repository
import pymongo

def inspect_records():
    repo = get_triage_repository()
    print("Connecting to TriageRepository...")
    
    # Get last 5 records
    records = repo.find_all(sort=[("timestamp", pymongo.DESCENDING)], limit=5)
    
    print(f"Found {len(records)} records.")
    for r in records:
        print(f"Audit ID: {r.get('audit_id')}")
        print(f"  Patient ID: {r.get('patient_id')}")
        print(f"  Timestamp: {r.get('timestamp')}")
        print("-" * 20)

if __name__ == "__main__":
    inspect_records()
