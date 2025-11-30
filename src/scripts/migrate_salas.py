import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db.connection import get_database
from bson import ObjectId

def migrate_salas():
    print("Starting migration of salas...")
    db = get_database()
    centros_col = db["centros"]
    salas_col = db["salas"]
    
    centros = list(centros_col.find({}))
    print(f"Found {len(centros)} centers.")
    
    for centro in centros:
        centro_id = str(centro["_id"])
        salas_list = centro.get("salas", [])
        
        if not salas_list:
            print(f"Center {centro.get('denominacion')} has no embedded salas.")
            continue
            
        print(f"Migrating {len(salas_list)} salas for center {centro.get('denominacion')}...")
        
        for sala in salas_list:
            sala_code = sala.get("codigo")
            
            if not sala_code:
                print("Skipping sala without code.")
                continue
            
            # 1. Start with embedded data (contains details like equipamiento, horarios)
            final_sala = sala.copy()
            
            # 2. Check if exists in separate collection (might have newer basic info)
            existing_doc = salas_col.find_one({"codigo": sala_code})
            
            if existing_doc:
                print(f"  - Merging existing data for {sala_code}")
                # Update with fields from existing doc, excluding _id
                for k, v in existing_doc.items():
                    if k != "_id":
                        final_sala[k] = v
            
            # 3. Ensure centro_id is set
            final_sala["centro_id"] = centro_id
            
            # 4. Ensure timestamps
            if "created_at" not in final_sala:
                final_sala["created_at"] = datetime.now()
            final_sala["updated_at"] = datetime.now()
            final_sala["updated_by"] = "migration_script"
            
            # 5. Upsert
            salas_col.update_one(
                {"codigo": sala_code},
                {"$set": final_sala},
                upsert=True
            )
            print(f"  - Migrated/Updated {sala_code}")

        # 6. Remove salas array from centro
        centros_col.update_one(
            {"_id": centro["_id"]},
            {"$unset": {"salas": ""}}
        )
        print(f"Removed embedded salas from center {centro.get('denominacion')}.")

    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate_salas()
