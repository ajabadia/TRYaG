# path: src/components/analytics/evolution.py
"""
Componente de evolución temporal para triajes y archivos.
"""
import streamlit as st
import pandas as pd
from utils.icon_utils import get_icon_html

def render_evolution(df_audit, df_files, key_prefix="evolution"):
    """
    Renderiza gráficos de evolución temporal combinados.
    Muestra la evolución de triajes y archivos en el tiempo.
    """
    st.markdown(f"### {get_icon_html('trending_up', 24)}Evolución Temporal", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Evolución de Triajes
    with col1:
        st.markdown("##### Triajes por Día")
        if not df_audit.empty and 'timestamp' in df_audit.columns:
            chart_type = st.radio("Tipo de Gráfico", ["Líneas", "Área", "Barras"], 
                                 key=f"{key_prefix}_chart_evol_triajes", horizontal=True)
            
            triajes_por_dia = df_audit.groupby(df_audit['timestamp'].dt.date).size()
            
            if chart_type == "Líneas":
                st.line_chart(triajes_por_dia, use_container_width=True)
            elif chart_type == "Área":
                st.area_chart(triajes_por_dia, use_container_width=True)
            else:
                st.bar_chart(triajes_por_dia, use_container_width=True)
        else:
            st.info("No hay datos de triajes disponibles.")
    
    # Evolución de Archivos
    with col2:
        st.markdown("##### Archivos por Día")
        if not df_files.empty and 'timestamp' in df_files.columns:
            chart_type_files = st.radio("Tipo de Gráfico", ["Líneas", "Área", "Barras"], 
                                        key=f"{key_prefix}_chart_evol_files", horizontal=True)
            
            df_files_copy = df_files.copy()
            df_files_copy['date'] = pd.to_datetime(df_files_copy['timestamp']).dt.date
            files_por_dia = df_files_copy.groupby('date').size()
            
            if chart_type_files == "Líneas":
                st.line_chart(files_por_dia, use_container_width=True)
            elif chart_type_files == "Área":
                st.area_chart(files_por_dia, use_container_width=True)
            else:
                st.bar_chart(files_por_dia, use_container_width=True)
        else:
            st.info("No hay datos de archivos disponibles.")

    st.markdown('<div class="debug-footer">src/components/analytics/evolution.py</div>', unsafe_allow_html=True)
