"""
Módulo de gestión de conexión a MongoDB Atlas.

Este módulo proporciona una interfaz centralizada para conectarse a MongoDB,
con manejo de errores, retry logic y connection pooling.
"""
import os
from typing import Optional
from functools import wraps
import time
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

import certifi

# Cargar variables de entorno
load_dotenv()

# Variables globales para connection pooling
_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def retry_on_connection_error(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator para reintentar operaciones en caso de error de conexión.
    
    Args:
        max_retries: Número máximo de reintentos
        delay: Tiempo de espera entre reintentos (en segundos)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (attempt + 1)
                        print(f"⚠️ Error de conexión (intento {attempt + 1}/{max_retries}). Reintentando en {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Error de conexión después de {max_retries} intentos.")
            
            raise last_exception
        return wrapper
    return decorator


@retry_on_connection_error(max_retries=3, delay=1.0)
def get_client() -> MongoClient:
    """
    Obtiene el cliente de MongoDB (singleton pattern).
    
    Returns:
        MongoClient: Cliente de MongoDB configurado
        
    Raises:
        ValueError: Si no se encuentra MONGODB_URI en las variables de entorno
        ConnectionFailure: Si no se puede conectar a MongoDB
    """
    global _client
    
    if _client is not None:
        return _client
    
    # Obtener URI desde variables de entorno
    mongodb_uri = os.getenv("MONGODB_URI")
    
    if not mongodb_uri:
        raise ValueError(
            "MONGODB_URI no encontrado en variables de entorno. "
            "Asegúrate de tener un archivo .env con la configuración correcta."
        )
    
    # Debug: Mostrar URI enmascarada para verificar que se carga correctamente
    masked_uri = mongodb_uri.replace(mongodb_uri.split("@")[0].split("//")[1].split(":")[1], "****") if "@" in mongodb_uri else "URI_SIN_CREDENCIALES"
    print(f"🔌 Intentando conectar a MongoDB con URI: {masked_uri}")
    
    # Crear cliente con configuración optimizada
    _client = MongoClient(
        mongodb_uri,
        server_api=ServerApi('1'),
        maxPoolSize=50,  # Máximo de conexiones en el pool
        minPoolSize=10,  # Mínimo de conexiones mantenidas
        maxIdleTimeMS=45000,  # Tiempo máximo de inactividad
        serverSelectionTimeoutMS=30000,  # Timeout para selección de servidor (30s)
        connectTimeoutMS=30000,  # Timeout para conexión inicial (30s)
        socketTimeoutMS=30000,  # Timeout para operaciones de socket (30s)
        tlsCAFile=certifi.where(), # Explicitly use certifi CA bundle
        tlsDisableOCSPEndpointCheck=True, # Disable OCSP check which might fail on mobile networks
    )
    
    # Verificar conexión
    _client.admin.command('ping')
    
    return _client


def get_database() -> Database:
    """
    Obtiene la base de datos configurada (singleton pattern).
    
    Returns:
        Database: Instancia de la base de datos MongoDB
    """
    global _database
    
    if _database is not None:
        return _database
    
    client = get_client()
    db_name = os.getenv("MONGODB_DATABASE", "triaje_db")
    _database = client[db_name]
    
    return _database


def health_check() -> dict:
    """
    Verifica el estado de la conexión a MongoDB.
    
    Returns:
        dict: Información sobre el estado de la conexión
    """
    try:
        client = get_client()
        
        # Ping al servidor
        client.admin.command('ping')
        
        # Obtener información del servidor
        server_info = client.server_info()
        
        # Obtener base de datos
        db = get_database()
        
        return {
            "status": "healthy",
            "mongodb_version": server_info.get("version"),
            "database": db.name,
            "collections": db.list_collection_names(),
            "connection_pool_size": client.options.pool_options.max_pool_size,
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def close_connection():
    """
    Cierra la conexión a MongoDB.
    
    Útil para cleanup al finalizar la aplicación.
    """
    global _client, _database
    
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        print("🔒 Conexión a MongoDB cerrada correctamente")


# Context manager para operaciones transaccionales
class MongoDBSession:
    """
    Context manager para manejar sesiones de MongoDB.
    
    Ejemplo:
        with MongoDBSession() as session:
            # Realizar operaciones con la sesión
            pass
    """
    
    def __init__(self):
        self.client = None
        self.session = None
    
    def __enter__(self):
        self.client = get_client()
        self.session = self.client.start_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.end_session()
        
        # Retornar False para propagar excepciones
        return False


if __name__ == "__main__":
    # Prueba de conexión
    print("🔄 Probando conexión a MongoDB...")
    
    try:
        db = get_database()
        print(f"✅ Conectado a la base de datos: {db.name}")
        
        health = health_check()
        print(f"📊 Estado: {health}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        close_connection()
