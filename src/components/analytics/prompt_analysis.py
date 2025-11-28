# path: src/components/analytics/prompt_analysis.py
# Creado: 2025-11-23
# Actualizado: 2025-11-23 - Fix para MongoDB
# path: src/components/analytics/prompt_analysis.py
# Creado: 2025-11-23
# Actualizado: 2025-11-23 - Fix para MongoDB
"""
Componente de análisis gráfico para los Prompts.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from src.core.prompt_manager import PromptManager
from utils.icon_utils import get_icon_html

def load_prompts_data():
    """Carga y procesa los datos de los prompts para análisis."""
    pm = PromptManager()
    
    # Obtener todos los prompts usando el repositorio
    try:
        all_prompts = pm.repo.get_all_prompts() if pm.repo else []
    except:
        all_prompts = []
    
    data = []
    for prompt_doc in all_prompts:
        prompt_type = prompt_doc.get("prompt_type", "unknown")
        active_ver = prompt_doc.get("active_version")
        versions = prompt_doc.get("versions", [])
        
        for version in versions:
            ver_id = version.get("version_id", "N/A")
            created_at = version.get("created_at")
            
            # Convertir datetime a string si es necesario
            if hasattr(created_at, 'isoformat'):
                created_at = created_at.isoformat()
            
            row = {
                "prompt_type": prompt_type,
                "version_id": ver_id,
                "status": version.get("status", "unknown"),
                "author": version.get("author", "unknown"),
                "created_at": created_at,
                "is_active": (ver_id == active_ver)
            }
            data.append(row)
            
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    # Parse dates with mixed format support
    df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', errors='coerce')
    return df

def render_prompt_analysis(key_prefix="prompt_analysis"):
    """Renderiza el panel de análisis de prompts."""
    st.markdown(f"### {get_icon_html('smart_toy', 24)}Análisis de Prompts", unsafe_allow_html=True)
    
    df = load_prompts_data()
    
    if df.empty:
        st.info("No hay datos de prompts para analizar.")
        return

    # --- KPIs Principales ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_versions = len(df)
    active_versions = len(df[df['is_active'] == True])
    unique_types = df['prompt_type'].nunique()
    top_author = df['author'].mode()[0] if not df.empty else "N/A"
    
    col1.metric("Total Versiones", total_versions)
    col2.metric("Versiones Activas", active_versions)
    col3.metric("Tipos de Prompt", unique_types)
    col4.metric("Autor Más Activo", top_author)
    
    st.divider()
    
    # --- Gráficos ---
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("##### Distribución por Tipo")
        fig_pie = px.pie(df, names='prompt_type', title='Versiones por Tipo de Prompt', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True, key=f"{key_prefix}_pie_type")
        
    with col_g2:
        st.markdown("##### Estado de Versiones")
        fig_bar = px.bar(df, x='prompt_type', color='status', title='Estado de Versiones por Tipo', barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True, key=f"{key_prefix}_bar_status")
        
    st.divider()
    
    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        st.markdown("##### Evolución Temporal (Creación)")
        # Agrupar por fecha (día)
        df_time = df.copy()
        df_time['date'] = df_time['created_at'].dt.date
        df_evol = df_time.groupby(['date', 'prompt_type']).size().reset_index(name='count')
        
        fig_line = px.line(df_evol, x='date', y='count', color='prompt_type', markers=True, title='Nuevas Versiones en el Tiempo')
        st.plotly_chart(fig_line, use_container_width=True, key=f"{key_prefix}_line_evol")

    with col_g4:
        st.markdown("##### Actividad por Autor")
        df_author = df.groupby('author').size().reset_index(name='count')
        fig_author = px.bar(df_author, x='author', y='count', title='Versiones creadas por Autor', color='count')
        st.plotly_chart(fig_author, use_container_width=True, key=f"{key_prefix}_bar_author")
