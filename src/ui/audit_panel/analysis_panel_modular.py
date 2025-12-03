import streamlit as st
import pandas as pd
from components.analytics.modules.kpis import render_kpis_module
from components.analytics.modules.evolution import render_evolution_module
from components.analytics.modules.triage_analysis import render_triage_analysis_module
from components.analytics.modules.file_analysis import render_file_analysis_module
from components.analytics.modules.transcription_analysis import render_transcription_analysis_module
from components.analytics.modules.relational_analysis import render_relational_analysis_module
from components.analytics.modules.prompt_analysis import render_prompt_analysis_module
from components.analytics.modules.feedback_analysis import render_feedback_analysis_module
from components.analytics.modules.concordance_analysis import render_concordance_analysis_module

def mostrar_panel_analisis_modular(
    df_audit_base,
    df_files=None,
    df_trans=None,
    df_feedback=None,
    key_prefix="analisis_mod",
):
    """
    Panel de Análisis Gráfico Modular.
    Orquesta los submódulos independientes.
    """
    st.subheader("📊 Análisis Gráfico (Modular)")

    # Dataframes base (copias para seguridad)
    df_analisis = df_audit_base.copy()
    df_files_base = df_files.copy() if df_files is not None else pd.DataFrame()
    df_trans_base = df_trans.copy() if df_trans is not None else pd.DataFrame()
    df_feedback_base = df_feedback.copy() if df_feedback is not None else pd.DataFrame()

    # Pestañas
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
        render_kpis_module(df_analisis, df_files_base, df_trans_base, key_prefix=f"{key_prefix}_kpis")
        
    with tab_evol:
        render_evolution_module(df_analisis, df_files_base, key_prefix=f"{key_prefix}_evol")
        
    with tab_triaje:
        render_triage_analysis_module(df_analisis, key_prefix=f"{key_prefix}_triage")
        
    with tab_concordancia:
        render_concordance_analysis_module(df_analisis, key_prefix=f"{key_prefix}_concordance")
        
    with tab_files:
        render_file_analysis_module(df_files_base, key_prefix=f"{key_prefix}_files")
        
    with tab_trans:
        render_transcription_analysis_module(df_trans_base, key_prefix=f"{key_prefix}_trans")
        
    with tab_relacional:
        render_relational_analysis_module(df_files_base, df_trans_base, key_prefix=f"{key_prefix}_rel")
        
    with tab_prompts:
        render_prompt_analysis_module(key_prefix=f"{key_prefix}_prompts")
        
    with tab_feedback:
        render_feedback_analysis_module(df_feedback_base, key_prefix=f"{key_prefix}_feedback")

    st.markdown('<div class="debug-footer">src/ui/audit_panel/analysis_panel_modular.py</div>', unsafe_allow_html=True)
