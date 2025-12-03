# path: src/ui/config/centro_tab.py
import streamlit as st
from services.permissions_service import has_permission

def render_centro_tab(centro_config):
    """Renderiza la pestaña de Configuración del Centro."""
    # Sub-tabs dinámicas según permisos
    subtabs_map = {}
    subtabs_map["Datos"] = "📋 Datos Generales"
    subtabs_map["Salas"] = "🏢 Salas (Orquestador)"
    
    if has_permission("configuracion", "usuarios"):
        subtabs_map["Usuarios"] = "👤 Gestión de Usuarios"
        subtabs_map["GestionTurnos"] = "📅 Gestión de Turnos (Temporal)"
    
    if has_permission("configuracion", "roles"):
        subtabs_map["Roles"] = "🛡️ Gestión de Roles"
        
    subtabs_map["Grupos"] = "🌐 Grupos (Multi-Tenant)"
        
    selected_subtabs = st.tabs(list(subtabs_map.values()))
    
    subtab_datos = selected_subtabs[list(subtabs_map.keys()).index("Datos")]
    subtab_salas = selected_subtabs[list(subtabs_map.keys()).index("Salas")]
    subtab_usuarios = selected_subtabs[list(subtabs_map.keys()).index("Usuarios")] if "Usuarios" in subtabs_map else None
    subtab_roles = selected_subtabs[list(subtabs_map.keys()).index("Roles")] if "Roles" in subtabs_map else None
    subtab_turnos = selected_subtabs[list(subtabs_map.keys()).index("GestionTurnos")] if "GestionTurnos" in subtabs_map else None
    subtab_grupos = selected_subtabs[list(subtabs_map.keys()).index("Grupos")]

    with subtab_datos:
        from ui.config.datos_generales import render_datos_generales
        render_datos_generales()
    
    with subtab_salas:
        st.info("Gestión integral de salas, asignaciones y control.")
        tab_gestion, tab_asignacion, tab_control = st.tabs([
            "🛠️ Gestión de Salas", 
            "📍 Asignación (Fija)", 
            "🎮 Control de Salas"
        ])
        
        with tab_gestion:
            from ui.config.salas_manager import render_salas_manager
            existing_salas = centro_config.get('salas', [])
            render_salas_manager(centro_id=centro_config.get('_id'), existing_salas=existing_salas)
        
        with tab_asignacion:
            from ui.config.asignacion_turnos import render_asignacion_turnos
            existing_salas = centro_config.get('salas', [])
            render_asignacion_turnos(salas=existing_salas)
            
        with tab_control:
            from ui.room_manager_view import mostrar_gestor_salas
            mostrar_gestor_salas()
    
    if subtab_usuarios:
        with subtab_usuarios:
            from ui.config.usuarios_manager import render_usuarios_manager
            render_usuarios_manager()

    if subtab_roles:
        with subtab_roles:
            from ui.config.roles_manager import render_roles_manager
            render_roles_manager()
            
    if subtab_turnos:
        with subtab_turnos:
            from ui.shift_manager_advanced import render_advanced_shift_manager
            render_advanced_shift_manager()
            
    with subtab_grupos:
        from ui.config.center_groups_manager import render_center_groups_manager
        render_center_groups_manager()

