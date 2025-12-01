"""
Paquete de acceso a datos para MongoDB.

Este paquete contiene:
- connection.py: Gestión de conexiones
- models.py: Modelos Pydantic para validación
- repositories/: Implementaciones del patrón Repository
"""

from .connection import (
    get_client,
    get_database,
    health_check,
    close_connection,
    MongoDBSession,
    retry_on_connection_error
)

__all__ = [
    "get_client",
    "get_database",
    "health_check",
    "close_connection",
    "MongoDBSession",
    "retry_on_connection_error"
]
