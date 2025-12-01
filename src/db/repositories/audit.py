"""
Repositorio para registros de auditoría.

Gestiona el registro de acciones y decisiones en el sistema.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import pymongo

from db.repositories.base import BaseRepository

class AuditRepository(BaseRepository):
    """
    Repositorio para registros de auditoría.
    
    Gestiona el log de acciones, validaciones y cambios en el sistema.
    """
    
    def __init__(self):
        super().__init__("audit_log")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios para la colección."""
        # Índice en timestamp
        self.create_index([("timestamp", pymongo.DESCENDING)])
        # Índice en patient_code (si aplica)
        self.create_index([("patient_code", 1)])
        # Índice en usuario
        self.create_index([("usuario", 1)])
        # Índice en tipo de acción
        self.create_index([("accion", 1)])
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene los registros de auditoría más recientes.
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            List[Dict]: Lista de registros ordenados por fecha descendente
        """
        return self.find_all(
            sort=[("timestamp", pymongo.DESCENDING)],
            limit=limit
        )
    
    def registrar_accion(self, accion: str, usuario: str, detalles: Dict[str, Any], patient_code: Optional[str] = None) -> str:
        """
        Registra una nueva acción en la auditoría.
        
        Args:
            accion: Tipo de acción realizada
            usuario: Usuario que realizó la acción
            detalles: Diccionario con detalles de la acción
            patient_code: Código del paciente relacionado (opcional)
            
        Returns:
            str: ID del nuevo registro
        """
        registro = {
            "timestamp": datetime.now(),
            "accion": accion,
            "usuario": usuario,
            "detalles": detalles,
            "patient_code": patient_code
        }
        return self.create(registro)

# Instancia singleton
_audit_repo: Optional[AuditRepository] = None

def get_audit_repository() -> AuditRepository:
    """Obtiene la instancia singleton del repositorio."""
    global _audit_repo
    if _audit_repo is None:
        _audit_repo = AuditRepository()
    return _audit_repo
