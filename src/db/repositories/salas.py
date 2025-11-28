# path: src/db/repositories/salas.py
# Creado: 2025-11-25
"""
Repositorio para gestión de salas (CRUD) y consultas auxiliares.
Mantiene la filosofía DRY y archivos pequeños.
"""
from typing import List, Dict, Any, Optional
from db.connection import get_database
from datetime import datetime


def get_collection():
    """Obtiene la colección MongoDB de salas."""
    db = get_database()
    return db["salas"]


def get_all_salas() -> List[Dict[str, Any]]:
    """Devuelve la lista completa de salas."""
    collection = get_collection()
    return list(collection.find())


def get_salas_by_tipo(tipo: str) -> List[Dict[str, Any]]:
    """Filtra salas por su tipo (admision, triaje, box, etc.)."""
    collection = get_collection()
    return list(collection.find({"tipo": tipo}))


def get_sala(codigo: str) -> Optional[Dict[str, Any]]:
    """Obtiene una sala por su código único."""
    collection = get_collection()
    return collection.find_one({"codigo": codigo})


def save_sala(sala_data: Dict[str, Any]) -> bool:
    """Crea o actualiza una sala.
    Si la sala ya existe se actualiza, si no se inserta.
    """
    collection = get_collection()
    sala_data["updated_at"] = datetime.now()
    try:
        result = collection.update_one(
            {"codigo": sala_data["codigo"]},
            {"$set": sala_data},
            upsert=True,
        )
        return result.acknowledged
    except Exception as e:
        print(f"Error guardando sala {sala_data.get('codigo')}: {e}")
        return False


def delete_sala(codigo: str) -> bool:
    """Elimina una sala siempre que no tenga pacientes asignados.
    En esta versión solo verifica existencia; la lógica de pacientes
    se implementará más adelante.
    """
    collection = get_collection()
    try:
        result = collection.delete_one({"codigo": codigo})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error eliminando sala {codigo}: {e}")
        return False


def get_usuarios_asignados_sala(codigo: str) -> List[Dict[str, Any]]:
    """Obtiene usuarios asignados a una sala."""
    from db.repositories.users import get_users_repository
    repo = get_users_repository()
    all_users = repo.get_all_users(active_only=True)
    return [u for u in all_users if u.get("sala_asignada") == codigo]
