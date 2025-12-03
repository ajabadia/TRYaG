import streamlit as st
from db import get_database
from .debug_modules.collection_inspector import render_collection_inspector

def render_debug_panel_modular(key_prefix="debug_modular"):
    """
    Orquestador modular del panel de depuración de MongoDB.
    Itera sobre las colecciones y renderiza el inspector para cada una.
    """
    st.subheader("🔍 Inspector de MongoDB Atlas (Modular)")
    
    try:
        db = get_database()
        collections = sorted(db.list_collection_names())
        
        if not collections:
            st.warning("No se encontraron colecciones.")
            return

        # Crear pestañas dinámicas
        tabs = st.tabs([f"🗄️ {c}" for c in collections])
        
        for i, collection_name in enumerate(collections):
            with tabs[i]:
                # Determinar campo de fecha principal para cada colección
                date_field = "timestamp"
                if collection_name in ['config', 'centros', 'roles']:
                    date_field = "updated_at"
                elif collection_name in ['prompts', 'users']:
                    date_field = "created_at"
                elif collection_name == 'ai_audit_logs':
                    date_field = "timestamp_start"
                
                # Renderizar el módulo inspector
                render_collection_inspector(
                    collection_name=collection_name,
                    key_prefix=key_prefix,
                    date_field=date_field
                )

    except Exception as e:
        st.error(f"Error al conectar con MongoDB: {e}")
        st.markdown('<div class="debug-footer">src/ui/audit_panel/debug_panel_modular.py</div>', unsafe_allow_html=True)
