# path: scripts/inspect_vital_signs_db.py
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.repositories.vital_signs_repo import VitalSignsRepository

def inspect_db():
    print("Inspecting Vital Signs DB...")
    repo = VitalSignsRepository()
    refs = repo.get_all_references()
    
    for ref in refs:
        print(f"\n--- {ref.name} ({ref.key}) ---")
        for cfg in ref.configs:
            print(f"  Age: {cfg.min_age}-{cfg.max_age}")
            print(f"  Ranges:")
            # Sort ranges by priority for easier reading
            sorted_ranges = sorted(cfg.ranges, key=lambda x: x.priority)
            for r in sorted_ranges:
                print(f"    [{r.color.upper()}] {r.min_val} - {r.max_val} ({r.label})")

if __name__ == "__main__":
    inspect_db()
