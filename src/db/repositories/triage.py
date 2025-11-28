"""
Repositorio para registros de triaje (antes audit_records).

Gestiona los registros de triaje realizados con la IA.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import pymongo

from src.db.repositories.base import BaseRepository
from src.db.models import TriageRecord


class TriageRepository(BaseRepository[TriageRecord]):
    """
    Repositorio para registros de triaje.
    
    Gestiona los registros de auditoría de triajes realizados.
    """
    
    def __init__(self):
        super().__init__("triage_records")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios para la colección."""
        # Índice único en audit_id
        self.create_index([("audit_id", 1)], unique=True)
        # Índice en timestamp (descendente para queries recientes)
        self.create_index([("timestamp", pymongo.DESCENDING)])
        # Índice en prompt_type
        self.create_index([("prompt_type", 1)])
        # Índice compuesto para filtros comunes
        self.create_index([("timestamp", pymongo.DESCENDING), ("prompt_type", 1)])
    
    def get_by_audit_id(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un registro por su audit_id.
        
        Args:
            audit_id: ID único del registro
            
        Returns:
            Optional[Dict]: Registro encontrado o None
        """
        return self.find_one({"audit_id": audit_id})
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene los registros más recientes.
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            List[Dict]: Lista de registros ordenados por fecha descendente
        """
        return self.find_all(
            sort=[("timestamp", pymongo.DESCENDING)],
            limit=limit
        )
    
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Obtiene registros en un rango de fechas.
        
        Args:
            start_date: Fecha inicial
            end_date: Fecha final
            
        Returns:
            List[Dict]: Lista de registros en el rango
        """
        return self.find_all(
            filters={
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            },
            sort=[("timestamp", pymongo.DESCENDING)]
        )
    
    def get_by_prompt_type(self, prompt_type: str) -> List[Dict[str, Any]]:
        """
        Obtiene registros por tipo de prompt.
        
        Args:
            prompt_type: Tipo de prompt usado
            
        Returns:
            List[Dict]: Lista de registros
        """
        return self.find_all(
            filters={"prompt_type": prompt_type},
            sort=[("timestamp", pymongo.DESCENDING)]
        )


# Instancia singleton
_triage_repo: Optional[TriageRepository] = None


def get_triage_repository() -> TriageRepository:
    """Obtiene la instancia singleton del repositorio."""
    global _triage_repo
    if _triage_repo is None:
        _triage_repo = TriageRepository()
    return _triage_repo
