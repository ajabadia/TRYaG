import streamlit as st
from db import get_database
from .debug_modules.collection_inspector import render_collection_inspector

def render_debug_panel_modular(key_prefix="debug_modular"):
    """
    Orquestador modular del panel de depuración de MongoDB.
    Itera sobre las colecciones y renderiza el inspector para cada una.
    """
    st.subheader("🔍 Inspector de MongoDB Atlas")
    
    try:
        db = get_database()
        all_collections = sorted(db.list_collection_names())
        
        if not all_collections:
            st.warning("No se encontraron colecciones.")
            return

        # Definir Mapeo de Categorías
        CATEGORIES = {
            "🏥 Actividad Clínica": [
                "triage_records", "patients", "patient_flow", 
                "transcriptions_records", "file_import_records", "clinical_options"
            ],
            "👥 Gestión & Usuarios": [
                "users", "login_logs", "people", "turnos", 
                "roles", "centros", "salas"
            ],
            "🤖 Inteligencia Artificial": [
                "ai_audit_logs", "ai_models", "prompt_tests", 
                "prompts", "feedback_reports"
            ],
            "⚙️ Sistema": [
                "audit_log", "notifications", "config", "counters"
            ]
        }

        # Selector de Categoría
        cat_selection = st.radio(
            "Categoría:",
            ["🏥 Actividad Clínica", "👥 Gestión & Usuarios", "🤖 Inteligencia Artificial", "⚙️ Sistema", "📂 Otros"],
            horizontal=True,
            label_visibility="collapsed"
        )

        # Filtrar colecciones
        filtered_cols = []
        if cat_selection == "📂 Otros":
            # Todo lo que no esté en las otras listas
            known_cols = set([c for sublist in CATEGORIES.values() for c in sublist])
            filtered_cols = [c for c in all_collections if c not in known_cols]
        else:
            target_list = CATEGORIES.get(cat_selection, [])
            filtered_cols = [c for c in all_collections if c in target_list]

        if not filtered_cols:
            st.info(f"No hay colecciones en esta categoría ({cat_selection}).")
            return

        # Crear pestañas dinámicas para la categoría seleccionada
        tabs = st.tabs([f"🗄️ {c}" for c in filtered_cols])
        
        for i, collection_name in enumerate(filtered_cols):
            with tabs[i]:
                # Determinar campo de fecha principal para cada colección
                date_field = "timestamp"
                if collection_name in ['config', 'centros', 'roles', 'clinical_options']:
                    date_field = "updated_at"
                elif collection_name in ['prompts', 'users', 'people', 'patients']:
                    date_field = "created_at"
                elif collection_name == 'ai_audit_logs':
                    date_field = "timestamp_start"
                elif collection_name == 'turnos':
                    date_field = "fecha_desde"
                
                # Renderizar el módulo inspector
                render_collection_inspector(
                    collection_name=collection_name,
                    key_prefix=f"{key_prefix}_{collection_name}",
                    date_field=date_field
                )

    except Exception as e:
        st.error(f"Error al conectar con MongoDB: {e}")
        st.markdown('<div class="debug-footer">src/ui/audit_panel/debug_panel_modular.py</div>', unsafe_allow_html=True)
