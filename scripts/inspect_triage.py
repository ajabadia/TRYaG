import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from db import get_database
import json
from datetime import datetime

db = get_database()
record = db["triage_records"].find_one({}, sort=[("timestamp", -1)])

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

if record:
    print(json.dumps(record, default=json_serial, indent=2))
else:
    print("No records found")
