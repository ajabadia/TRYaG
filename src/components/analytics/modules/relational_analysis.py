import streamlit as st
from datetime import date, timedelta
from ui.audit_panel.components import render_date_selector, render_action_bar
from components.analytics import render_relational_analysis as render_rel_content

def render_relational_analysis_module(df_files, df_trans, key_prefix="mod_rel"):
    """
    Módulo independiente de Análisis Relacional.
    """
    st.markdown("### 🔗 Análisis Relacional")
    
    # 1. Filtros
    default_end = date.today()
    default_start = default_end - timedelta(days=30)
    
    start_date, end_date = render_date_selector(
        date(2020, 1, 1), date.today(),
        default_start, default_end,
        key_prefix=key_prefix
    )
    
    # Filtrar ambos dataframes
    df_files_f = df_files.copy()
    if not df_files_f.empty and start_date and end_date:
        mask = (df_files_f['timestamp'].dt.date >= start_date) & (df_files_f['timestamp'].dt.date <= end_date)
        df_files_f = df_files_f.loc[mask]
        
    df_trans_f = df_trans.copy()
    if not df_trans_f.empty and start_date and end_date:
        mask = (df_trans_f['timestamp'].dt.date >= start_date) & (df_trans_f['timestamp'].dt.date <= end_date)
        df_trans_f = df_trans_f.loc[mask]
        
    # 2. Acciones (Exportar qué? Quizás un resumen combinado, por ahora deshabilitado o solo uno)
    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=None, # Difícil exportar relacional directo a CSV simple
        on_refresh=lambda: st.rerun()
    )
    
    st.divider()
    
    render_rel_content(df_files_f, df_trans_f, key_prefix=f"{key_prefix}_content")
