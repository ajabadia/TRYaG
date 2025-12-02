"""
Repositorio para gestionar los modelos de IA disponibles en MongoDB.
"""
from typing import List, Dict, Any
from datetime import datetime
from db import get_database

COLLECTION_NAME = "ai_models"

class AIModelsRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db[COLLECTION_NAME]

    def update_models(self, models_list: List[str]) -> int:
        """
        Actualiza la lista de modelos disponibles.
        - Marca como activos los que están en la lista.
        - Marca como inactivos los que ya no están.
        - Inserta los nuevos.
        """
        if not models_list:
            return 0

        # 1. Marcar todos como inactivos temporalmente (o podríamos hacerlo selectivamente)
        # Estrategia: Upsert para cada modelo encontrado
        
        current_time = datetime.now()
        count = 0
        
        # Obtener modelos actuales para comparar
        existing_models = {m["name"] for m in self.collection.find({}, {"name": 1})}
        
        # Procesar lista nueva
        for model_name in models_list:
            self.collection.update_one(
                {"name": model_name},
                {
                    "$set": {
                        "name": model_name,
                        "is_active": True,
                        "last_seen": current_time,
                        "provider": "google" # Por ahora solo Google
                    },
                    "$setOnInsert": {
                        "created_at": current_time
                    }
                },
                upsert=True
            )
            count += 1
            
        # Marcar como inactivos los que no vinieron en la lista
        self.collection.update_many(
            {"name": {"$nin": models_list}},
            {"$set": {"is_active": False}}
        )
        
        return count

    def get_available_models(self) -> List[str]:
        """
        Retorna lista de nombres de modelos activos.
        """
        cursor = self.collection.find({"is_active": True}, {"name": 1}).sort("name", 1)
        return [doc["name"] for doc in cursor]

    def get_all_models(self) -> List[Dict[str, Any]]:
        """
        Retorna todos los modelos con sus detalles.
        """
        cursor = self.collection.find({}).sort("name", 1)
        return list(cursor)

_repository = None

def get_ai_models_repository() -> AIModelsRepository:
    global _repository
    if _repository is None:
        _repository = AIModelsRepository()
    return _repository
