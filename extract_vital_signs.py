
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from db import get_database

def extract_vital_signs_refs():
    with open('vital_signs_dump.txt', 'w', encoding='utf-8') as f:
        try:
            db = get_database()
            collection = db["vital_signs_references"]
            
            # Get all options
            options = list(collection.find().sort([("param_name", 1)]))
            
            f.write("=== VITAL SIGNS REFERENCES ANNEX ===\n")
            
            for opt in options:
                name = opt.get('param_name', 'Unknown')
                ranges = opt.get('ranges', [])
                
                f.write(f"\n## {name}\n")
                for r in ranges:
                    f.write(f"- {r}\n")
                
        except Exception as e:
            f.write(f"Error extracting options: {e}\n")

if __name__ == "__main__":
    extract_vital_signs_refs()
