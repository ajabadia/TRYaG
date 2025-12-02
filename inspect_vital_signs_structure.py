
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from db import get_database

def inspect_vital_signs_structure():
    try:
        db = get_database()
        collection = db["vital_signs_references"]
        doc = collection.find_one()
        if doc:
            print(f"Keys: {list(doc.keys())}")
            print(f"Sample: {doc}")
        else:
            print("No document found in vital_signs_references")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_vital_signs_structure()
