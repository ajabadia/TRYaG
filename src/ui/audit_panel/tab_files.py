# path: src/ui/audit_panel/tab_files.py
# Creado: 2025-11-23
"""
Módulo para la pestaña "Log de Ficheros Importados".
"""
import streamlit as st
from components.audit.filters import render_file_filters, apply_file_filters
from components.audit.file_log import render_file_log

def render_tab_files(df_files, start_date, end_date, key_prefix="files_log"):
    """Renderiza el contenido de la pestaña de ficheros."""
    st.markdown("##### Registro de Ficheros")
    
    # Filtros específicos
    selected_type, selected_source = render_file_filters(df_files)
    
    # Aplicar filtros
    df_files_filtered = apply_file_filters(df_files, start_date, end_date, selected_type, selected_source)
    
    render_file_log(df_files_filtered, start_date, end_date, key_prefix=key_prefix)

    st.markdown('<div class="debug-footer">src/ui/audit_panel/tab_files.py</div>', unsafe_allow_html=True)
