# path: src/utils/session_utils.py
# Creado: 2025-11-23
"""
Utilidades para la gestión del estado de la sesión (Session State).
"""
import streamlit as st

def reset_session_state():
    """
    Reinicia el estado de la sesión de forma segura.
    Resetea las variables de estado de la aplicación a sus valores por defecto
    e incrementa el contador de reset para forzar la recreación de widgets.
    """
    # 1. Resetear variables de estado de la aplicación (definidas en app.py)
    st.session_state.resultado = None
    st.session_state.datos_paciente = {
        "texto_medico": "",
        "edad": 40,
        "dolor": 5,
        "imagenes": [],
        "imagenes_confirmadas_ia": []
    }
    st.session_state.calificacion_humana = None
    st.session_state.send_to_ai_checked = False
    st.session_state.modal_image_selection = {}
    st.session_state.analysis_complete = False
    st.session_state.show_text_error = False
    st.session_state.is_editing_text = True
    
    # Variables de validación (validation_form.py)
    if 'validation_complete' in st.session_state:
        del st.session_state['validation_complete']
    if 'validation_msg' in st.session_state:
        del st.session_state['validation_msg']
    if 'validation_msg_type' in st.session_state:
        del st.session_state['validation_msg_type']
        
    # Variables temporales
    if 'temp_recorded_audio' in st.session_state:
        del st.session_state['temp_recorded_audio']
    if 'deleted_filenames' in st.session_state:
        del st.session_state['deleted_filenames']

    # 2. Incrementar contador de reset para invalidar claves de widgets
    if 'reset_counter' not in st.session_state:
        st.session_state.reset_counter = 0
    st.session_state.reset_counter += 1
