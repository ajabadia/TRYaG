"""
Repositorio para registros de pruebas de prompts.

Gestiona los logs de pruebas realizadas en el editor de prompts.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import pymongo

from src.db.repositories.base import BaseRepository
from src.db.models import PromptTest


class PromptTestsRepository(BaseRepository[PromptTest]):
    """
    Repositorio para registros de pruebas de prompts.
    
    Gestiona los logs de pruebas del editor de prompts.
    """
    
    def __init__(self):
        super().__init__("prompt_tests")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios para la colección."""
        # Índice único en test_id
        self.create_index([("test_id", 1)], unique=True)
        # Índice en timestamp
        self.create_index([("timestamp", pymongo.DESCENDING)])
        # Índice compuesto para filtrar por prompt_type y version
        self.create_index([("prompt_type", 1), ("version_id", 1)])
        # Índice en rating para analytics
        self.create_index([("rating", 1)])
    
    def get_by_test_id(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una prueba por su ID.
        
        Args:
            test_id: ID único de la prueba
            
        Returns:
            Optional[Dict]: Registro encontrado o None
        """
        return self.find_one({"test_id": test_id})
    
    def get_by_prompt_version(
        self,
        prompt_type: str,
        version_id: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene pruebas de una versión específica de prompt.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión
            
        Returns:
            List[Dict]: Lista de pruebas
        """
        return self.find_all(
            filters={
                "prompt_type": prompt_type,
                "version_id": version_id
            },
            sort=[("timestamp", pymongo.DESCENDING)]
        )
    
    def get_by_rating(self, rating: int) -> List[Dict[str, Any]]:
        """
        Obtiene pruebas por calificación.
        
        Args:
            rating: Calificación (0=dislike, 1=like)
            
        Returns:
            List[Dict]: Lista de pruebas
        """
        return self.find_all(
            filters={"rating": rating},
            sort=[("timestamp", pymongo.DESCENDING)]
        )
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene las pruebas más recientes.
        
        Args:
            limit: Número máximo de pruebas
            
        Returns:
            List[Dict]: Lista de pruebas ordenadas por fecha descendente
        """
        return self.find_all(
            sort=[("timestamp", pymongo.DESCENDING)],
            limit=limit
        )
    
    def get_stats_by_version(self, prompt_type: str, version_id: str) -> Dict[str, Any]:
        """
        Obtiene estadísticas de una versión de prompt.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión
            
        Returns:
            Dict: Estadísticas (total, likes, dislikes, ratio)
        """
        tests = self.get_by_prompt_version(prompt_type, version_id)
        
        total = len(tests)
        likes = sum(1 for t in tests if t.get("rating") == 1)
        dislikes = sum(1 for t in tests if t.get("rating") == 0)
        
        return {
            "total": total,
            "likes": likes,
            "dislikes": dislikes,
            "like_ratio": likes / total if total > 0 else 0
        }


# Instancia singleton
_tests_repo: Optional[PromptTestsRepository] = None


def get_prompt_tests_repository() -> PromptTestsRepository:
    """Obtiene la instancia singleton del repositorio."""
    global _tests_repo
    if _tests_repo is None:
        _tests_repo = PromptTestsRepository()
    return _tests_repo
