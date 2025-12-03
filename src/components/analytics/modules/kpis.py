import streamlit as st
from datetime import date, timedelta
from ui.audit_panel.components import render_date_selector, render_action_bar
from components.analytics import render_kpis as render_kpis_content # Reusar lógica de visualización existente

def render_kpis_module(df_audit_base, df_files, df_trans, key_prefix="mod_kpis"):
    """
    Módulo independiente de KPIs.
    """
    st.markdown("### 🎯 Resumen General (KPIs)")
    
    # 1. Filtros Locales
    default_end = date.today()
    default_start = default_end - timedelta(days=30)
    
    start_date, end_date = render_date_selector(
        date(2020, 1, 1), date.today(),
        default_start, default_end,
        key_prefix=key_prefix
    )
    
    # Filtrar datos
    df_filtered = df_audit_base.copy()
    if not df_filtered.empty and start_date and end_date:
        mask = (df_filtered['timestamp'].dt.date >= start_date) & (df_filtered['timestamp'].dt.date <= end_date)
        df_filtered = df_filtered.loc[mask]
        
    # Filtrar auxiliares (si aplica)
    # ... (lógica similar para df_files, df_trans si se usan en KPIs)
    
    # 2. Barra de Acciones
    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_filtered,
        on_refresh=lambda: st.rerun(),
        excel_filename=f"kpis_{date.today()}.xlsx"
    )
    
    st.divider()
    
    # 3. Contenido
    if df_filtered.empty:
        st.info("No hay datos en el rango seleccionado.")
    else:
        # Llamar al renderizador de contenido existente (reutilización)
        # Nota: render_kpis espera dataframes ya filtrados
        render_kpis_content(df_filtered, df_files, df_trans)
