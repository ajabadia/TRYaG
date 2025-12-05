import streamlit as st
from services.permissions_service import has_permission

def render_ai_config_ui():
    """
    Renderiza el panel de configuración de Inteligencia Artificial.
    Agrupa Prompts y Base de Conocimiento (RAG).
    """
    st.markdown("### 🧠 Configuración de Inteligencia Artificial")
    
    tabs = []
    
    # Tab 1: Prompts (Existente)
    if has_permission("configuracion", "prompts"):
        tabs.append("📝 Prompts")
        
    # Tab 2: Base de Conocimiento (Nuevo)
    # Asumimos que requiere el mismo permiso o uno nuevo 'rag'
    # Por ahora usamos 'prompts' o 'general' como fallback si no existe 'rag'
    if has_permission("configuracion", "prompts"): 
        tabs.append("📚 Base de Conocimiento (RAG)")
        
    if not tabs:
        st.warning("No tienes permisos para configurar la IA.")
        return

    selected_tab = st.tabs(tabs)
    
    # Renderizar contenido
    for i, tab_name in enumerate(tabs):
        with selected_tab[i]:
            if tab_name == "📝 Prompts":
                from components.config.prompt_manager import render_prompt_manager
                render_prompt_manager()
                
            elif tab_name == "📚 Base de Conocimiento (RAG)":
                from ui.config.knowledge_base_ui import render_knowledge_base_ui
                render_knowledge_base_ui()
