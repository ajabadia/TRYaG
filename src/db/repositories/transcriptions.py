"""
Repositorio para registros de transcripciones.

Gestiona las transcripciones de audio realizadas.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import pymongo

from db.repositories.base import BaseRepository
from db.models import TranscriptionRecord


class TranscriptionsRepository(BaseRepository[TranscriptionRecord]):
    """
    Repositorio para registros de transcripciones.
    
    Gestiona las transcripciones de audio.
    """
    
    def __init__(self):
        super().__init__("transcriptions_records")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios para la colección."""
        # Índice único en transcription_id
        self.create_index([("transcription_id", 1)], unique=True)
        # Índice en timestamp
        self.create_index([("timestamp", pymongo.DESCENDING)])
        # Índice en language_code para filtrar por idioma
        self.create_index([("language_code", 1)])
    
    def get_by_transcription_id(self, transcription_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una transcripción por su ID.
        
        Args:
            transcription_id: ID único de la transcripción
            
        Returns:
            Optional[Dict]: Registro encontrado o None
        """
        return self.find_one({"transcription_id": transcription_id})
    
    def get_by_language(self, language_code: str) -> List[Dict[str, Any]]:
        """
        Obtiene transcripciones por idioma.
        
        Args:
            language_code: Código ISO del idioma
            
        Returns:
            List[Dict]: Lista de transcripciones
        """
        return self.find_all(
            filters={"language_code": language_code},
            sort=[("timestamp", pymongo.DESCENDING)]
        )
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene las transcripciones más recientes.
        
        Args:
            limit: Número máximo de transcripciones
            
        Returns:
            List[Dict]: Lista de transcripciones ordenadas por fecha descendente
        """
        return self.find_all(
            sort=[("timestamp", pymongo.DESCENDING)],
            limit=limit
        )


# Instancia singleton
_transcriptions_repo: Optional[TranscriptionsRepository] = None


def get_transcriptions_repository() -> TranscriptionsRepository:
    """Obtiene la instancia singleton del repositorio."""
    global _transcriptions_repo
    if _transcriptions_repo is None:
        _transcriptions_repo = TranscriptionsRepository()
    return _transcriptions_repo
