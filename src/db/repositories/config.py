"""
Repositorio para gestionar items de configuración.

Este es el repositorio más simple y sirve como prueba de concepto
para el patrón Repository antes de migrar los módulos más complejos.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from db.repositories.base import BaseRepository
from db.models import ConfigItem


class ConfigRepository(BaseRepository[ConfigItem]):
    """
    Repositorio para items de configuración.
    
    Gestiona la configuración general de la aplicación (modelos, etc.)
    """
    
    def __init__(self):
        super().__init__("config")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios para la colección."""
        # Índice único en 'key' para evitar duplicados
        self.create_index([("key", 1)], unique=True)
    
    def get_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un item de configuración por su clave.
        
        Args:
            key: Clave de configuración (ej: "triage_model")
            
        Returns:
            Optional[Dict]: Item de configuración o None
        """
        return self.find_one({"key": key})
    
    def set_config(
        self, 
        key: str, 
        value: Any, 
        description: Optional[str] = None,
        updated_by: str = "admin"
    ) -> str:
        """
        Establece o actualiza un valor de configuración.
        
        Args:
            key: Clave de configuración
            value: Valor a guardar
            description: Descripción opcional
            updated_by: Usuario que realiza el cambio
            
        Returns:
            str: ID del documento (nuevo o existente)
        """
        existing = self.get_by_key(key)
        
        if existing:
            # Actualizar existente
            self.collection.update_one(
                {"key": key},
                {
                    "$set": {
                        "value": value,
                        "description": description or existing.get("description"),
                        "updated_at": datetime.now(),
                        "updated_by": updated_by
                    }
                }
            )
            return str(existing["_id"])
        else:
            # Crear nuevo
            doc = {
                "key": key,
                "value": value,
                "description": description,
                "updated_at": datetime.now(),
                "updated_by": updated_by
            }
            return self.create(doc)
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración como un diccionario.
        
        Returns:
            Dict: Diccionario con key -> value de toda la configuración
        """
        all_items = self.find_all()
        return {item["key"]: item["value"] for item in all_items}
    
    def delete_by_key(self, key: str) -> bool:
        """
        Elimina un item de configuración por su clave.
        
        Args:
            key: Clave de configuración
            
        Returns:
            bool: True si se eliminó, False si no
        """
        result = self.collection.delete_one({"key": key})
        return result.deleted_count > 0
    
    def bulk_set(self, config_dict: Dict[str, Any], updated_by: str = "admin") -> int:
        """
        Establece múltiples valores de configuración de una vez.
        
        Args:
            config_dict: Diccionario con key -> value
            updated_by: Usuario que realiza los cambios
            
        Returns:
            int: Número de items actualizados/creados
        """
        count = 0
        for key, value in config_dict.items():
            self.set_config(key, value, updated_by=updated_by)
            count += 1
        return count


# Instancia singleton del repositorio
_config_repo: Optional[ConfigRepository] = None


def get_config_repository() -> ConfigRepository:
    """
    Obtiene la instancia singleton del repositorio de configuración.
    
    Returns:
        ConfigRepository: Instancia del repositorio
    """
    global _config_repo
    if _config_repo is None:
        _config_repo = ConfigRepository()
    return _config_repo
