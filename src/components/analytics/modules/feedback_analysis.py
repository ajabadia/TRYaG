import streamlit as st
from datetime import date, timedelta
from ui.audit_panel.components import render_date_selector, render_action_bar
from components.analytics import render_feedback_analysis as render_feedback_content

def render_feedback_analysis_module(df_feedback, key_prefix="mod_feedback"):
    """
    Módulo independiente de Análisis de Feedback.
    """
    st.markdown("### 🐛 Análisis de Feedback")
    
    # 1. Filtros
    default_end = date.today()
    default_start = default_end - timedelta(days=30)
    
    start_date, end_date = render_date_selector(
        date(2020, 1, 1), date.today(),
        default_start, default_end,
        key_prefix=key_prefix
    )
    
    # Filtrar
    df_filtered = df_feedback.copy()
    if not df_filtered.empty and start_date and end_date:
        mask = (df_filtered['timestamp'].dt.date >= start_date) & (df_filtered['timestamp'].dt.date <= end_date)
        df_filtered = df_filtered.loc[mask]
        
    # 2. Acciones
    render_action_bar(
        key_prefix=f"{key_prefix}_actions",
        df=df_filtered,
        on_refresh=lambda: st.rerun(),
        excel_filename=f"feedback_{date.today()}.xlsx"
    )
    
    st.divider()
    
    if df_filtered.empty:
        st.info("No hay feedback registrado.")
    else:
        render_feedback_content(df_filtered, key_prefix=f"{key_prefix}_content")
        
        st.divider()
        st.markdown("#### 📋 Detalle de Feedback")
        
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
                st.info(f"📝 **Detalle Feedback**")
                st.json(row.to_dict(), expanded=False)
            except:
                pass
