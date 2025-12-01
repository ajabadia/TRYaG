# path: src/db/repositories/triage_config.py
"""
Repositorio para la configuración de rangos de triaje.
"""
from typing import Optional, List, Dict, Any
from db.repositories.base import BaseRepository
from db.models import TriageRangeConfig

class TriageConfigRepository(BaseRepository[TriageRangeConfig]):
    """
    Repositorio para gestionar la configuración de umbrales de triaje.
    """
    
    def __init__(self):
        super().__init__("triage_config")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios."""
        # Índice único por métrica
        self.create_index([("metric", 1)], unique=True)

    def get_by_metric(self, metric: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la configuración para una métrica específica.
        """
        return self.find_one({"metric": metric})
    
    def get_all_configs(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las configuraciones de rangos.
        """
        return self.find_all(sort=[("metric", 1)])
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Guarda o actualiza la configuración de una métrica.
        """
        metric = config.get("metric")
        if not metric:
            return False
            
        return self.collection.replace_one(
            {"metric": metric},
            config,
            upsert=True
        ).acknowledged

# Instancia singleton
_triage_config_repo: Optional[TriageConfigRepository] = None

def get_triage_config_repository() -> TriageConfigRepository:
    """Obtiene la instancia singleton del repositorio."""
    global _triage_config_repo
    if _triage_config_repo is None:
        _triage_config_repo = TriageConfigRepository()
    return _triage_config_repo
