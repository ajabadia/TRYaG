import streamlit as st
import pandas as pd
from .components import render_action_bar, render_filters, calculate_date_range, render_date_selector

def render_tab_transcriptions_v2(df_trans):
    """
    Renderiza la pestaña de Log de Transcripciones (Versión Modular).
    """
    st.markdown("### 🎙️ Log de Transcripciones")
    
    if df_trans.empty:
        st.info("No hay registros de transcripciones.")
        return

    # 1. Selector de Fechas Propio
    min_date, max_date = calculate_date_range([df_trans])
    start_date, end_date = render_date_selector(
        min_date, max_date, 
        min_date, max_date, 
        "trans_v2"
    )
    
    # 2. Filtros Locales
    df_filtered = df_trans.copy()
    if "timestamp" in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered["timestamp"].dt.date >= start_date) & 
            (df_filtered["timestamp"].dt.date <= end_date)
        ]
        
    # 3. Filtros Dinámicos
    df_filtered = render_filters(df_filtered, ["language", "source"], "trans_v2_dynamic")
    
    # 4. Barra de Acciones
    def refresh_data():
        st.cache_data.clear()
        st.rerun()

    render_action_bar(
        "trans_v2_actions",
        df=df_filtered,
        on_refresh=refresh_data,
        excel_filename="transcripciones.xlsx"
    )
    
    # 5. Tabla
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Mostrando {len(df_filtered)} registros")
    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/audit_panel/tab_transcriptions_v2.py</div>', unsafe_allow_html=True)
