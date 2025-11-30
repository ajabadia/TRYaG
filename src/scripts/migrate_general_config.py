import os
import sys
from src.db.connection import get_database

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def migrate_config():
    print("--- Migrating General Config ---")
    db = get_database()
    collection = db["general_config"]
    CONFIG_ID = "app_general_config"
    
    config = collection.find_one({"_id": CONFIG_ID})
    if not config:
        print("Config not found. Nothing to migrate.")
        return

    print(f"Current config keys: {list(config.keys())}")
    
    updates = {}
    unset = {}
    
    # Determine default model from existing values or default
    current_triage = config.get("model_triage")
    current_transcription = config.get("model_transcription")
    
    # Prefer triage model, then transcription, then default
    new_default = current_triage or current_transcription or "gemini-2.5-flash"
    
    if "default_ai_model" not in config:
        print(f"Setting default_ai_model to: {new_default}")
        updates["default_ai_model"] = new_default
    
    # Remove old keys
    if "model_triage" in config:
        unset["model_triage"] = ""
    if "model_transcription" in config:
        unset["model_transcription"] = ""
        
    update_op = {}
    if updates:
        update_op["$set"] = updates
    if unset:
        update_op["$unset"] = unset
        
    if update_op:
        collection.update_one({"_id": CONFIG_ID}, update_op)
        print("Migration completed successfully.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    migrate_config()
