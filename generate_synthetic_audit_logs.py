import os
import sys
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
import uuid

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from db.connection import get_database

def generate_synthetic_audit_logs(num_records=50):
    print("Connecting to database using shared connection logic...")
    db = get_database()
    collection = db['audit_logs']

    actions = ["Login", "Triage", "Consultation", "Patient Update", "Logout", "View Record"]
    decisions = ["Alta", "Ingreso", "Derivación", "Observación", "Rechazo"]
    users = ["admin", "doctor1", "nurse1", "recepcion"]
    modules = ["Auth", "Triage", "Consultation", "Admission"]

    records = []
    base_time = datetime.now()

    print(f"Generating {num_records} synthetic audit records...")

    for i in range(num_records):
        timestamp = base_time - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        action = random.choice(actions)
        user = random.choice(users)
        module = random.choice(modules)
        
        decision = None
        if action in ["Triage", "Consultation"]:
            decision = random.choice(decisions)

        record = {
            "timestamp": timestamp,
            "audit_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
            "decision_humana": decision,
            "detalles": {
                "action": action,
                "user": user,
                "module": module,
                "details": f"Synthetic action {action} by {user}"
            },
            "is_synthetic": True
        }
        records.append(record)

    if records:
        collection.insert_many(records)
        print(f"Successfully inserted {len(records)} records into 'audit_logs'.")
    else:
        print("No records generated.")

if __name__ == "__main__":
    generate_synthetic_audit_logs()
