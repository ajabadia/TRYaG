# path: src/db/repositories/people.py
# Creado: 2025-11-25
"""
Repositorio para la gestión de personas (anteriormente pacientes).
Maneja la colección 'people'.
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from src.db.connection import get_database
from datetime import datetime

class PeopleRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.people

    def get_by_id(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una persona por su ID."""
        try:
            return self.collection.find_one({"_id": ObjectId(person_id)})
        except:
            return None

    def get_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Busca por número de identificación (DNI, NIE, Pasaporte)."""
        # Buscar en campo legacy o en array de identificaciones
        return self.collection.find_one({
            "$or": [
                {"identification_number": identifier},
                {"identificaciones.value": identifier}
            ]
        })

    def search_by_name(self, query: str, limit: int = 10, active_only: bool = True) -> List[Dict[str, Any]]:
        """Busca personas por nombre o apellido."""
        regex = {"$regex": query, "$options": "i"}
        
        filter_q = {
            "$or": [
                {"nombre": regex},
                {"apellido1": regex},
                {"apellido2": regex},
                {"identification_number": regex},
                {"identificaciones.value": regex},
                {"num_ss": regex},
                {"patient_code": regex}
            ]
        }
        
        if active_only:
            filter_q["activo"] = True
            
        return list(self.collection.find(filter_q).limit(limit))

    def create_person(self, person_data: Dict[str, Any]) -> str:
        """Crea un nuevo registro de persona."""
        person_data["created_at"] = datetime.now()
        person_data["updated_at"] = datetime.now()
        result = self.collection.insert_one(person_data)
        return str(result.inserted_id)

    def update_person(self, person_id: str, updates: Dict[str, Any]) -> bool:
        """Actualiza los datos de una persona."""
        updates["updated_at"] = datetime.now()
        result = self.collection.update_one(
            {"_id": ObjectId(person_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

_people_repo = None

def get_people_repository() -> PeopleRepository:
    global _people_repo
    if _people_repo is None:
        _people_repo = PeopleRepository()
    return _people_repo
