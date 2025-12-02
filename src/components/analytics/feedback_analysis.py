import streamlit as st
import pandas as pd
import plotly.express as px

def render_feedback_analysis(df_feedback, key_prefix="feedback_analysis"):
    """
    Renderiza el análisis gráfico de los reportes de feedback.
    """
    st.markdown("### 📨 Análisis de Feedback y Errores")
    
    if df_feedback is None or df_feedback.empty:
        st.info("No hay datos de feedback para analizar en el periodo seleccionado.")
        return

    # Asegurar tipos
    if 'timestamp' in df_feedback.columns:
        df_feedback['timestamp'] = pd.to_datetime(df_feedback['timestamp'])
    
    # --- Filtros Locales ---
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if 'type' in df_feedback.columns:
            types = df_feedback['type'].unique().tolist()
            selected_types = st.multiselect("Filtrar por Tipo", types, default=types, key=f"{key_prefix}_filter_type")
            if selected_types:
                df_feedback = df_feedback[df_feedback['type'].isin(selected_types)]
    
    with col_f2:
        if 'status' in df_feedback.columns:
            statuses = df_feedback['status'].unique().tolist()
            selected_statuses = st.multiselect("Filtrar por Estado", statuses, default=statuses, key=f"{key_prefix}_filter_status")
            if selected_statuses:
                df_feedback = df_feedback[df_feedback['status'].isin(selected_statuses)]
    
    if df_feedback.empty:
        st.warning("No hay datos de feedback para los filtros seleccionados.")
        return
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reportes", len(df_feedback))
    with col2:
        errores = len(df_feedback[df_feedback['type'] == 'error'])
        st.metric("Errores", errores)
    with col3:
        mejoras = len(df_feedback[df_feedback['type'] == 'mejora'])
        st.metric("Mejoras", mejoras)
    with col4:
        pendientes = len(df_feedback[df_feedback['status'] == 'pendiente'])
        st.metric("Pendientes", pendientes)
        
    st.divider()
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### Distribución por Tipo")
        if 'type' in df_feedback.columns:
            fig_type = px.pie(
                df_feedback, 
                names='type', 
                title='Tipos de Reporte',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_type, use_container_width=True, key=f"{key_prefix}_pie_type")
            
    with col_chart2:
        st.markdown("#### Estado de los Reportes")
        if 'status' in df_feedback.columns:
            status_counts = df_feedback['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            fig_status = px.bar(
                status_counts, 
                x='status', 
                y='count', 
                title='Estado Actual',
                color='status',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_status, use_container_width=True, key=f"{key_prefix}_bar_status")
            
    st.divider()
    
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.markdown("#### Reportes por Módulo")
        if 'module' in df_feedback.columns:
            module_counts = df_feedback['module'].value_counts().reset_index()
            module_counts.columns = ['module', 'count']
            fig_module = px.bar(
                module_counts,
                y='module',
                x='count',
                orientation='h',
                title='Módulos más reportados'
            )
            st.plotly_chart(fig_module, use_container_width=True, key=f"{key_prefix}_bar_module")

    with col_chart4:
        st.markdown("#### Evolución Temporal")
        if 'timestamp' in df_feedback.columns:
            df_evol = df_feedback.set_index('timestamp').resample('D').size().reset_index(name='count')
            fig_evol = px.line(
                df_evol,
                x='timestamp',
                y='count',
                title='Reportes por Día',
                markers=True
            )
            st.plotly_chart(fig_evol, use_container_width=True, key=f"{key_prefix}_line_evol")

    st.markdown('<div class="debug-footer">src/components/analytics/feedback_analysis.py</div>', unsafe_allow_html=True)
