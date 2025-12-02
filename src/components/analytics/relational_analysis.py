# path: src/components/analytics/relational_analysis.py
"""
Componente de análisis relacional entre archivos y transcripciones.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils.icon_utils import get_icon_html

def render_relational_analysis(df_files, df_trans, key_prefix="relational"):
    """
    Renderiza análisis combinados: archivos vs idiomas, evolución de idiomas.
    """
    st.markdown(f"### {get_icon_html('link', 24)}Análisis Relacional", unsafe_allow_html=True)
    
    if df_files.empty or df_trans.empty:
        st.info("Se necesitan datos de archivos y transcripciones para el análisis relacional.")
        return
    
    # JOIN por file_md5
    merged = pd.merge(df_files, df_trans, on='file_md5', how='inner')
    
    if merged.empty:
        st.warning("No hay coincidencias entre archivos y transcripciones (file_md5).")
        return
    
    # Análisis 1: Tipos de Archivo vs Idiomas
    st.markdown("##### Tipos de Archivo vs Idiomas")
    
    if 'file_type' in merged.columns and 'language_name' in merged.columns:
        chart_type = st.radio("Tipo de Visualización", ["Heatmap", "Barras Agrupadas", "Tabla"], 
                             key=f"{key_prefix}_chart_relational", horizontal=True)
        
        crosstab = pd.crosstab(merged['file_type'], merged['language_name'])
        
        if chart_type == "Heatmap":
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(crosstab, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_title('Relación entre Tipos de Archivo e Idiomas')
            ax.set_xlabel('Idioma')
            ax.set_ylabel('Tipo de Archivo')
            st.pyplot(fig)
            plt.close(fig)
        elif chart_type == "Barras Agrupadas":
            st.bar_chart(crosstab, use_container_width=True)
        else:  # Tabla
            st.dataframe(crosstab, use_container_width=True)
    else:
        st.info("Faltan columnas necesarias para el análisis.")
    
    st.divider()
    
    # Análisis 2: Evolución de Idiomas en el Tiempo
    st.markdown("##### Evolución de Idiomas en el Tiempo")
    
    if 'timestamp' in merged.columns and 'language_name' in merged.columns:
        chart_type_evol = st.radio("Tipo de Gráfico", ["Líneas", "Área Apilada", "Barras"], 
                                   key=f"{key_prefix}_chart_lang_evolution", horizontal=True)
        
        merged_copy = merged.copy()
        merged_copy['date'] = pd.to_datetime(merged_copy['timestamp']).dt.date
        evolution = merged_copy.groupby(['date', 'language_name']).size().reset_index(name='count')
        
        # Pivot para gráficos
        pivot = evolution.pivot(index='date', columns='language_name', values='count').fillna(0)
        
        if chart_type_evol == "Líneas":
            st.line_chart(pivot, use_container_width=True)
        elif chart_type_evol == "Área Apilada":
            st.area_chart(pivot, use_container_width=True)
        else:  # Barras
            st.bar_chart(pivot, use_container_width=True)
    else:
        st.info("Faltan datos temporales para mostrar la evolución.")

    st.markdown('<div class="debug-footer">src/components/analytics/relational_analysis.py</div>', unsafe_allow_html=True)
