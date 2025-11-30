import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.db.connection import get_database

def update_prompts_model():
    db = get_database()
    collection = db["prompts"]
    
    # Default model requested by user
    DEFAULT_MODEL = "gemini-2.5-flash"
    
    print(f"Updating prompts to use default model: {DEFAULT_MODEL}")
    
    prompts = collection.find({})
    count = 0
    
    for prompt in prompts:
        updated = False
        versions = prompt.get("versions", [])
        new_versions = []
        
        for v in versions:
            if "model" not in v or not v["model"] or v["model"] == "gemini-1.5-flash":
                v["model"] = DEFAULT_MODEL
                updated = True
            new_versions.append(v)
            
        if updated:
            collection.update_one(
                {"_id": prompt["_id"]},
                {"$set": {"versions": new_versions, "updated_at": datetime.now()}}
            )
            count += 1
            print(f"Updated prompt type: {prompt.get('prompt_type')}")
            
    print(f"Migration completed. Updated {count} prompt documents.")

if __name__ == "__main__":
    update_prompts_model()
