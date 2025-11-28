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
        st.caption("Configura los identificadores de los modelos Gemini a utilizar.")
        col_ia1, col_ia2 = st.columns(2)
        with col_ia1:
            model_triage = st.text_input(
                "Modelo Triaje",
                value=general_config.get('model_triage', "gemini-2.5-flash"),
                help="Modelo usado para el razonamiento clínico",
            )
        with col_ia2:
            model_transcription = st.text_input(
                "Modelo Transcripción",
                value=general_config.get('model_transcription', "gemini-2.5-flash"),
                help="Modelo usado para audio",
            )
        # Botones Guardar / Restaurar
        col_save, col_reset, _ = st.columns([1, 1, 2])
        with col_save:
            if st.button(":material/save: Guardar Cambios", use_container_width=True, type="primary"):
                general_config['min_chars_motivo'] = new_min_chars
                general_config['model_triage'] = model_triage
                general_config['model_transcription'] = model_transcription
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
