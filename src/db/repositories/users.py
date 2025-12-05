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

    def increment_failed_attempts(self, user_id: str) -> int:
        """Incrementa el contador de intentos fallidos y devuelve el nuevo valor."""
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$inc": {"failed_login_attempts": 1}},
            return_document=True
        )
        return result.get("failed_login_attempts", 0) if result else 0

    def reset_failed_attempts(self, user_id: str):
        """Resetea el contador de intentos fallidos, nivel de bloqueo y desbloquea."""
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "failed_login_attempts": 0, 
                "locked_until": None,
                "lockout_level": 0
            }}
        )

    def lock_user(self, user_id: str, minutes: int = 30):
        """Bloquea al usuario por un tiempo determinado (Método simple)."""
        from datetime import timedelta
        unlock_time = datetime.now() + timedelta(minutes=minutes)
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"locked_until": unlock_time}}
        )

    def apply_exponential_lockout(self, user_id: str) -> int:
        """
        Aplica bloqueo exponencial: 30min * 2^nivel.
        Incrementa el nivel y resetea el contador de intentos para la próxima ronda.
        Devuelve los minutos de bloqueo aplicados.
        """
        from datetime import timedelta
        
        user = self.get_by_id(user_id)
        if not user:
            return 0
            
        level = user.get("lockout_level", 0)
        minutes = 30 * (2 ** level)
        
        unlock_time = datetime.now() + timedelta(minutes=minutes)
        
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "locked_until": unlock_time,
                "failed_login_attempts": 0 # Resetear para que tenga otros 5 intentos tras desbloqueo
            }, "$inc": {
                "lockout_level": 1
            }}
        )
        return minutes

_users_repo = None

def get_users_repository() -> UsersRepository:
    global _users_repo
    if _users_repo is None:
        _users_repo = UsersRepository()
    return _users_repo
