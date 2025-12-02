"""
Orquestador principal del panel de análisis gráfico unificado.
Ensambla componentes modulares de análisis.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import io
from utils.pdf_utils import PDF
from components.analytics import (
    render_kpis,
    render_evolution,
    render_triage_analysis,
    render_file_analysis,
    render_transcription_analysis,
    render_relational_analysis,
)
from components.analytics.concordance_analysis import render_concordance_analysis
from .components import render_date_selector, render_action_bar

def generate_pdf_analisis(df_analisis, filters_text):
    """Genera un PDF con los gráficos de análisis (simplificado)."""
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Informe de Análisis', ln=1)
    pdf.set_font('Arial', '', 10)
    for f_text in filters_text:
        pdf.multi_cell(0, 8, f_text, ln=1)
    pdf.ln(5)
    pdf.cell(0, 10, 'Ver dashboard interactivo para gráficos detallados.', ln=1)
    return bytes(pdf.output())

def mostrar_panel_analisis(
    df_audit_base,
    default_start_date,
    default_end_date,
    default_decisions, # Kept for compatibility but unused globally now
    df_files=None,
    df_trans=None,
    df_feedback=None,
    key_prefix="analisis",
):
    """Panel de Análisis Gráfico.
    Gestiona filtros globales y ensambla los componentes de visualización.
    """
    st.subheader("📊 Análisis Gráfico")

    # Copiar dataframes
    df_analisis = df_audit_base.copy()
    df_files_filtered = df_files.copy() if df_files is not None else pd.DataFrame()
    df_trans_filtered = df_trans.copy() if df_trans is not None else pd.DataFrame()
    df_feedback_filtered = df_feedback.copy() if df_feedback is not None else pd.DataFrame()

    # ---------------------------------------------------------------------
    # 1️⃣ Filtros Globales (Fechas)
    # ---------------------------------------------------------------------
    st.markdown("##### Filtros Globales")
    
    # Determinar rango global
    if not df_analisis.empty:
        min_date = df_analisis['timestamp'].min().date()
        max_date = df_analisis['timestamp'].max().date()
        if min_date == max_date:
            max_date = min_date + timedelta(days=1)
    else:
        min_date = date(2020, 1, 1)
        max_date = date.today()

    start_date, end_date = render_date_selector(
        min_date, max_date,
        default_start_date, default_end_date,
        key_prefix=key_prefix
    )

    # Aplicar filtro de fechas a los dataframes
    if start_date and end_date:
        mask = (df_analisis['timestamp'].dt.date >= start_date) & (df_analisis['timestamp'].dt.date <= end_date)
        df_analisis = df_analisis.loc[mask]
        if not df_files_filtered.empty and 'timestamp' in df_files_filtered.columns:
            mask_files = (df_files_filtered['timestamp'].dt.date >= start_date) & (df_files_filtered['timestamp'].dt.date <= end_date)
            df_files_filtered = df_files_filtered.loc[mask_files]
        if not df_trans_filtered.empty and 'timestamp' in df_trans_filtered.columns:
            mask_trans = (df_trans_filtered['timestamp'].dt.date >= start_date) & (df_trans_filtered['timestamp'].dt.date <= end_date)
            df_trans_filtered = df_trans_filtered.loc[mask_trans]
        if not df_feedback_filtered.empty and 'timestamp' in df_feedback_filtered.columns:
            mask_fb = (df_feedback_filtered['timestamp'].dt.date >= start_date) & (df_feedback_filtered['timestamp'].dt.date <= end_date)
            df_feedback_filtered = df_feedback_filtered.loc[mask_fb]

    # ---------------------------------------------------------------------
    # 2️⃣ Barra de Acciones
    # ---------------------------------------------------------------------
    
    # Preparar generador de PDF
    def pdf_generator():
        filters_text = [
            f" - Desde: {start_date.strftime('%d/%m/%Y')}",
            f" - Hasta: {end_date.strftime('%d/%m/%Y')}",
        ]
        return generate_pdf_analisis(df_analisis, filters_text)

    # Preparar parámetros de compartir
    share_params = {
        "tab": "analisis",
        "analisis_start": start_date.isoformat(),
        "analisis_end": end_date.isoformat()
    }

    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_analisis, # Para CSV/Excel
        on_refresh=lambda: st.rerun(),
        pdf_generator=pdf_generator,
        excel_filename=f"analisis_{start_date.strftime('%Y%m%d')}.xlsx",
        share_params=share_params
    )

    st.divider()

    if df_analisis.empty:
        st.info("No hay datos que coincidan con los filtros seleccionados.")
        return

    # ---------------------------------------------------------------------
    # 3️⃣ Pestañas principales de visualización
    # ---------------------------------------------------------------------
    tab_resumen, tab_evol, tab_triaje, tab_concordancia, tab_files, tab_trans, tab_relacional, tab_prompts, tab_feedback = st.tabs([
        "🎯 Resumen General",
        "📈 Evolución Temporal",
        "🏥 Análisis de Triaje",
        "🧪 Validación Científica",
        "📂 Análisis de Archivos",
        "🎙️ Análisis de Transcripciones",
        "🔗 Análisis Relacional",
        "📜 Análisis de Prompts",
        "🐛 Análisis de Feedback",
    ])

    with tab_resumen:
        render_kpis(df_analisis, df_files_filtered, df_trans_filtered)
    with tab_evol:
        render_evolution(df_analisis, df_files_filtered, key_prefix=f"{key_prefix}_evol")
    with tab_triaje:
        render_triage_analysis(df_analisis, key_prefix=f"{key_prefix}_triage")
    with tab_concordancia:
        render_concordance_analysis(df_analisis, key_prefix=f"{key_prefix}_concordance")
    with tab_files:
        render_file_analysis(df_files_filtered, key_prefix=f"{key_prefix}_file")
    with tab_trans:
        render_transcription_analysis(df_trans_filtered, key_prefix=f"{key_prefix}_trans")
    with tab_relacional:
        render_relational_analysis(df_files_filtered, df_trans_filtered, key_prefix=f"{key_prefix}_rel")
    with tab_prompts:
        from components.analytics.prompt_analysis import render_prompt_analysis
        render_prompt_analysis(key_prefix=f"{key_prefix}_prompts")
    with tab_feedback:
        from components.analytics.feedback_analysis import render_feedback_analysis
        render_feedback_analysis(df_feedback_filtered, key_prefix=f"{key_prefix}_feedback")

    st.markdown('<div class="debug-footer">src/ui/audit_panel/analysis_panel.py</div>', unsafe_allow_html=True)