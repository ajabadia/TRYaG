from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from ..connection import get_database
from ..models_rules import UIField

class UIFieldsRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.ui_fields
        self._ensure_indexes()

    def _ensure_indexes(self):
        # Unique index on internal_name to prevent duplicates
        self.collection.create_index("internal_name", unique=True)

    def get_all_fields(self) -> List[UIField]:
        """Recupera todos los campos."""
        cursor = self.collection.find({}).sort("internal_name", 1)
        return [UIField(**doc) for doc in cursor]

    def get_field_by_name(self, internal_name: str) -> Optional[UIField]:
        doc = self.collection.find_one({"internal_name": internal_name})
        return UIField(**doc) if doc else None

    def upsert_field(self, field: UIField) -> bool:
        """
        Inserta o actualiza un campo basado en internal_name.
        Merges new modules if they differ.
        """
        existing = self.get_field_by_name(field.internal_name)
        
        data = field.model_dump(by_alias=True, exclude={"id", "created_at"})
        data["updated_at"] = datetime.utcnow()
        
        if existing:
            # Merge logic for modules: don't overwrite, append unique
            current_modules = set(existing.modules)
            new_modules = set(field.modules)
            merged_modules = list(current_modules.union(new_modules))
            data["modules"] = merged_modules
            
            # Merge logic for help_text/display_name? 
            # For now, crawler might overwrite descriptions if they change in code?
            # Or better, prioritize DB manual edits? 
            # Strategy: If DB has value, keep it. If DB Empty, take code.
            # But here we are just upserting what comes in.
            
            self.collection.update_one(
                {"internal_name": field.internal_name},
                {"$set": data}
            )
        else:
            data["created_at"] = datetime.utcnow()
            self.collection.insert_one(data)
            
        return True

    def update_field_status(self, internal_name: str, status: str) -> bool:
        """Updates just the status of a field."""
        result = self.collection.update_one(
            {"internal_name": internal_name},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

# Singleton
_repo = None
def get_ui_fields_repository():
    global _repo
    if not _repo:
        _repo = UIFieldsRepository()
    return _repo
