# path: src/db/repositories/users.py
# Creado: 2025-11-25
"""
Repositorio para la gestión de usuarios del sistema.
Maneja la colección 'users' y su relación con 'people'.
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from db.connection import get_database
from datetime import datetime

class UsersRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.users

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID."""
        try:
            return self.collection.find_one({"_id": ObjectId(user_id)})
        except:
            return None

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su nombre de usuario (login)."""
        return self.collection.find_one({"username": username})

    def get_by_internal_id(self, internal_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID interno de empleado."""
        return self.collection.find_one({"internal_id": internal_id})

    def get_all_users(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios."""
        query = {"activo": True} if active_only else {}
        return list(self.collection.find(query))

    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Crea un nuevo usuario."""
        user_data["created_at"] = datetime.now()
        user_data["updated_at"] = datetime.now()
        if "activo" not in user_data:
            user_data["activo"] = True
            
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Actualiza los datos de un usuario."""
        updates["updated_at"] = datetime.now()
        result = self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    def delete_user(self, user_id: str) -> bool:
        """Elimina (lógicamente) un usuario."""
        return self.update_user(user_id, {"activo": False})

    def get_users_by_role(self, role_code: str) -> List[Dict[str, Any]]:
        """Obtiene usuarios filtrados por rol."""
        return list(self.collection.find({"rol": role_code, "activo": True}))

_users_repo = None

def get_users_repository() -> UsersRepository:
    global _users_repo
    if _users_repo is None:
        _users_repo = UsersRepository()
    return _users_repo
