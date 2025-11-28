"""
Repositorio para registros de archivos importados.

Gestiona los archivos (imágenes, PDFs) importados en el sistema.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import pymongo

from src.db.repositories.base import BaseRepository
from src.db.models import FileImportRecord


class FileImportsRepository(BaseRepository[FileImportRecord]):
    """
    Repositorio para registros de archivos importados.
    
    Gestiona los archivos subidos al sistema.
    """
    
    def __init__(self):
        super().__init__("file_imports_records")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios para la colección."""
        # Índice único en file_id
        self.create_index([("file_id", 1)], unique=True)
        # Índice en timestamp
        self.create_index([("timestamp", pymongo.DESCENDING)])
        # Índice en audit_id para relación con triajes
        self.create_index([("audit_id", 1)])
    
    def get_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un archivo por su file_id.
        
        Args:
            file_id: ID único del archivo
            
        Returns:
            Optional[Dict]: Registro encontrado o None
        """
        return self.find_one({"file_id": file_id})
    
    def get_by_audit_id(self, audit_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene archivos asociados a un registro de auditoría.
        
        Args:
            audit_id: ID del registro de auditoría
            
        Returns:
            List[Dict]: Lista de archivos
        """
        return self.find_all(
            filters={"audit_id": audit_id},
            sort=[("timestamp", pymongo.DESCENDING)]
        )
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene los archivos más recientes.
        
        Args:
            limit: Número máximo de archivos
            
        Returns:
            List[Dict]: Lista de archivos ordenados por fecha descendente
        """
        return self.find_all(
            sort=[("timestamp", pymongo.DESCENDING)],
            limit=limit
        )


# Instancia singleton
_files_repo: Optional[FileImportsRepository] = None


def get_file_imports_repository() -> FileImportsRepository:
    """Obtiene la instancia singleton del repositorio."""
    global _files_repo
    if _files_repo is None:
        _files_repo = FileImportsRepository()
    return _files_repo
