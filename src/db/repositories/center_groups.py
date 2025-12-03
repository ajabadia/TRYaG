# path: src/db/repositories/center_groups.py
from typing import List, Optional, Dict, Any
from db.connection import get_database
from db.models import CenterGroup
from datetime import datetime
from bson import ObjectId

class CenterGroupRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["center_groups"]

    def get_all(self) -> List[CenterGroup]:
        """Obtiene todos los grupos de centros."""
        cursor = self.collection.find()
        return [CenterGroup(**doc) for doc in cursor]

    def get_by_id(self, group_id: str) -> Optional[CenterGroup]:
        """Obtiene un grupo por su ID."""
        try:
            doc = self.collection.find_one({"_id": ObjectId(group_id)})
            return CenterGroup(**doc) if doc else None
        except Exception:
            return None

    def create(self, group: CenterGroup) -> str:
        """Crea un nuevo grupo."""
        doc = group.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def update(self, group_id: str, updates: Dict[str, Any]) -> bool:
        """Actualiza un grupo existente."""
        updates["updated_at"] = datetime.now()
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(group_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception:
            return False

    def delete(self, group_id: str) -> bool:
        """Elimina un grupo."""
        try:
            result = self.collection.delete_one({"_id": ObjectId(group_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    def add_center_to_group(self, group_id: str, center_id: str) -> bool:
        """Añade un centro a un grupo."""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(group_id)},
                {"$addToSet": {"center_ids": center_id}, "$set": {"updated_at": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception:
            return False

    def remove_center_from_group(self, group_id: str, center_id: str) -> bool:
        """Elimina un centro de un grupo."""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(group_id)},
                {"$pull": {"center_ids": center_id}, "$set": {"updated_at": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception:
            return False

_repo_instance = None

def get_center_group_repository() -> CenterGroupRepository:
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = CenterGroupRepository()
    return _repo_instance
