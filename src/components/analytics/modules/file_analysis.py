import streamlit as st
from datetime import date, timedelta
from ui.audit_panel.components import render_date_selector, render_action_bar
from components.analytics import render_file_analysis as render_file_content

def render_file_analysis_module(df_files, key_prefix="mod_files"):
    """
    Módulo independiente de Análisis de Archivos.
    """
    st.markdown("### 📂 Análisis de Archivos")
    
    # 1. Filtros
    default_end = date.today()
    default_start = default_end - timedelta(days=30)
    
    start_date, end_date = render_date_selector(
        date(2020, 1, 1), date.today(),
        default_start, default_end,
        key_prefix=key_prefix
    )
    
    # Filtrar
    df_filtered = df_files.copy()
    if not df_filtered.empty and start_date and end_date:
        mask = (df_filtered['timestamp'].dt.date >= start_date) & (df_filtered['timestamp'].dt.date <= end_date)
        df_filtered = df_filtered.loc[mask]
        
    # 2. Acciones
    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_filtered,
        on_refresh=lambda: st.rerun(),
        excel_filename=f"files_{date.today()}.xlsx"
    )
    
    st.divider()
    
    if df_filtered.empty:
        st.info("No hay datos.")
    else:
        render_file_content(df_filtered, key_prefix=f"{key_prefix}_content")
        
        st.divider()
        st.markdown("#### 📋 Detalle de Archivos")
        
        selection = st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"{key_prefix}_table"
        )
        
        if selection and selection.selection and selection.selection["rows"]:
            idx = selection.selection["rows"][0]
            try:
                row = df_filtered.iloc[idx]
                st.info(f"📝 **Detalle: {row.get('filename', 'N/A')}**")
                st.json(row.to_dict(), expanded=False)
            except:
                pass
