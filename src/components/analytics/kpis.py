# path: src/components/analytics/kpis.py
"""
Componente de KPIs unificados para el dashboard de análisis.
"""
import streamlit as st
import pandas as pd
from utils.icon_utils import get_icon_html

def render_kpis(df_audit, df_files, df_trans):
    """
    Renderiza tarjetas de métricas clave unificadas.
    Combina KPIs de triaje, archivos y transcripciones.
    """
    st.markdown(f"### {get_icon_html('target', 24)}Métricas Clave del Período", unsafe_allow_html=True)
    
    # Fila 1: Métricas de Triaje
    st.markdown("##### Triaje")
    col1, col2, col3, col4 = st.columns(4)
    
    total_casos = len(df_audit) if not df_audit.empty else 0
    with col1:
        st.metric("Total de Triajes", f"{total_casos:,}")
    
    if not df_audit.empty:
        aciertos = (df_audit['sugerencia_ia'] == df_audit['nivel_corregido']).sum()
        tasa_acierto = (aciertos / total_casos * 100) if total_casos > 0 else 0
        with col2:
            st.metric("Tasa de Acierto IA", f"{tasa_acierto:.1f}%", 
                     delta=f"{tasa_acierto-100:.1f}%" if tasa_acierto < 100 else None)
        
        modificaciones = (df_audit['decision_humana'] == 'Modificar Nivel').sum()
        tasa_modificacion = (modificaciones / total_casos * 100) if total_casos > 0 else 0
        with col3:
            st.metric("Tasa de Modificación", f"{tasa_modificacion:.1f}%",
                     help="Porcentaje de casos donde el humano decidió modificar el nivel sugerido.")
        
        calificaciones_positivas = (df_audit['calificacion_humana'] == 'Correcto').sum()
        tasa_calificacion_positiva = (calificaciones_positivas / total_casos * 100) if total_casos > 0 else 0
        with col4:
            st.metric("Calificación Positiva", f"{tasa_calificacion_positiva:.1f}%")
    
    st.divider()
    
    # Fila 2: Métricas de Archivos y Transcripciones
    st.markdown("##### Archivos y Transcripciones")
    col5, col6, col7, col8 = st.columns(4)
    
    total_files = len(df_files) if not df_files.empty else 0
    with col5:
        st.metric("Total de Archivos", f"{total_files:,}")
    
    # Archivos por auditoría
    if not df_files.empty and 'audit_id' in df_files.columns:
        avg_files_per_audit = df_files.groupby('audit_id').size().mean()
    else:
        avg_files_per_audit = 0
    with col6:
        st.metric("Archivos/Auditoría", f"{avg_files_per_audit:.1f}")
    
    # Tasa de transcripción
    if not df_files.empty and not df_trans.empty:
        audio_files = df_files[df_files['file_type'].isin(['wav', 'mp3', 'ogg'])] if 'file_type' in df_files.columns else pd.DataFrame()
        transcription_rate = (len(df_trans) / len(audio_files) * 100) if len(audio_files) > 0 else 0
    else:
        transcription_rate = 0
    with col7:
        st.metric("Tasa de Transcripción", f"{transcription_rate:.1f}%")
    
    # Idioma más común
    if not df_trans.empty and 'language_name' in df_trans.columns:
        most_common_lang = df_trans['language_name'].mode()[0] if len(df_trans['language_name'].mode()) > 0 else "N/A"
    else:
        most_common_lang = "N/A"
    with col8:
        st.metric("Idioma Principal", most_common_lang)

    st.markdown('<div class="debug-footer">src/components/analytics/kpis.py</div>', unsafe_allow_html=True)
