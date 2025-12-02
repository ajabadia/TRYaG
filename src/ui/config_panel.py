# path: src/ui/config_panel.py
# Creado: 2025-11-23
# Actualizado: 2025-12-01 - Refactorizado en módulos (Loader, General, Centro)
"""
Panel de configuración de la aplicación.
Orquesta las pestañas principales delegando en módulos específicos.
"""
import streamlit as st
from ui.components.common.tools_panel import render_tools_panel
from ui.config.config_loader import load_general_config, load_centro_config
from ui.config.general_tab import render_general_tab
from ui.config.centro_tab import render_centro_tab
from services.permissions_service import has_permission

def mostrar_panel_configuracion():
    """Muestra el panel de configuración con pestañas modulares."""
    
    st.header("⚙️ Configuración")
    
    # Panel de Herramientas
    render_tools_panel("Configuración", show_pdf=False)

    # Cargar configuración en session_state (una sola vez)
    if 'general_config' not in st.session_state:
        st.session_state.general_config = load_general_config()
    if 'centro_config' not in st.session_state:
        st.session_state.centro_config = load_centro_config()

    # -------------------------------------------------------------------
    # Pestañas principales (Dinámicas según permisos)
    # -------------------------------------------------------------------
    tabs_map = {}
    
    # Siempre mostrar General si tiene acceso al panel
    tabs_map["General"] = "🎛️ General"
    
    if has_permission("configuracion", "centro"):
        tabs_map["Centro"] = "🏢 Centro"

    selected_tabs = st.tabs(list(tabs_map.values()))
    
    # Asignar variables a las tabs creadas
    tab_general = selected_tabs[list(tabs_map.keys()).index("General")]
    tab_centro = selected_tabs[list(tabs_map.keys()).index("Centro")] if "Centro" in tabs_map else None

    # -------------------------------------------------------------------
    # Renderizar Pestañas
    # -------------------------------------------------------------------
    with tab_general:
        render_general_tab()

    if tab_centro:
        with tab_centro:
            render_centro_tab(st.session_state.centro_config)

    st.markdown('<div class="debug-footer">src/ui/config_panel.py</div>', unsafe_allow_html=True)
