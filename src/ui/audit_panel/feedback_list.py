# path: src/ui/audit_panel/feedback_list.py
import streamlit as st
import pandas as pd
import os
from .components import render_action_bar, render_filters

def render_feedback_list(df_feedback, start_date=None, end_date=None):
    """
    Renderiza la lista de reportes de feedback.
    
    Args:
        df_feedback (pd.DataFrame): DataFrame con los reportes.
        start_date (date, optional): Fecha de inicio para filtrar.
        end_date (date, optional): Fecha de fin para filtrar.
    """
    st.subheader("📨 Reportes de Feedback y Errores")
    
    if df_feedback is None or df_feedback.empty:
        st.info("No hay reportes registrados.")
        return

    # Trabajar con copia para no afectar el original
    df = df_feedback.copy()
    
    # Asegurar timestamp datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Filtrar por fecha si se proporcionan
    if start_date and end_date and 'timestamp' in df.columns:
        # Eliminar NaT antes de comparar
        df = df.dropna(subset=['timestamp'])
        mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
        df = df.loc[mask]
    
    if df.empty:
        st.info("No hay reportes en el rango de fechas seleccionado.")
        return

    # Filtros Avanzados
    cols_to_filter = ['type', 'module', 'status', 'user_id']
    df = render_filters(df, cols_to_filter, key_prefix="feedback")

    # Botonera de Acciones
    render_action_bar(
        key_prefix="feedback",
        df=df,
        on_refresh=lambda: st.rerun(),
        excel_filename="feedback_report.xlsx",
        share_params={"tab": "feedback"} # Simplificado
    )

    # Seleccionar columnas relevantes para la tabla
    cols_to_show = ['timestamp', 'type', 'module', 'title', 'user_id', 'status']
    cols_to_show = [c for c in cols_to_show if c in df.columns]
    
    st.dataframe(
        df[cols_to_show].sort_values('timestamp', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    st.markdown("### 🔍 Detalles")
    
    # Mostrar detalles de los registros filtrados
    # Convertir de nuevo a lista de dicts para iterar fácil
    filtered_reports = df.sort_values('timestamp', ascending=False).to_dict('records')
    
    for report in filtered_reports:
        ts_str = report.get('timestamp').strftime('%Y-%m-%d %H:%M') if pd.notnull(report.get('timestamp')) else "N/A"
        with st.expander(f"{ts_str} | {report.get('type')} - {report.get('title')}"):
            st.markdown(f"**Usuario:** {report.get('user_id')}")
            st.markdown(f"**Módulo:** {report.get('module')}")
            st.markdown(f"**Estado:** {report.get('status')}")
            st.markdown(f"**Descripción:**")
            st.info(report.get('description'))
            st.caption(f"ID: {report.get('_id')}")
            
            attachments = report.get('attachments', [])
            # Manejar si attachments es string (a veces pasa en CSV/Excel imports mal formados)
            if isinstance(attachments, list) and attachments:
                st.markdown("#### 📂 Adjuntos")
                for att in attachments:
                    if isinstance(att, dict):
                        col_att, col_dl = st.columns([4, 1])
                        with col_att:
                            st.text(f"📄 {att.get('name')} ({att.get('size', 0)} bytes)")
                            st.caption(f"MD5: {att.get('md5')}")
                        with col_dl:
                            file_path = att.get('path')
                            if file_path and os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label="⬇️",
                                        data=f,
                                        file_name=att.get('name'),
                                        mime="application/octet-stream",
                                        key=f"dl_{report.get('_id')}_{att.get('md5')}"
                                    )
                            else:
                                st.warning("Archivo no encontrado")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/audit_panel/feedback_list.py</div>', unsafe_allow_html=True)
