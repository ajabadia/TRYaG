"""
Repositorio para gestionar prompts versionados.

Este repositorio maneja la complejidad del versionado de prompts,
permitiendo múltiples versiones (draft, active, deprecated) por tipo.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.db.repositories.base import BaseRepository
from src.db.models import Prompt, PromptVersion


class PromptsRepository(BaseRepository[Prompt]):
    """
    Repositorio para prompts versionados.
    
    Gestiona prompts con múltiples versiones y estados (draft, active, deprecated).
    """
    
    def __init__(self):
        super().__init__("prompts")
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Crea índices necesarios para la colección."""
        # Índice único en prompt_type
        self.create_index([("prompt_type", 1)], unique=True)
        # Índice en versions.version_id para búsquedas rápidas
        self.create_index([("versions.version_id", 1)])
        # Índice en versions.status
        self.create_index([("versions.status", 1)])
    
    def get_by_type(self, prompt_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un prompt por su tipo.
        
        Args:
            prompt_type: Tipo de prompt (triage_gemini, triage_sim, transcription)
            
        Returns:
            Optional[Dict]: Documento del prompt o None
        """
        return self.find_one({"prompt_type": prompt_type})
    
    def get_active_version(self, prompt_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la versión activa de un prompt.
        
        Args:
            prompt_type: Tipo de prompt
            
        Returns:
            Optional[Dict]: Versión activa o None
        """
        prompt = self.get_by_type(prompt_type)
        if not prompt or not prompt.get("active_version"):
            return None
        
        # Buscar la versión activa en el array
        active_id = prompt["active_version"]
        for version in prompt.get("versions", []):
            if version["version_id"] == active_id:
                return version
        
        return None
    
    def get_version(self, prompt_type: str, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una versión específica de un prompt.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión (ej: v1, v2)
            
        Returns:
            Optional[Dict]: Versión encontrada o None
        """
        prompt = self.get_by_type(prompt_type)
        if not prompt:
            return None
        
        for version in prompt.get("versions", []):
            if version["version_id"] == version_id:
                return version
        
        return None
    
    def list_versions(self, prompt_type: str) -> List[Dict[str, Any]]:
        """
        Lista todas las versiones de un prompt.
        
        Args:
            prompt_type: Tipo de prompt
            
        Returns:
            List[Dict]: Lista de versiones
        """
        prompt = self.get_by_type(prompt_type)
        if not prompt:
            return []
        
        return prompt.get("versions", [])
    
    def create_prompt_type(self, prompt_type: str) -> str:
        """
        Crea un nuevo tipo de prompt (sin versiones inicialmente).
        
        Args:
            prompt_type: Tipo de prompt
            
        Returns:
            str: ID del documento creado
        """
        doc = {
            "prompt_type": prompt_type,
            "active_version": None,
            "versions": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        return self.create(doc)
    
    def add_version(
        self,
        prompt_type: str,
        version_id: str,
        content: str,
        author: str = "admin",
        notes: str = "",
        status: str = "draft"
    ) -> bool:
        """
        Añade una nueva versión a un prompt.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión
            content: Contenido del prompt
            author: Autor de la versión
            notes: Notas sobre la versión
            status: Estado (draft, active, deprecated)
            
        Returns:
            bool: True si se añadió, False si no
        """
        # Verificar que el prompt existe
        prompt = self.get_by_type(prompt_type)
        if not prompt:
            # Crear el tipo de prompt si no existe
            self.create_prompt_type(prompt_type)
        
        # Crear nueva versión
        new_version = {
            "version_id": version_id,
            "content": content,
            "author": author,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "updated_by": author,
            "notes": notes,
            "status": status
        }
        
        # Añadir al array de versiones
        result = self.collection.update_one(
            {"prompt_type": prompt_type},
            {
                "$push": {"versions": new_version},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        return result.modified_count > 0
    
    def update_version(
        self,
        prompt_type: str,
        version_id: str,
        content: Optional[str] = None,
        notes: Optional[str] = None,
        status: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> bool:
        """
        Actualiza una versión existente.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión
            content: Nuevo contenido (opcional)
            notes: Nuevas notas (opcional)
            status: Nuevo estado (opcional)
            updated_by: Usuario que actualiza (opcional)
            
        Returns:
            bool: True si se actualizó, False si no
        """
        update_fields = {"versions.$.updated_at": datetime.now()}
        
        if content is not None:
            update_fields["versions.$.content"] = content
        if notes is not None:
            update_fields["versions.$.notes"] = notes
        if status is not None:
            update_fields["versions.$.status"] = status
        if updated_by is not None:
            update_fields["versions.$.updated_by"] = updated_by
        
        result = self.collection.update_one(
            {
                "prompt_type": prompt_type,
                "versions.version_id": version_id
            },
            {
                "$set": update_fields
            }
        )
        
        return result.modified_count > 0
    
    def set_active_version(self, prompt_type: str, version_id: str) -> bool:
        """
        Establece una versión como activa.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión a activar
            
        Returns:
            bool: True si se activó, False si no
        """
        # Verificar que la versión existe
        version = self.get_version(prompt_type, version_id)
        if not version:
            return False
        
        # Actualizar estado de la versión a 'active'
        self.update_version(prompt_type, version_id, status="active")
        
        # Establecer como active_version
        result = self.collection.update_one(
            {"prompt_type": prompt_type},
            {
                "$set": {
                    "active_version": version_id,
                    "updated_at": datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    
    def deprecate_version(self, prompt_type: str, version_id: str) -> bool:
        """
        Marca una versión como deprecated.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión
            
        Returns:
            bool: True si se depreció, False si no
        """
        return self.update_version(prompt_type, version_id, status="deprecated")
    
    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los prompts con sus versiones.
        
        Returns:
            List[Dict]: Lista de todos los prompts
        """
        return self.find_all()


# Instancia singleton del repositorio
_prompts_repo: Optional[PromptsRepository] = None


def get_prompts_repository() -> PromptsRepository:
    """
    Obtiene la instancia singleton del repositorio de prompts.
    
    Returns:
        PromptsRepository: Instancia del repositorio
    """
    global _prompts_repo
    if _prompts_repo is None:
        _prompts_repo = PromptsRepository()
    return _prompts_repo
