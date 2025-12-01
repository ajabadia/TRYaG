# path: src/db/repositories/vital_signs_repo.py
from typing import List, Optional, Any
from db.repositories.base import BaseRepository
from db.models import VitalSignReference

class VitalSignsRepository(BaseRepository[VitalSignReference]):
    """Repositorio para gestionar referencias de signos vitales."""
    
    def __init__(self):
        super().__init__(collection_name="vital_sign_references")
    
    def get_by_key(self, key: str) -> Optional[VitalSignReference]:
        """Obtiene la configuración de un signo vital por su clave interna."""
        data = self.find_one({"key": key})
        return VitalSignReference(**data) if data else None
    
    def get_all_references(self) -> List[VitalSignReference]:
        """Obtiene todas las referencias de signos vitales."""
        docs = self.find_all(sort=[("name", 1)])
        return [VitalSignReference(**d) for d in docs]

    def get_config(self, metric: str, age: int) -> Optional[Any]:
        """
        Obtiene la configuración específica para un signo vital y edad.
        
        Args:
            metric: Clave del signo vital (ej: 'fc', 'spo2')
            age: Edad del paciente
            
        Returns:
            VitalSignAgeConfig o None si no se encuentra
        """
        ref = self.get_by_key(metric)
        if not ref:
            return None
            
        # Buscar configuración por rango de edad
        for config in ref.configs:
            if config.min_age <= age <= config.max_age:
                return config
                
        return None
