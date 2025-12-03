import streamlit as st
from datetime import date, timedelta
from ui.audit_panel.components import render_date_selector, render_action_bar
from components.analytics import render_evolution as render_evolution_content

def render_evolution_module(df_audit_base, df_files, key_prefix="mod_evol"):
    """
    Módulo independiente de Evolución Temporal.
    """
    st.markdown("### 📈 Evolución Temporal")
    
    # 1. Filtros Locales
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
        
    # 2. Barra de Acciones
    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_filtered,
        on_refresh=lambda: st.rerun(),
        excel_filename=f"evolution_{date.today()}.xlsx"
    )
    
    st.divider()
    
    if df_filtered.empty:
        st.info("No hay datos.")
    else:
        render_evolution_content(df_filtered, df_files, key_prefix=f"{key_prefix}_content")
