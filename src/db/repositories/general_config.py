"""
Repositorio para gestionar la configuración general de la aplicación en MongoDB.
"""
from typing import Dict, Any, Optional
from src.db.connection import get_database

COLLECTION_NAME = "general_config"
CONFIG_ID = "app_general_config"  # ID único para el documento de configuración

class GeneralConfigRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db[COLLECTION_NAME]

    def get_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración general.
        Si no existe, retorna una configuración por defecto.
        """
        try:
            config = self.collection.find_one({"_id": CONFIG_ID})
            if config:
                return config
            
            # Configuración por defecto si no existe
            default_config = {
                "_id": CONFIG_ID,
                "min_chars_motivo": 3,
                "model_triage": "gemini-2.5-flash",
                "model_transcription": "gemini-2.5-flash"
            }
            # Guardar por defecto para la próxima vez
            self.save_config(default_config)
            return default_config
            
        except Exception as e:
            print(f"Error al obtener configuración general: {e}")
            return {"min_chars_motivo": 3}

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Guarda o actualiza la configuración general.
        """
        try:
            # Asegurar que el ID es correcto
            config["_id"] = CONFIG_ID
            self.collection.replace_one(
                {"_id": CONFIG_ID},
                config,
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error al guardar configuración general: {e}")
            return False

_repository = None

def get_general_config_repository() -> GeneralConfigRepository:
    """Singleton provider for GeneralConfigRepository"""
    global _repository
    if _repository is None:
        _repository = GeneralConfigRepository()
    return _repository
