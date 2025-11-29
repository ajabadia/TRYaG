"""
Repositorio para opciones clínicas configurables.
"""
from typing import List, Optional
from src.db.repositories.base import BaseRepository
from src.db.models import ClinicalOption

class ClinicalOptionsRepository(BaseRepository):
    """
    Repositorio para gestionar opciones clínicas (alergias, patologías, etc.).
    """
    
    def __init__(self):
        super().__init__("clinical_options")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios."""
        self.create_index([("category", 1)])
        self.create_index([("value", 1)])
    
    def get_options(self, category: str) -> List[ClinicalOption]:
        """
        Obtiene todas las opciones activas de una categoría.
        
        Args:
            category: Categoría a buscar (ej: 'allergy_agent')
            
        Returns:
            List[ClinicalOption]: Lista de opciones encontradas
        """
        docs = self.find_all(
            filters={"category": category, "active": True},
            sort=[("label", 1)]
        )
        return [ClinicalOption(**doc) for doc in docs]
    
    def get_by_value(self, category: str, value: str) -> Optional[ClinicalOption]:
        """Obtiene una opción específica por su valor."""
        doc = self.find_one({"category": category, "value": value})
        return ClinicalOption(**doc) if doc else None

# Instancia singleton
_clinical_options_repo: Optional[ClinicalOptionsRepository] = None

def get_clinical_options_repository() -> ClinicalOptionsRepository:
    """Obtiene la instancia singleton del repositorio."""
    global _clinical_options_repo
    if _clinical_options_repo is None:
        _clinical_options_repo = ClinicalOptionsRepository()
    return _clinical_options_repo
