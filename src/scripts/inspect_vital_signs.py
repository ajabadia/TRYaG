# path: src/scripts/inspect_vital_signs.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from db.repositories.vital_signs_repo import VitalSignsRepository

def inspect():
    repo = VitalSignsRepository()
    refs = repo.get_all_references()
    
    print(f"Found {len(refs)} references.")
    
    for ref in refs:
        print(f"\n--- {ref.name} ({ref.key}) ---")
        for cfg in ref.configs:
            print(f"  Age: {cfg.min_age}-{cfg.max_age}")
            print(f"  Ranges: {len(cfg.ranges)}")
            for r in cfg.ranges:
                print(f"    - {r.label}: {r.min_val}-{r.max_val} ({r.color})")

if __name__ == "__main__":
    inspect()
