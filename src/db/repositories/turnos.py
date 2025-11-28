from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from db.connection import get_database
from db.models import Turno

class TurnosRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["turnos"]

    def create(self, turno: Turno) -> Turno:
        result = self.collection.insert_one(turno.model_dump(by_alias=True, exclude={"id"}))
        turno.id = result.inserted_id
        return turno

    def get_by_user(self, user_id: str) -> List[Turno]:
        return [Turno(**doc) for doc in self.collection.find({"user_id": user_id, "activo": True})]

    def get_by_sala(self, sala_code: str) -> List[Turno]:
        return [Turno(**doc) for doc in self.collection.find({"sala_code": sala_code, "activo": True})]
    
    def get_active_shifts(self, date_val: datetime) -> List[Turno]:
        """Obtiene turnos activos para una fecha específica."""
        # Un turno está activo si la fecha cae entre fecha_desde y fecha_hasta
        query = {
            "activo": True,
            "fecha_desde": {"$lte": date_val},
            "fecha_hasta": {"$gte": date_val}
        }
        return [Turno(**doc) for doc in self.collection.find(query)]
    
    def get_user_shifts(self, user_id: str, date_val) -> List[Turno]:
        """
        Obtiene turnos de un usuario para una fecha específica.
        
        Args:
            user_id: ID del usuario
            date_val: Fecha (date o datetime)
        
        Returns:
            Lista de turnos del usuario para esa fecha
        """
        # Convertir a datetime si es date
        if hasattr(date_val, 'year') and not hasattr(date_val, 'hour'):
            # Es un date, convertir a datetime
            from datetime import datetime as dt
            date_val = dt.combine(date_val, dt.min.time())
        
        query = {
            "user_id": user_id,
            "activo": True,
            "fecha_desde": {"$lte": date_val},
            "fecha_hasta": {"$gte": date_val}
        }
        return [Turno(**doc) for doc in self.collection.find(query)]

_turnos_repo = TurnosRepository()

def get_turnos_repository() -> TurnosRepository:
    return _turnos_repo
