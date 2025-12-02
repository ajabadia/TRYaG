# path: src/components/analytics/transcription_analysis.py
"""
Componente de análisis de transcripciones.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.icon_utils import get_icon_html

def render_transcription_analysis(df_trans, key_prefix="transcription"):
    """
    Renderiza análisis de transcripciones: idiomas, fuentes, calidad.
    """
    st.markdown(f"### {get_icon_html('mic', 24)}Análisis de Transcripciones", unsafe_allow_html=True)
    
    if df_trans.empty:
        st.info("No hay datos de transcripciones disponibles.")
        return
    
    col1, col2 = st.columns(2)
    
    # Distribución de Idiomas
    with col1:
        st.markdown("##### Distribución de Idiomas")
        if 'language_name' in df_trans.columns:
            chart_type = st.radio("Tipo de Gráfico", ["Barras", "Pastel"], 
                                 key=f"{key_prefix}_chart_lang", horizontal=True)
            
            lang_counts = df_trans['language_name'].value_counts()
            
            if chart_type == "Pastel":
                fig, ax = plt.subplots()
                ax.pie(lang_counts, labels=lang_counts.index, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.bar_chart(lang_counts, use_container_width=True)
        else:
            st.info("No hay datos de idiomas.")
    
    # Fuente de Transcripciones
    with col2:
        st.markdown("##### Fuente de Transcripciones")
        if 'source' in df_trans.columns:
            source_counts = df_trans['source'].value_counts()
            st.bar_chart(source_counts, use_container_width=True)
        else:
            st.info("No hay datos de fuente disponibles.")
    
    st.divider()
    
    # Calidad de Transcripciones
    st.markdown("##### Calidad de Transcripciones")
    if 'spanish_user_text' in df_trans.columns:
        total = len(df_trans)
        edited = df_trans['spanish_user_text'].notna().sum()
        edit_rate = (edited / total * 100) if total > 0 else 0
        
        col_metric, col_chart = st.columns([1, 2])
        
        with col_metric:
            st.metric("Tasa de Edición", f"{edit_rate:.1f}%",
                     help="Porcentaje de transcripciones que fueron editadas manualmente")
            st.metric("Total Editadas", f"{edited}/{total}")
            
            # Interpretación
            if edit_rate < 20:
                st.success("✅ Excelente calidad de IA")
            elif edit_rate < 50:
                st.info("ℹ️ Calidad aceptable")
            else:
                st.warning("⚠️ Muchas correcciones manuales")
        
        with col_chart:
            st.markdown("**Distribución de Estados**")
            edit_data = pd.DataFrame({
                'Estado': ['Editadas', 'Sin Editar'],
                'Cantidad': [edited, total - edited]
            })
            st.bar_chart(edit_data.set_index('Estado'), use_container_width=True)
    else:
        st.info("No hay datos de edición disponibles.")

    st.markdown('<div class="debug-footer">src/components/analytics/transcription_analysis.py</div>', unsafe_allow_html=True)
