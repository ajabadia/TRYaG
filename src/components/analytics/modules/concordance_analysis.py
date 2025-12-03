import streamlit as st
from datetime import date, timedelta
from ui.audit_panel.components import render_date_selector, render_action_bar
from components.analytics.concordance_analysis import render_concordance_analysis as render_concordance_content

def render_concordance_analysis_module(df_audit_base, key_prefix="mod_concordance"):
    """
    Módulo independiente de Validación Científica (Concordancia).
    """
    st.markdown("### 🧪 Validación Científica")
    
    # 1. Filtros
    default_end = date.today()
    default_start = default_end - timedelta(days=30)
    
    start_date, end_date = render_date_selector(
        date(2020, 1, 1), date.today(),
        default_start, default_end,
        key_prefix=key_prefix
    )
    
    # Filtrar
    df_filtered = df_audit_base.copy()
    if not df_filtered.empty and start_date and end_date:
        mask = (df_filtered['timestamp'].dt.date >= start_date) & (df_filtered['timestamp'].dt.date <= end_date)
        df_filtered = df_filtered.loc[mask]
        
    # 2. Acciones
    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_filtered,
        on_refresh=lambda: st.rerun(),
        excel_filename=f"concordance_{date.today()}.xlsx"
    )
    
    st.divider()
    
    if df_filtered.empty:
        st.info("No hay datos suficientes.")
    else:
        render_concordance_content(df_filtered, key_prefix=f"{key_prefix}_content")
