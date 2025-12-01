# path: src/services/permissions_service.py
# Creado: 2025-11-25
"""
Servicio de gestión de permisos y control de acceso (RBAC).
"""
import streamlit as st
from typing import List, Dict, Optional
from db.repositories.roles import get_role_by_code

def get_current_user() -> Optional[Dict]:
    """Retorna el usuario actual de la sesión o None."""
    return st.session_state.get("current_user")

def has_permission(module: str, action: str = "view") -> bool:
    """
    Verifica si el usuario actual tiene permiso para una acción en un módulo.
    
    Args:
        module: Nombre del módulo (admision, triaje, configuracion, etc.)
        action: Acción requerida (view, create, edit, delete, manage, export)
    """
    user = get_current_user()
    if not user:
        return False
        
    role_code = user.get("rol")
    role_def = get_role_by_code(role_code)
    
    if not role_def:
        return False
        
    # Superadmin tiene acceso total
    if role_code == "superadministrador":
        return True
        
    permissions = role_def.get("permissions", {})
    module_perms = permissions.get(module, {})
    
    # Si el módulo no está definido en permisos, denegar por defecto
    if not module_perms:
        return False
    
    # Si el permiso es un booleano directo (caso simple)
    if isinstance(module_perms, bool):
        return module_perms
        
    # Si es diccionario, buscar la acción específica
    # Si la acción es 'general' (usada para acceso a tab), verificar 'view' o si existe alguna key True
    if action == "general":
        if isinstance(module_perms, dict):
            return any(module_perms.values())
        return bool(module_perms)

    return module_perms.get(action, False)

def get_available_tabs() -> List[str]:
    """
    Retorna la lista de pestañas principales disponibles para el usuario actual.
    """
    tabs = []
    
    if has_permission("admision", "view"):
        tabs.append("📋 Admisión")
        
    if has_permission("triaje", "view"):
        tabs.append("🩺 Triaje")
        
    if has_permission("atencion_box", "view"):
        tabs.append("🏥 Atención Box")

    # Sala de Espera visible para Triaje o Atención
    if has_permission("triaje", "view") or has_permission("atencion_box", "view"):
        tabs.append("🪑 Sala de Espera")
        
    if has_permission("consulta_ingreso", "view"):
        tabs.append("👨‍⚕️ Consulta")
        
    if has_permission("auditoria", "view"):
        tabs.append("📊 Auditoría")


    # Control de Salas movido a Configuración > Centro > Salas
    # if has_permission("control_salas", "view"):
    #     tabs.append("🎛️ Control de Salas")
        
    # Configuración requiere permiso en alguno de sus sub-módulos
    if has_permission("configuracion", "general"):
        tabs.append("⚙️ Configuración")
        
    return tabs
