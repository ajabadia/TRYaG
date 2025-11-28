# path: src/ui/audit_panel/raw_data_panel.py
# Creado: 2025-11-21
# Última modificación: 2025-11-28
"""
Módulo orquestador para la visualización de la pestaña "Datos en Bruto"
del panel de auditoría. Importa y ensambla componentes modulares divididos en pestañas.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Importar componentes de pestañas
from .tab_audit import render_tab_audit
from .tab_files import render_tab_files
from .tab_transcriptions import render_tab_transcriptions
from components.audit.prompt_log import render_prompt_log_final
from .feedback_list import render_feedback_list
from .components import render_date_selector

def _obtener_rango_fechas(df_audit, df_files, df_trans, df_feedback=None):
    """Calcula el rango global de fechas a partir de los dataframes.
    Si solo hay un día, se amplía +1 día para que los sliders sean válidos.
    """
    all_dates = []
    if not df_audit.empty and "timestamp" in df_audit.columns:
        all_dates.extend(df_audit["timestamp"].dropna().tolist())
    if not df_files.empty and "timestamp" in df_files.columns:
        all_dates.extend(df_files["timestamp"].dropna().tolist())
    if not df_trans.empty and "timestamp" in df_trans.columns:
        all_dates.extend(df_trans["timestamp"].dropna().tolist())
    if df_feedback is not None and not df_feedback.empty and "timestamp" in df_feedback.columns:
        all_dates.extend(df_feedback["timestamp"].dropna().tolist())

    if all_dates:
        min_date = min(all_dates).date()
        max_date = max(all_dates).date()
        
        # Asegurar que el rango incluye "hoy" para permitir selección por defecto
        if max_date < date.today():
            max_date = date.today()
            
        if min_date == max_date:
            max_date = min_date + timedelta(days=1)
    else:
        min_date = date(2020, 1, 1)
        max_date = date.today()
    return min_date, max_date


def mostrar_panel_datos_brutos(df_audit_base, df_files, df_trans, df_feedback,
                               default_start_date, default_end_date):
    """Renderiza la pestaña "Datos en Bruto" con filtros independientes por sección."""
    st.subheader("Registro Completo de Decisiones")

    # -----------------------------------------------------------------
    # 1️⃣ Filtros Globales (Fechas) – independientes por sección
    # -----------------------------------------------------------------
    st.markdown("##### Filtros Globales")
    
    min_date, max_date = _obtener_rango_fechas(df_audit_base, df_files, df_trans, df_feedback)
    
    start_date, end_date = render_date_selector(
        min_date, max_date,
        default_start_date, default_end_date,
        key_prefix="raw"
    )
    st.divider()

    # -----------------------------------------------------------------
    # 2️⃣ Estado de sesión (sets para selección/visualización)
    # -----------------------------------------------------------------
    for key in [
        "visualized_audit_ids",
        "visualized_file_indices",
        "selected_audit_ids",
        "selected_file_indices",
        "selected_trans_indices",
    ]:
        if key not in st.session_state:
            st.session_state[key] = set()

    # -----------------------------------------------------------------
    # 3️⃣ Pestañas con sus respectivos renderizados
    # -----------------------------------------------------------------
    tab_registros_padre, tab_log_ficheros, tab_log_trans, tab_log_prompts, tab_feedback = st.tabs([
        ":material/list_alt: Registros de Auditoría",
        ":material/folder_open: Log de Ficheros Importados",
        ":material/transcribe: Log de Transcripciones",
        ":material/history_edu: Log de Prompts",
        ":material/bug_report: Feedback & Errores",
    ])

    with tab_registros_padre:
        render_tab_audit(df_audit_base, df_files, start_date, end_date)

    with tab_log_ficheros:
        render_tab_files(df_files, start_date, end_date, key_prefix="raw_files")

    with tab_log_trans:
        render_tab_transcriptions(df_trans, start_date, end_date, key_prefix="raw_trans")

    with tab_log_prompts:
        render_prompt_log_final(key_prefix="raw_prompts")

    with tab_feedback:
        render_feedback_list(df_feedback, start_date, end_date)