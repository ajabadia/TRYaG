import streamlit as st
import pandas as pd
from .components import render_action_bar, render_filters, calculate_date_range, render_date_selector
from services.feedback_service import get_feedback_reports

def render_feedback_list_v2(df_feedback):
    """
    Renderiza la lista de reportes de feedback (Versión Modular).
    """
    st.markdown("### 📨 Reportes de Feedback y Errores")
    
    if df_feedback is None or df_feedback.empty:
        st.info("No hay reportes registrados.")
        return

    # 1. Selector de Fechas Propio
    min_date, max_date = calculate_date_range([df_feedback])
    start_date, end_date = render_date_selector(
        min_date, max_date, 
        min_date, max_date, 
        "feedback_v2"
    )
    
    # 2. Filtros Locales
    df = df_feedback.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        df = df[
            (df["timestamp"].dt.date >= start_date) & 
            (df["timestamp"].dt.date <= end_date)
        ]
        
    # 3. Filtros Dinámicos
    df = render_filters(df, ["type", "status", "module"], "feedback_v2_dynamic")
    
    # 4. Barra de Acciones
    def refresh_data():
        st.cache_data.clear()
        st.rerun()

    render_action_bar(
        "feedback_v2_actions",
        df=df,
        on_refresh=refresh_data,
        excel_filename="feedback.xlsx"
    )
    
    # 5. Tabla Resumen
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # 6. Detalles (Expanders)
    # Convertir a lista de dicts para iterar
    reports = df.to_dict('records')
    for report in reports:
        timestamp_str = report.get('timestamp').strftime('%Y-%m-%d %H:%M') if pd.notnull(report.get('timestamp')) else "N/A"
        with st.expander(f"{timestamp_str} | {report.get('type')} - {report.get('title')}"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Módulo:** {report.get('module')}")
                st.markdown(f"**Descripción:** {report.get('body')}")
                if report.get('subtype'):
                    st.markdown(f"**Subtipo:** {report.get('subtype')}")
            with c2:
                st.info(f"Estado: {report.get('status')}")
                st.caption(f"ID: {report.get('_id')}")
                
            # Adjuntos
            if report.get('attachments'):
                st.markdown("---")
                st.markdown("**Adjuntos:**")
                for att in report.get('attachments'):
                    st.markdown(f"- 📎 {att.get('name')} ({att.get('size')} bytes)")
                    
    st.caption(f"Mostrando {len(df)} registros")
    st.markdown('<div class="debug-footer">src/ui/audit_panel/feedback_list_v2.py</div>', unsafe_allow_html=True)
