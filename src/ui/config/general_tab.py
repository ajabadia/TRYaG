# path: src/ui/config/general_tab.py
import streamlit as st
from services.permissions_service import has_permission

def render_general_tab():
    """Renderiza la pestaña de Configuración General."""
    st.markdown("### 🎛️ Configuración General")
    
    # Sub-tabs de General
    gen_tabs = ["📱 Aplicación", "📷 Equipamiento", "💓 Signos Vitales", "📋 Opciones Clínicas", "🏥 Aseguradoras"]
    
    if has_permission("configuracion", "prompts"):
        gen_tabs.append("📝 Prompts IA")

    if has_permission("configuracion", "general"):
        gen_tabs.append("🔔 Notificaciones")

    # PTR Config (Phase 8.6)
    gen_tabs.append("🚑 Triaje (PTR)")
        
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
    subtab_insurers = get_tab("🏥 Aseguradoras")
    subtab_prompts = get_tab("📝 Prompts IA")
    subtab_notif = get_tab("🔔 Notificaciones")
    subtab_ptr = get_tab("🚑 Triaje (PTR)")
    
    with subtab_equip:
        from ui.config.equipment_config import render_equipment_config
        render_equipment_config()

    with subtab_vitals:
        from ui.config.vital_signs_config import render_vital_signs_config
        render_vital_signs_config()
        
    with subtab_clinical:
        from ui.config.clinical_options_manager import render_clinical_options_manager
        render_clinical_options_manager()
        
    with subtab_insurers:
        from ui.config.insurers_manager import render_insurers_manager
        render_insurers_manager()
        
    if subtab_prompts:
        with subtab_prompts:
            from components.config.prompt_manager import render_prompt_manager
            render_prompt_manager()

    if subtab_notif:
        with subtab_notif:
            from ui.config.notification_config_ui import render_notification_config_panel
            render_notification_config_panel()

    if subtab_ptr:
        with subtab_ptr:
            from ui.config.ptr_config_panel import render_ptr_config_panel
            render_ptr_config_panel()

    with subtab_app:
        from ui.config.app_config import render_app_config
        render_app_config()
