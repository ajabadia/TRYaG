# path: src/ui/audit_panel/raw_data_panel_v2.py
"""
Módulo orquestador para la visualización de la pestaña "Datos en Bruto" (Versión Modular V2).
Cada pestaña gestiona sus propios filtros y fechas.
"""

import streamlit as st
import pandas as pd

# Importar componentes de pestañas V2
from .tab_audit_v2 import render_tab_audit_v2
from .tab_files_v2 import render_tab_files_v2
from .tab_transcriptions_v2 import render_tab_transcriptions_v2
from .feedback_list_v2 import render_feedback_list_v2
# Para prompts, usaremos el existente por ahora o crearemos wrapper si es necesario
from components.audit.prompt_log import render_prompt_log_final

def mostrar_panel_datos_brutos_v2(df_audit_base, df_files, df_trans, df_feedback):
    """
    Renderiza la pestaña "Datos en Bruto" V2.
    Ya no recibe fechas globales, solo los DataFrames.
    """
    st.subheader("Registro Completo de Decisiones (Modular)")

    # -----------------------------------------------------------------
    # Pestañas con sus respectivos renderizados
    # -----------------------------------------------------------------
    tab_registros_padre, tab_log_ficheros, tab_log_trans, tab_log_prompts, tab_feedback = st.tabs([
        "📋 Registros de Auditoría",
        "📂 Log de Ficheros Importados",
        "🎙️ Log de Transcripciones",
        "📜 Log de Prompts",
        "🐛 Feedback & Errores",
    ])

    with tab_registros_padre:
        render_tab_audit_v2(df_audit_base, df_files)

    with tab_log_ficheros:
        render_tab_files_v2(df_files)

    with tab_log_trans:
        render_tab_transcriptions_v2(df_trans)

    with tab_log_prompts:
        render_prompt_log_final()

    with tab_feedback:
        render_feedback_list_v2(df_feedback)
    
    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/audit_panel/raw_data_panel_v2.py</div>', unsafe_allow_html=True)
