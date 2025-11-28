import streamlit as st
import pandas as pd
from .components import render_action_bar, render_filters, calculate_date_range, render_date_selector
from utils.pdf_utils import generate_audit_pdf

def render_audit_specific_filters(df):
    """Renderiza filtros específicos para Auditoría."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_text = st.text_input("Buscar en detalles", placeholder="Escribe para buscar...", key="audit_v2_search")
    
    with col2:
        age_range = (0, 100)
        if "detalles.edad" in df.columns:
             min_age = int(df["detalles.edad"].min())
             max_age = int(df["detalles.edad"].max())
             age_range = st.slider("Edad", min_age, max_age, (min_age, max_age), key="audit_v2_age")
             
    with col3:
        pain_range = (0, 10)
        if "detalles.dolor" in df.columns:
            pain_range = st.slider("Nivel de Dolor", 0, 10, (0, 10), key="audit_v2_pain")
            
    show_discrepancies_only = st.checkbox("Mostrar solo discrepancias (IA vs Humano)", key="audit_v2_discrepancy")
    
    return search_text, age_range, pain_range, show_discrepancies_only

def apply_audit_filters(df, start_date, end_date, search_text, age_range, pain_range, show_discrepancies_only):
    """Aplica los filtros al DataFrame de auditoría."""
    df_filtered = df.copy()
    
    # Filtro fecha
    if "timestamp" in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered["timestamp"].dt.date >= start_date) & 
            (df_filtered["timestamp"].dt.date <= end_date)
        ]
        
    # Filtro texto
    if search_text:
        # Buscar en varias columnas relevantes
        mask = df_filtered.astype(str).apply(lambda x: x.str.contains(search_text, case=False, na=False)).any(axis=1)
        df_filtered = df_filtered[mask]
        
    # Filtro edad
    if "detalles.edad" in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered["detalles.edad"] >= age_range[0]) & 
            (df_filtered["detalles.edad"] <= age_range[1])
        ]
        
    # Filtro dolor
    if "detalles.dolor" in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered["detalles.dolor"] >= pain_range[0]) & 
            (df_filtered["detalles.dolor"] <= pain_range[1])
        ]
        
    # Filtro discrepancias
    if show_discrepancies_only:
        # Asumiendo que existe una columna de discrepancia o comparando decisión IA vs Humana
        # Esto depende de tu lógica específica de discrepancia. 
        # Si no tienes columna directa, habría que implementarla.
        # Por ahora, placeholder si no existe la columna.
        if "discrepancia" in df_filtered.columns:
             df_filtered = df_filtered[df_filtered["discrepancia"] == True]
        elif "decision_ia" in df_filtered.columns and "decision_humana" in df_filtered.columns:
             df_filtered = df_filtered[df_filtered["decision_ia"] != df_filtered["decision_humana"]]

    return df_filtered

def render_tab_audit_v2(df_audit_base, df_files):
    """
    Renderiza la pestaña de Registros de Auditoría (Versión Modular).
    """
    st.markdown("### 📋 Registros de Auditoría")
    
    if df_audit_base.empty:
        st.info("No hay registros de auditoría disponibles.")
        return

    # 1. Selector de Fechas Propio
    min_date, max_date = calculate_date_range([df_audit_base])
    start_date, end_date = render_date_selector(
        min_date, max_date, 
        min_date, max_date, # Default to full range or today? Let's default to full range for now or today as requested before.
        "audit_v2"
    )
    
    # 2. Filtros Específicos
    search_text, age_range, pain_range, show_discrepancies_only = render_audit_specific_filters(df_audit_base)
    
    # 3. Aplicar Filtros
    df_filtered = apply_audit_filters(df_audit_base, start_date, end_date, search_text, age_range, pain_range, show_discrepancies_only)
    
    # 4. Filtros Dinámicos (Columnas extra)
    df_filtered = render_filters(df_filtered, ["decision_humana", "usuario"], "audit_v2_dynamic")
    
    # 5. Barra de Acciones
    def refresh_data():
        st.cache_data.clear()
        st.rerun()
        
    def generate_pdf():
        return generate_audit_pdf(df_filtered)

    render_action_bar(
        "audit_v2_actions",
        df=df_filtered,
        on_refresh=refresh_data,
        pdf_generator=generate_pdf,
        excel_filename="auditoria.xlsx"
    )
    
    # 6. Tabla de Datos
    st.dataframe(
        df_filtered,
        use_container_width=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Fecha/Hora", format="DD/MM/YYYY HH:mm"),
            "decision_humana": "Decisión",
            "usuario": "Usuario",
            "detalles": "Detalles"
        },
        hide_index=True
    )
    
    st.caption(f"Mostrando {len(df_filtered)} registros")
    
    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/audit_panel/tab_audit_v2.py</div>', unsafe_allow_html=True)
