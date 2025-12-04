"""
Repositorio para gestionar centros médicos y sus salas.

Gestiona la información de los centros y las salas asociadas.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from db.repositories.base import BaseRepository


class CentrosRepository(BaseRepository):
    """
    Repositorio para centros médicos.
    
    Gestiona la información de los centros y sus salas asociadas.
    """
    
    def __init__(self):
        super().__init__("centros")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios para la colección."""
        # Índice único en 'codigo' para evitar duplicados
        self.collection.create_index([("codigo", 1)], unique=True, sparse=True)
    
    def get_by_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un centro por su código.
        
        Args:
            codigo: Código del centro
            
        Returns:
            Optional[Dict]: Centro o None
        """
        return self.find_one({"codigo": codigo})
    
    def get_centro_principal(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el centro principal (el primero o único centro).
        
        Returns:
            Optional[Dict]: Centro principal o None
        """
        # Por ahora asumimos un solo centro, devolvemos el primero
        return self.find_one({})
    
    def create_or_update_centro(
        self, 
        codigo: str,
        denominacion: str,
        cif: Optional[str] = None,
        direccion: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        logo_path: Optional[str] = None,
        mensaje: Optional[str] = None,
        salas: Optional[List[Dict[str, Any]]] = None,
        group_id: Optional[str] = None,
        updated_by: str = "admin"
    ) -> str:
        """
        Crea o actualiza un centro.
        
        Args:
            codigo: Código único del centro
            denominacion: Nombre del centro
            cif: CIF/NIF
            direccion: Dirección
            email: Email de contacto
            telefono: Teléfono
            logo_path: Ruta al logo
            mensaje: Mensaje informativo
            salas: Lista de salas del centro
            group_id: ID del grupo al que pertenece (Multi-tenant)
            updated_by: Usuario que realiza el cambio
            
        Returns:
            str: ID del documento
        """
        existing = self.get_by_codigo(codigo) if codigo else None
        
        centro_data = {
            "codigo": codigo,
            "denominacion": denominacion,
            "cif": cif,
            "direccion": direccion,
            "email": email,
            "telefono": telefono,
            "logo_path": logo_path,
            "mensaje": mensaje,
            "salas": salas or [],
            "group_id": group_id,
            "updated_at": datetime.now(),
            "updated_by": updated_by
        }
        
        if existing:
            # Actualizar existente
            self.collection.update_one(
                {"codigo": codigo},
                {"$set": centro_data}
            )
            return str(existing["_id"])
        else:
            # Crear nuevo
            centro_data["created_at"] = datetime.now()
            return self.create(centro_data)
    
    def add_sala(
        self,
        centro_codigo: str,
        sala: Dict[str, Any],
        updated_by: str = "admin"
    ) -> bool:
        """
        Añade una sala a un centro.
        
        Args:
            centro_codigo: Código del centro
            sala: Datos de la sala
            updated_by: Usuario que realiza el cambio
            
        Returns:
            bool: True si se añadió correctamente
        """
        result = self.collection.update_one(
            {"codigo": centro_codigo},
            {
                "$push": {"salas": sala},
                "$set": {
                    "updated_at": datetime.now(),
                    "updated_by": updated_by
                }
            }
        )
        return result.modified_count > 0
    
    def update_sala(
        self,
        centro_codigo: str,
        sala_codigo: str,
        sala_data: Dict[str, Any],
        updated_by: str = "admin"
    ) -> bool:
        """
        Actualiza una sala específica de un centro.
        
        Args:
            centro_codigo: Código del centro
            sala_codigo: Código de la sala a actualizar
            sala_data: Nuevos datos de la sala
            updated_by: Usuario que realiza el cambio
            
        Returns:
            bool: True si se actualizó correctamente
        """
        result = self.collection.update_one(
            {
                "codigo": centro_codigo,
                "salas.codigo": sala_codigo
            },
            {
                "$set": {
                    "salas.$": sala_data,
                    "updated_at": datetime.now(),
                    "updated_by": updated_by
                }
            }
        )
        return result.modified_count > 0
    
    def delete_sala(
        self,
        centro_codigo: str,
        sala_codigo: str,
        updated_by: str = "admin"
    ) -> bool:
        """
        Elimina una sala de un centro.
        
        Args:
            centro_codigo: Código del centro
            sala_codigo: Código de la sala a eliminar
            updated_by: Usuario que realiza el cambio
            
        Returns:
            bool: True si se eliminó correctamente
        """
        result = self.collection.update_one(
            {"codigo": centro_codigo},
            {
                "$pull": {"salas": {"codigo": sala_codigo}},
                "$set": {
                    "updated_at": datetime.now(),
                    "updated_by": updated_by
                }
            }
        )
        return result.modified_count > 0
    
    def get_salas_by_tipo(
        self,
        centro_codigo: str,
        tipo: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las salas de un centro filtradas por tipo.
        
        Args:
            centro_codigo: Código del centro
            tipo: Tipo de sala (admision, triaje, espera, box, consulta)
            
        Returns:
            List[Dict]: Lista de salas del tipo especificado
        """
        centro = self.get_by_codigo(centro_codigo)
        if not centro:
            return []
        
        salas = centro.get("salas", [])
        return [sala for sala in salas if sala.get("tipo") == tipo]
    
    def get_salas_activas(self, centro_codigo: str) -> List[Dict[str, Any]]:
        """
        Obtiene las salas activas de un centro.
        
        Args:
            centro_codigo: Código del centro
            
        Returns:
            List[Dict]: Lista de salas activas
        """
        centro = self.get_by_codigo(centro_codigo)
        if not centro:
            return []
        
        salas = centro.get("salas", [])
        return [sala for sala in salas if sala.get("activa", False)]

    def get_centers_by_group(self, group_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene los centros pertenecientes a un grupo.
        
        Args:
            group_id: ID del grupo
            
        Returns:
            List[Dict]: Lista de centros
        """
        cursor = self.collection.find({"group_id": group_id})
        return list(cursor)


# Instancia singleton del repositorio
_centros_repo: Optional[CentrosRepository] = None


def get_centros_repository() -> CentrosRepository:
    """
    Obtiene la instancia singleton del repositorio de centros.
    
    Returns:
        CentrosRepository: Instancia del repositorio
    """
    global _centros_repo
    if _centros_repo is None:
        _centros_repo = CentrosRepository()
    return _centros_repo
