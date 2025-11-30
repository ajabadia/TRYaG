# path: src/ui/config/app_config.py
# Creado: 2025-11-28
"""
UI para configuración de la aplicación (Validación, Modelos IA).
Componente modular para la sección General > Aplicación.
"""
import streamlit as st
from src.db.repositories.general_config import get_general_config_repository

def save_general_config(config):
    """Guarda la configuración general en MongoDB."""
    repo = get_general_config_repository()
    return repo.save_config(config)

def render_app_config():
    """
    Renderiza el formulario de configuración de la aplicación.
    Incluye: Validación de formularios y selección de modelos IA.
    """
    # Asegurar que la configuración está cargada
    if 'general_config' not in st.session_state:
        repo = get_general_config_repository()
        st.session_state.general_config = repo.get_config()
        
    general_config = st.session_state.general_config

    with st.container(border=True):
        st.markdown("#### :material/rule: Validación de Formularios")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Caracteres mínimos en 'Motivo de Consulta'**")
            st.caption("Define el número mínimo de caracteres requeridos en el campo de texto libre.")
        with col2:
            new_min_chars = st.number_input(
                "Mínimo",
                min_value=1,
                max_value=100,
                value=general_config.get('min_chars_motivo', 3),
                step=1,
                key="min_chars_input",
                label_visibility="collapsed",
            )
        st.divider()
        st.markdown("#### :material/psychology: Modelos de IA")
        st.caption("Gestión de modelos Gemini disponibles y configuración por defecto.")
        
        # --- Sección de Descubrimiento de Modelos ---
        from src.services.ai_model_discovery import fetch_and_update_models
        from src.db.repositories.ai_models import get_ai_models_repository
        
        col_check, col_info = st.columns([1, 2])
        with col_check:
            if st.button("🔄 Comprobar modelos IA", help="Consulta a Google los modelos disponibles y actualiza la base de datos"):
                with st.spinner("Consultando API de Google..."):
                    success, msg, count = fetch_and_update_models()
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        
        # Obtener modelos disponibles
        models_repo = get_ai_models_repository()
        available_models = models_repo.get_available_models()
        
        if not available_models:
            st.warning("No hay modelos registrados. Pulsa 'Comprobar modelos IA'.")
            available_models = ["gemini-2.5-flash"] # Fallback visual
            
        with st.expander("Ver lista de modelos disponibles", expanded=False):
            st.dataframe(
                [{"Modelo": m} for m in available_models],
                use_container_width=True,
                hide_index=True
            )

        # --- Selección de Modelo por Defecto ---
        current_default = general_config.get('default_ai_model', "gemini-2.5-flash")
        if current_default not in available_models:
            available_models.append(current_default)
            
        new_default_model = st.selectbox(
            "Modelo Predeterminado Global",
            options=available_models,
            index=available_models.index(current_default) if current_default in available_models else 0,
            help="Este modelo se usará si un prompt no especifica uno propio."
        )
        
        st.markdown("**Funcionalidades IA**")
        enable_predictive_alerts = st.checkbox(
            "Habilitar Alertas Predictivas (Pre-Triaje)",
            value=general_config.get('enable_predictive_alerts', True),
            help="Si está desactivado, se ocultará el botón de análisis de riesgos para ahorrar tokens."
        )
        # Botones Guardar / Restaurar
        col_save, col_reset, _ = st.columns([1, 1, 2])
        with col_save:
            if st.button(":material/save: Guardar Cambios", use_container_width=True, type="primary"):
                general_config['min_chars_motivo'] = new_min_chars
                general_config['default_ai_model'] = new_default_model
                general_config['enable_predictive_alerts'] = enable_predictive_alerts
                if save_general_config(general_config):
                    st.session_state.general_config = general_config
                    st.success(":material/check_circle: Configuración guardada correctamente")
                    st.info(":material/refresh: Recargando aplicación...")
                    st.rerun()
                else:
                    st.error(":material/error: Error al guardar la configuración")
        with col_reset:
            if st.button(":material/restore: Restaurar Valores por Defecto", use_container_width=True):
                default_config = {"min_chars_motivo": 3}
                if save_general_config(default_config):
                    st.session_state.general_config = default_config
                    st.success(":material/check_circle: Configuración restaurada a valores por defecto")
                    st.rerun()
                else:
                    st.error(":material/error: Error al restaurar la configuración")
        st.divider()
        st.markdown("##### :material/info: Información")
        st.caption(":material/database: Configuración almacenada en MongoDB Atlas")
        st.caption(":material/tips_and_updates: Los cambios se aplican automáticamente al guardar.")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/config/app_config.py</div>', unsafe_allow_html=True)
