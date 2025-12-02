# path: src/components/analytics/file_analysis.py
"""
Componente de análisis de archivos.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.icon_utils import get_icon_html

def render_file_analysis(df_files, key_prefix="file_analysis"):
    """
    Renderiza análisis de archivos: tipo, origen, por auditoría.
    """
    st.markdown(f"### {get_icon_html('file', 24)}Análisis de Archivos", unsafe_allow_html=True)
    
    if df_files.empty:
        st.info("No hay datos de archivos disponibles.")
        return
    
    col1, col2 = st.columns(2)
    
    # Distribución por Tipo
    with col1:
        st.markdown("##### Distribución por Tipo")
        if 'file_type' in df_files.columns:
            chart_type = st.radio("Tipo de Gráfico", ["Barras", "Pastel"], 
                                 key=f"{key_prefix}_chart_file_type", horizontal=True)
            
            type_counts = df_files['file_type'].value_counts()
            
            if chart_type == "Pastel":
                fig, ax = plt.subplots()
                ax.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.bar_chart(type_counts, use_container_width=True)
        else:
            st.info("No hay datos de tipo de archivo.")
    
    # Distribución por Origen
    with col2:
        st.markdown("##### Distribución por Origen")
        if 'source_type' in df_files.columns:
            source_counts = df_files['source_type'].value_counts()
            st.bar_chart(source_counts, use_container_width=True)
        else:
            st.info("No hay datos de origen disponibles.")
    
    st.divider()
    
    # Archivos por Auditoría
    st.markdown("##### Archivos por Auditoría")
    if 'audit_id' in df_files.columns:
        files_per_audit = df_files.groupby('audit_id').size().reset_index()
        files_per_audit.columns = ['audit_id', 'num_files']
        
        # Histograma de distribución
        fig, ax = plt.subplots()
        ax.hist(files_per_audit['num_files'], bins=20, edgecolor='black')
        ax.set_xlabel('Número de Archivos')
        ax.set_ylabel('Frecuencia (Auditorías)')
        ax.set_title('Distribución de Archivos por Auditoría')
        st.pyplot(fig)
        plt.close(fig)
        
        # Estadísticas
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Promedio", f"{files_per_audit['num_files'].mean():.1f}")
        with col_stats2:
            st.metric("Mediana", f"{files_per_audit['num_files'].median():.0f}")
        with col_stats3:
            st.metric("Máximo", f"{files_per_audit['num_files'].max()}")
    else:
        st.info("No hay datos de audit_id disponibles.")

    st.markdown('<div class="debug-footer">src/components/analytics/file_analysis.py</div>', unsafe_allow_html=True)
