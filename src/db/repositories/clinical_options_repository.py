
from typing import List, Dict, Optional
from db import get_database
from db.models import ClinicalOption

class ClinicalOptionsRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db['clinical_options']

    def get_options_by_category(self, category: str) -> List[Dict]:
        """
        Obtiene las opciones activas para una categoría específica, ordenadas por 'meta.order'.
        """
        cursor = self.collection.find(
            {"category": category, "active": True}
        ).sort("meta.order", 1)
        
        return [
            {
                "value": doc["value"],
                "label": doc["label"],
                "meta": doc.get("meta", {})
            }
            for doc in cursor
        ]

    def get_options_map(self, category: str) -> Dict[str, str]:
        """
        Devuelve un diccionario {value: label} para una categoría.
        Útil para lookups rápidos.
        """
        options = self.get_options_by_category(category)
        return {opt["value"]: opt["label"] for opt in options}

_repo_instance = None

def get_clinical_options_repository() -> ClinicalOptionsRepository:
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = ClinicalOptionsRepository()
    return _repo_instance
