# path: src/ui/audit_panel/tab_transcriptions.py
# Creado: 2025-11-23
"""
Módulo para la pestaña "Log de Transcripciones".
"""
import streamlit as st
from components.audit.filters import render_transcription_filters, apply_transcription_filters
from components.audit.transcription_log import render_transcription_log

def render_tab_transcriptions(df_trans, start_date, end_date, key_prefix="trans_log"):
    """Renderiza el contenido de la pestaña de transcripciones."""
    st.markdown("##### Registro de Transcripciones")
    
    # Filtros específicos
    selected_source, selected_lang = render_transcription_filters(df_trans)
    
    # Aplicar filtros
    df_trans_filtered = apply_transcription_filters(df_trans, start_date, end_date, selected_source, selected_lang)
    
    render_transcription_log(df_trans_filtered, start_date, end_date, key_prefix=key_prefix)

    st.markdown('<div class="debug-footer">src/ui/audit_panel/tab_transcriptions.py</div>', unsafe_allow_html=True)
