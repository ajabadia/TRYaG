"""
Clase base para todos los repositorios.

Implementa operaciones CRUD comunes que heredarán todos los repositorios específicos.
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any
from datetime import datetime
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from bson import ObjectId

from src.db.connection import get_database

# Tipo genérico para los modelos
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Repositorio base con operaciones CRUD genéricas.
    
    Attributes:
        collection_name: Nombre de la colección en MongoDB
        collection: Instancia de la colección MongoDB
    """
    
    def __init__(self, collection_name: str):
        """
        Inicializa el repositorio.
        
        Args:
            collection_name: Nombre de la colección en MongoDB
        """
        self.collection_name = collection_name
        self.collection: Collection = get_database()[collection_name]
    
    def create(self, document: Dict[str, Any]) -> str:
        """
        Crea un nuevo documento en la colección.
        
        Args:
            document: Documento a insertar
            
        Returns:
            str: ID del documento insertado
        """
        # Añadir timestamp de creación si no existe
        if 'created_at' not in document:
            document['created_at'] = datetime.now()
        
        result: InsertOneResult = self.collection.insert_one(document)
        return str(result.inserted_id)
    
    def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca un documento por su ID.
        
        Args:
            doc_id: ID del documento (puede ser ObjectId o string)
            
        Returns:
            Optional[Dict]: Documento encontrado o None
        """
        try:
            # Intentar convertir a ObjectId si es posible
            if ObjectId.is_valid(doc_id):
                query = {"_id": ObjectId(doc_id)}
            else:
                query = {"_id": doc_id}
            
            return self.collection.find_one(query)
        except Exception:
            return None
    
    def find_one(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Busca un documento que coincida con los filtros.
        
        Args:
            filters: Filtros de búsqueda
            
        Returns:
            Optional[Dict]: Primer documento encontrado o None
        """
        return self.collection.find_one(filters)
    
    def find_all(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca todos los documentos que coincidan con los filtros.
        
        Args:
            filters: Filtros de búsqueda (opcional)
            sort: Lista de tuplas (campo, dirección) para ordenar
            limit: Número máximo de resultados
            skip: Número de resultados a saltar
            
        Returns:
            List[Dict]: Lista de documentos encontrados
        """
        filters = filters or {}
        cursor = self.collection.find(filters)
        
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    def update(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Actualiza un documento por su ID.
        
        Args:
            doc_id: ID del documento
            update_data: Datos a actualizar
            
        Returns:
            bool: True si se actualizó, False si no
        """
        # Añadir timestamp de actualización
        update_data['updated_at'] = datetime.now()
        
        try:
            if ObjectId.is_valid(doc_id):
                query = {"_id": ObjectId(doc_id)}
            else:
                query = {"_id": doc_id}
            
            result: UpdateResult = self.collection.update_one(
                query,
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def delete(self, doc_id: str) -> bool:
        """
        Elimina un documento por su ID.
        
        Args:
            doc_id: ID del documento
            
        Returns:
            bool: True si se eliminó, False si no
        """
        try:
            if ObjectId.is_valid(doc_id):
                query = {"_id": ObjectId(doc_id)}
            else:
                query = {"_id": doc_id}
            
            result: DeleteResult = self.collection.delete_one(query)
            return result.deleted_count > 0
        except Exception:
            return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta documentos que coincidan con los filtros.
        
        Args:
            filters: Filtros de búsqueda (opcional)
            
        Returns:
            int: Número de documentos
        """
        filters = filters or {}
        return self.collection.count_documents(filters)
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        Verifica si existe al menos un documento con los filtros dados.
        
        Args:
            filters: Filtros de búsqueda
            
        Returns:
            bool: True si existe, False si no
        """
        return self.collection.count_documents(filters, limit=1) > 0
    
    def create_index(self, keys: List[tuple], unique: bool = False):
        """
        Crea un índice en la colección.
        
        Args:
            keys: Lista de tuplas (campo, dirección) para el índice
            unique: Si el índice debe ser único
        """
        self.collection.create_index(keys, unique=unique)
