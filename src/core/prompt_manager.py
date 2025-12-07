# path: src/core/prompt_manager.py
# Creado: 2025-11-23
# Actualizado: 2025-11-23 - Migrado a MongoDB
"""
Gestor de Prompts para la aplicación.
Ahora usa MongoDB para almacenar y gestionar prompts versionados.
"""
import json
import os
import sys
from datetime import datetime

# Añadir directorio raíz al path para imports
if os.path.dirname(os.path.dirname(os.path.dirname(__file__))) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar repositorios de MongoDB
try:
    from db.repositories.prompts import get_prompts_repository
    from db.repositories.tests import get_prompt_tests_repository
except ImportError:
    # Fallback si no se puede importar
    get_prompts_repository = None
    get_prompt_tests_repository = None

# Mantener compatibilidad con archivos JSON como fallback
PROMPTS_FILE = os.path.join('data', 'prompts.json')


class PromptManager:
    """
    Gestor de prompts que usa MongoDB como almacenamiento principal.
    Mantiene compatibilidad con JSON como fallback.
    """
    
    def __init__(self):
        self.repo = get_prompts_repository()
        self.tests_repo = get_prompt_tests_repository()
    
    def get_prompt(self, prompt_type, version=None):
        """
        Obtiene el contenido de un prompt.
        Si version es None, devuelve la versión activa.
        
        Args:
            prompt_type: Tipo de prompt (triage_gemini, triage_sim, transcription)
            version: ID de versión específica (opcional)
            
        Returns:
            dict: Datos de la versión del prompt o None
        """
        try:
            if version is None:
                # Obtener versión activa
                version_data = self.repo.get_active_version(prompt_type)
            else:
                # Obtener versión específica
                version_data = self.repo.get_version(prompt_type, version)
            
            return version_data
            
        except Exception as e:
            print(f"Error obteniendo prompt desde MongoDB: {e}")
            # Fallback a JSON
            return self._get_prompt_from_json(prompt_type, version)
    
    def get_active_prompt(self, prompt_type):
        """
        Alias para obtener la versión activa de un prompt.
        """
        return self.get_prompt(prompt_type)
    
    def _get_prompt_from_json(self, prompt_type, version=None):
        """Fallback: obtiene prompt desde archivo JSON."""
        if not os.path.exists(PROMPTS_FILE):
            return None
        
        try:
            with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            
            if prompt_type not in prompts_data:
                return None
            
            p_data = prompts_data[prompt_type]
            
            if version is None:
                version = p_data.get("active_version")
            
            if not version or version not in p_data.get("versions", {}):
                return None
            
            return p_data["versions"][version]
        except Exception:
            return None
    
    def list_versions(self, prompt_type):
        """
        Devuelve una lista de versiones disponibles para un tipo de prompt.
        
        Args:
            prompt_type: Tipo de prompt
            
        Returns:
            dict: Diccionario con versiones {version_id: version_data}
        """
        try:
            versions_list = self.repo.list_versions(prompt_type)
            # Convertir lista a diccionario para compatibilidad
            return {v["version_id"]: v for v in versions_list}
        except Exception as e:
            print(f"Error listando versiones desde MongoDB: {e}")
            # Fallback a JSON
            return self._list_versions_from_json(prompt_type)
    
    def _list_versions_from_json(self, prompt_type):
        """Fallback: lista versiones desde JSON."""
        if not os.path.exists(PROMPTS_FILE):
            return {}
        
        try:
            with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
            
            if prompt_type not in prompts_data:
                return {}
            
            return prompts_data[prompt_type].get("versions", {})
        except Exception:
            return {}
    
    def get_active_version_id(self, prompt_type):
        """
        Devuelve el ID de la versión activa.
        
        Args:
            prompt_type: Tipo de prompt
            
        Returns:
            str: ID de la versión activa o None
        """
        try:
            prompt_doc = self.repo.get_by_type(prompt_type)
            if prompt_doc:
                return prompt_doc.get("active_version")
            return None
        except Exception:
            # Fallback a JSON
            if not os.path.exists(PROMPTS_FILE):
                return None
            
            try:
                with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
                    prompts_data = json.load(f)
                
                if prompt_type in prompts_data:
                    return prompts_data[prompt_type].get("active_version")
            except Exception:
                pass
            
            return None
    
    def create_version(self, prompt_type, content, model=None, author="admin", notes=""):
        """
        Crea una nueva versión (draft) de un prompt.
        
        Args:
            prompt_type: Tipo de prompt
            content: Contenido del prompt
            model: Modelo de IA asociado (opcional)
            author: Autor de la versión
            notes: Notas sobre la versión
            
        Returns:
            str: ID de la nueva versión
        """
        try:
            # Generar ID de versión (v1, v2, ...)
            versions = self.repo.list_versions(prompt_type)
            count = len(versions) + 1
            new_version_id = f"v{count}"
            
            # Verificar que no exista (evitar colisiones)
            while any(v["version_id"] == new_version_id for v in versions):
                count += 1
                new_version_id = f"v{count}"
            
            # Añadir versión
            self.repo.add_version(
                prompt_type=prompt_type,
                version_id=new_version_id,
                content=content,
                model=model,
                author=author,
                notes=notes,
                status="draft"
            )
            
            return new_version_id
            
        except Exception as e:
            print(f"Error creando versión en MongoDB: {e}")
            return None
    
    def update_version(self, prompt_type, version_id, content, model=None, author="admin", notes=""):
        """
        Actualiza una versión existente (solo si es draft).
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión
            content: Nuevo contenido
            model: Nuevo modelo (opcional)
            author: Autor de la actualización
            notes: Notas actualizadas
            
        Returns:
            bool: True si se actualizó, False si no
        """
        try:
            # Verificar que sea draft
            version = self.repo.get_version(prompt_type, version_id)
            if not version:
                return False
            
            current_status = version.get("status", "draft")
            if current_status != "draft":
                return False  # Solo editar drafts
            
            # Actualizar
            return self.repo.update_version(
                prompt_type=prompt_type,
                version_id=version_id,
                content=content,
                model=model,
                notes=notes,
                updated_by=author
            )
            
        except Exception as e:
            print(f"Error actualizando versión en MongoDB: {e}")
            return False
    
    def set_active_version(self, prompt_type, version_id):
        """
        Marca una versión como activa.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión a activar
            
        Returns:
            bool: True si se activó, False si no
        """
        try:
            # Obtener versión activa anterior
            old_active_id = self.get_active_version_id(prompt_type)
            
            # Deprecar la anterior si existe
            if old_active_id and old_active_id != version_id:
                self.repo.deprecate_version(prompt_type, old_active_id)
            
            # Activar nueva
            return self.repo.set_active_version(prompt_type, version_id)
            
        except Exception as e:
            print(f"Error activando versión en MongoDB: {e}")
            return False
    
    def deprecate_version(self, prompt_type, version_id):
        """
        Marca una versión como deprecada.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión
            
        Returns:
            bool: True si se depreció, False si no
        """
        try:
            # No deprecar la activa
            active_id = self.get_active_version_id(prompt_type)
            if active_id == version_id:
                return False
            
            return self.repo.deprecate_version(prompt_type, version_id)
            
        except Exception as e:
            print(f"Error deprecando versión en MongoDB: {e}")
            return False
    
    def log_test_result(self, prompt_type, version_id, prompt_content, response, model, rating, user="admin"):
        """
        Registra el resultado de una prueba de prompt en MongoDB.
        
        Args:
            prompt_type: Tipo de prompt
            version_id: ID de la versión
            prompt_content: Contenido del prompt probado
            response: Respuesta de la IA (string JSON)
            model: Modelo usado
            rating: Calificación (0=dislike, 1=like)
            user: Usuario que realizó la prueba
            
        Returns:
            bool: True si se guardó, False si no
        """
        try:
            # Generar test_id único
            import random
            test_id = f"TEST-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            # Parsear response si es string
            if isinstance(response, str):
                try:
                    response_dict = json.loads(response)
                except:
                    response_dict = {"raw": response}
            else:
                response_dict = response
            
            # Crear documento
            doc = {
                "test_id": test_id,
                "timestamp": datetime.now(),
                "user": user,
                "prompt_type": prompt_type,
                "version_id": version_id,
                "model": model,
                "rating": rating,
                "prompt_content": prompt_content,
                "test_input": "",  # No disponible en esta versión
                "response": response_dict,
                "created_at": datetime.now()
            }
            
            self.tests_repo.create(doc)
            return True
            
        except Exception as e:
            print(f"Error guardando log de prueba en MongoDB: {e}")
            return False
