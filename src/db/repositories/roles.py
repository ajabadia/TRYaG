# path: src/db/repositories/roles.py
# Creado: 2025-11-25
# Modificado: 2025-11-27 (Persistencia DB)
"""
Repositorio de Roles del sistema.
Maneja la colección 'roles' en MongoDB, con fallback a roles por defecto.
"""
from typing import List, Dict, Optional
from src.db.connection import get_database
from datetime import datetime

# Definición de Roles por Defecto (Seeding)
DEFAULT_ROLES = [
    {
        "code": "superadministrador",
        "nombre": "Super Administrador",
        "descripcion": "Acceso total al sistema",
        "permissions": {
            "admision": {"view": True, "create": True, "edit": True, "delete": True},
            "triaje": {"view": True, "create": True, "edit": True, "delete": True},
            "atencion_box": {"view": True, "create": True, "edit": True, "delete": True},
            "consulta_ingreso": {"view": True, "create": True, "edit": True, "delete": True},
            "auditoria": {"view": True, "export": True},
            "control_salas": {"view": True, "manage": True},
            "configuracion": {
                "general": True,
                "centro": True,
                "prompts": True,
                "usuarios": True,
                "roles": True
            }
        },
        "funciones_permitidas": ["administrativo", "enfermero", "medico", "analista_datos"],
        "nivel_acceso": 100,
        "system_role": True
    },
    {
        "code": "administrador",
        "nombre": "Administrador",
        "descripcion": "Gestión completa excepto auditoría avanzada",
        "permissions": {
            "admision": {"view": True, "create": True, "edit": True, "delete": True},
            "triaje": {"view": True, "create": True, "edit": True, "delete": True},
            "atencion_box": {"view": True, "create": True, "edit": True, "delete": True},
            "consulta_ingreso": {"view": True, "create": True, "edit": True, "delete": True},
            "auditoria": {"view": False, "export": False},
            "control_salas": {"view": True, "manage": True},
            "configuracion": {
                "general": True,
                "centro": True,
                "prompts": False,
                "usuarios": True,
                "roles": True
            }
        },
        "funciones_permitidas": ["administrativo", "enfermero", "medico"],
        "nivel_acceso": 80,
        "system_role": True
    },
    {
        "code": "auditor",
        "nombre": "Analista de Datos / Auditor",
        "descripcion": "Acceso a auditoría y configuración de prompts",
        "permissions": {
            "admision": {"view": False, "create": False, "edit": False, "delete": False},
            "triaje": {"view": False, "create": False, "edit": False, "delete": False},
            "atencion_box": {"view": False, "create": False, "edit": False, "delete": False},
            "consulta_ingreso": {"view": False, "create": False, "edit": False, "delete": False},
            "auditoria": {"view": True, "export": True},
            "control_salas": {"view": False, "manage": False},
            "configuracion": {
                "general": False,
                "centro": False,
                "prompts": True,
                "usuarios": False,
                "roles": False
            }
        },
        "funciones_permitidas": ["analista_datos"],
        "nivel_acceso": 20,
        "system_role": True
    },
    {
        "code": "usuario",
        "nombre": "Usuario Clínico",
        "descripcion": "Acceso a funciones clínicas según función asignada",
        "permissions": {
            "admision": {"view": True, "create": True, "edit": True, "delete": False},
            "triaje": {"view": True, "create": True, "edit": True, "delete": False},
            "atencion_box": {"view": True, "create": True, "edit": True, "delete": False},
            "consulta_ingreso": {"view": True, "create": True, "edit": True, "delete": False},
            "auditoria": {"view": False, "export": False},
            "control_salas": {"view": True, "manage": False},
            "configuracion": {
                "general": False,
                "centro": False,
                "prompts": False,
                "usuarios": False,
                "roles": False
            }
        },
        "funciones_permitidas": ["enfermero", "medico", "administrativo"],
        "nivel_acceso": 50,
        "system_role": True
    }
]

class RolesRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.roles
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Inicializa los roles por defecto si la colección está vacía."""
        if self.collection.count_documents({}) == 0:
            for role in DEFAULT_ROLES:
                role_data = role.copy()
                role_data["created_at"] = datetime.now()
                role_data["updated_at"] = datetime.now()
                self.collection.insert_one(role_data)

    def get_all_roles(self) -> List[Dict]:
        """Retorna todos los roles."""
        return list(self.collection.find({}))

    def get_role_by_code(self, code: str) -> Optional[Dict]:
        """Obtiene un rol por su código."""
        return self.collection.find_one({"code": code})

    def update_role(self, code: str, updates: Dict) -> bool:
        """Actualiza un rol existente."""
        updates["updated_at"] = datetime.now()
        result = self.collection.update_one(
            {"code": code},
            {"$set": updates}
        )
        return result.modified_count > 0

    def create_role(self, role_data: Dict) -> bool:
        """Crea un nuevo rol."""
        if self.get_role_by_code(role_data.get("code")):
            return False
        
        role_data["created_at"] = datetime.now()
        role_data["updated_at"] = datetime.now()
        self.collection.insert_one(role_data)
        return True

_roles_repo = None

def get_roles_repository() -> RolesRepository:
    global _roles_repo
    if _roles_repo is None:
        _roles_repo = RolesRepository()
    return _roles_repo

# Funciones helper para mantener compatibilidad
def get_all_roles() -> List[Dict]:
    return get_roles_repository().get_all_roles()

def get_role_by_code(code: str) -> Optional[Dict]:
    return get_roles_repository().get_role_by_code(code)
