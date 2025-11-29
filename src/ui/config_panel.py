# path: src/ui/config_panel.py
# Creado: 2025-11-23
# Actualizado: 2025-11-25 - Refactorizado con sub‑tabs y módulos
"""
Panel de configuración de la aplicación.
Incluye pestañas: General, Centro (con sub‑tabs), Prompts y Notificaciones.
"""
import os
import json
import streamlit as st
from utils.icons import render_icon
from src.db.repositories.centros import get_centros_repository

# ---------------------------------------------------------------------------
# Configuración general (JSON en disco)
# ---------------------------------------------------------------------------
from src.db.repositories.general_config import get_general_config_repository

def load_general_config():
    """Carga la configuración general desde MongoDB."""
    repo = get_general_config_repository()
    return repo.get_config()

def save_general_config(config):
    """Guarda la configuración general en MongoDB."""
    repo = get_general_config_repository()
    return repo.save_config(config)

# ---------------------------------------------------------------------------
# Configuración del centro (MongoDB)
# ---------------------------------------------------------------------------

def load_centro_config():
    """Carga la configuración del centro desde MongoDB."""
    try:
        centros_repo = get_centros_repository()
        centro = centros_repo.get_centro_principal()
        if centro:
            if '_id' in centro:
                centro['_id'] = str(centro['_id'])
            return centro
    except Exception as e:
        st.error(f"Error al cargar configuración del centro: {e}")
    # Valores por defecto
    return {
        "codigo": "",
        "denominacion": "",
        "cif": "",
        "direccion": "",
        "email": "",
        "telefono": "",
        "logo_path": "",
        "mensaje": "",
        "salas": [],
    }


def save_centro_config(config):
    """Guarda la configuración del centro en MongoDB."""
    try:
        centros_repo = get_centros_repository()
        centros_repo.create_or_update_centro(
            codigo=config.get('codigo', ''),
            denominacion=config.get('denominacion', ''),
            cif=config.get('cif'),
            direccion=config.get('direccion'),
            email=config.get('email'),
            telefono=config.get('telefono'),
            logo_path=config.get('logo_path'),
            mensaje=config.get('mensaje'),
            salas=config.get('salas', []),
            updated_by="admin",
        )
        return True
    except Exception as e:
        st.error(f"Error al guardar configuración del centro: {e}")
        return False

# ---------------------------------------------------------------------------
# UI principal
# ---------------------------------------------------------------------------
def mostrar_panel_configuracion():
    """Muestra el panel de configuración con pestañas modulares."""
    from ui.loading_indicator import loading_data

    st.header(":material/settings: Configuración")

    # Cargar configuración en session_state (una sola vez)
    if 'general_config' not in st.session_state:
        st.session_state.general_config = load_general_config()
    if 'centro_config' not in st.session_state:
        st.session_state.centro_config = load_centro_config()

    general_config = st.session_state.general_config
    centro_config = st.session_state.centro_config

    # -------------------------------------------------------------------
    # Pestañas principales
    # -------------------------------------------------------------------
    from services.permissions_service import has_permission

    # -------------------------------------------------------------------
    # Pestañas principales (Dinámicas según permisos)
    # -------------------------------------------------------------------
    tabs_map = {}
    
    # Siempre mostrar General si tiene acceso al panel
    tabs_map["General"] = ":material/tune: General"
    
    if has_permission("configuracion", "centro"):
        tabs_map["Centro"] = ":material/business: Centro"
        
    # Prompts movido a General > Prompts
        
    # Notificaciones movido a General > Notificaciones

    selected_tabs = st.tabs(list(tabs_map.values()))
    
    # Asignar variables a las tabs creadas para usar abajo
    tab_general = selected_tabs[list(tabs_map.keys()).index("General")]
    tab_centro = selected_tabs[list(tabs_map.keys()).index("Centro")] if "Centro" in tabs_map else None


    # -------------------------------------------------------------------
    # Tab General (validación y modelos IA)
    # -------------------------------------------------------------------
    with tab_general:
        st.markdown("### :material/tune: Configuración General")
        
        # Sub-tabs de General
        gen_tabs = ["📱 Aplicación", "📷 Equipamiento", "💓 Signos Vitales", "📋 Opciones Clínicas"]
        
        if has_permission("configuracion", "prompts"):
            gen_tabs.append("📝 Prompts IA")

        if has_permission("configuracion", "general"):
            gen_tabs.append("🔔 Notificaciones")
            
        gen_subtabs = st.tabs(gen_tabs)
        
        # Helper to get tab by label
        def get_tab(label):
            try:
                return gen_subtabs[gen_tabs.index(label)]
            except ValueError:
                return None

        subtab_app = get_tab("📱 Aplicación")
        subtab_equip = get_tab("📷 Equipamiento")
        subtab_vitals = get_tab("💓 Signos Vitales")
        subtab_clinical = get_tab("📋 Opciones Clínicas")
        subtab_prompts = get_tab("📝 Prompts IA")
        subtab_notif = get_tab("🔔 Notificaciones")
        
        with subtab_equip:
            from ui.config.equipment_config import render_equipment_config
            render_equipment_config()

        with subtab_vitals:
            from ui.config.vital_signs_config import render_vital_signs_config
            render_vital_signs_config()
            
        with subtab_clinical:
            from ui.config.clinical_options_manager import render_clinical_options_manager
            render_clinical_options_manager()
            
        if subtab_prompts:
            with subtab_prompts:
                from components.config.prompt_manager import render_prompt_manager
                render_prompt_manager()

        if subtab_notif:
            with subtab_notif:
                from ui.config.notification_config_ui import render_notification_config_panel
                render_notification_config_panel()

        with subtab_app:
            from ui.config.app_config import render_app_config
            render_app_config()

    # -------------------------------------------------------------------
    # Tab Centro – sub‑tabs modulares
    # -------------------------------------------------------------------
    if tab_centro:
        with tab_centro:
            # Sub-tabs dinámicas según permisos
            subtabs_map = {}
            subtabs_map["Datos"] = "📋 Datos Generales"
            subtabs_map["Salas"] = "🏢 Salas (Orquestador)"
            
            if has_permission("configuracion", "usuarios"):
                subtabs_map["Usuarios"] = "👤 Gestión de Usuarios"
                subtabs_map["GestionTurnos"] = "📅 Gestión de Turnos (Temporal)"
            
            if has_permission("configuracion", "roles"):
                subtabs_map["Roles"] = "🛡️ Gestión de Roles"
                
            selected_subtabs = st.tabs(list(subtabs_map.values()))
            
            subtab_datos = selected_subtabs[list(subtabs_map.keys()).index("Datos")]
            subtab_salas = selected_subtabs[list(subtabs_map.keys()).index("Salas")]
            subtab_usuarios = selected_subtabs[list(subtabs_map.keys()).index("Usuarios")] if "Usuarios" in subtabs_map else None
            subtab_roles = selected_subtabs[list(subtabs_map.keys()).index("Roles")] if "Roles" in subtabs_map else None
            subtab_turnos = selected_subtabs[list(subtabs_map.keys()).index("GestionTurnos")] if "GestionTurnos" in subtabs_map else None

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
                    render_salas_manager(existing_salas=existing_salas)
                
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

    # -------------------------------------------------------------------
    # Tab Prompts – edición de prompts IA
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # Tab Prompts – Movido a General
    # -------------------------------------------------------------------

    # -------------------------------------------------------------------
    # Tab Notificaciones – UI modular ya creada
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # Tab Notificaciones – Movido a General
    # -------------------------------------------------------------------

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/config_panel.py</div>', unsafe_allow_html=True)
