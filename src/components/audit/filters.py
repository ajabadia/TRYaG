# path: src/components/audit/filters.py
# Creado: 2025-11-21
# Última modificación: 2025-11-21
"""
Componente para la visualización y gestión de filtros en el panel de auditoría.
"""
import streamlit as st
import pandas as pd

def render_audit_specific_filters(df_audit_base):
    """
    Renderiza los filtros específicos para la pestaña de Auditoría.
    """
    st.markdown("##### Filtros de Auditoría")
    
    # Fila 1: Búsqueda
    search_text = st.text_input("Buscar en Motivo o Justificación", placeholder="Escribe para buscar...", key="search_text_audit")

    # Fila 2: Filtros específicos (Edad, Dolor, Discrepancias)
    with st.expander("Más filtros (Edad, Dolor, Discrepancias)", expanded=False):
        c_filter_1, c_filter_2, c_filter_3 = st.columns(3)
        with c_filter_1:
            # Calcular rango de edad con validación
            min_age_data = int(df_audit_base['edad'].min())
            max_age_data = int(df_audit_base['edad'].max())
            
            # Si min == max, expandir el rango para que el slider funcione
            if min_age_data == max_age_data:
                min_age = max(0, min_age_data - 5)  # Expandir -5 años (mínimo 0)
                max_age = min(120, max_age_data + 5)  # Expandir +5 años (máximo 120)
                default_range = (min_age_data, max_age_data)  # Valor por defecto es el real
            else:
                min_age = min_age_data
                max_age = max_age_data
                default_range = (min_age, max_age)
            
            age_range = st.slider("Rango de Edad", min_age, max_age, default_range, key="age_range_filter")
        with c_filter_2:
            pain_range = st.slider("Rango de Dolor (EVA)", 0, 10, (0, 10), key="pain_range_filter")
        with c_filter_3:
            st.write("") # Espaciado
            st.write("")
            show_discrepancies_only = st.checkbox("⚠️ Solo Discrepancias (IA ≠ Humano)", key="discrepancies_filter")

    st.divider()
    return search_text, age_range, pain_range, show_discrepancies_only

def apply_audit_filters(df, start_date, end_date, search_text, age_range, pain_range, show_discrepancies_only):
    """Aplica filtros de auditoría."""
    df_filtered = df.copy()
    
    # Fechas (Globales)
    if start_date and end_date:
        mask_date = (df_filtered['timestamp'].dt.date >= start_date) & (df_filtered['timestamp'].dt.date <= end_date)
        df_filtered = df_filtered.loc[mask_date]
    
    # Texto
    if search_text:
        text_query = search_text.lower()
        mask_text = (
            df_filtered['motivo_consulta'].astype(str).str.lower().str.contains(text_query) |
            df_filtered['justificacion_humana'].astype(str).str.lower().str.contains(text_query)
        )
        df_filtered = df_filtered.loc[mask_text]

    # Rangos
    df_filtered = df_filtered[(df_filtered['edad'] >= age_range[0]) & (df_filtered['edad'] <= age_range[1])]
    df_filtered = df_filtered[(df_filtered['dolor'] >= pain_range[0]) & (df_filtered['dolor'] <= pain_range[1])]

    # Discrepancias
    if show_discrepancies_only:
        df_filtered = df_filtered[df_filtered['sugerencia_ia'] != df_filtered['nivel_corregido']]
        
    return df_filtered

def render_file_filters(df_files):
    """Renderiza filtros para log de ficheros."""
    st.markdown("##### Filtros de Ficheros")
    c1, c2 = st.columns(2)
    with c1:
        # Filtro por Tipo (extensión)
        if not df_files.empty:
            types = sorted([str(x) for x in df_files['file_type'].unique() if pd.notna(x)])
            types = ["Todos"] + types
        else:
            types = ["Todos"]
        selected_type = st.selectbox("Tipo de Archivo", types, key="file_type_filter")
    with c2:
        # Filtro por Fuente
        if not df_files.empty and 'source_type' in df_files.columns:
            sources = sorted([str(x) for x in df_files['source_type'].unique() if pd.notna(x)])
            sources = ["Todos"] + sources
        else:
            sources = ["Todos"]
        selected_source = st.selectbox("Origen", sources, key="file_source_filter")
    
    st.divider()
    return selected_type, selected_source

def apply_file_filters(df, start_date, end_date, selected_type, selected_source):
    """Aplica filtros de ficheros."""
    df_filtered = df.copy()
    
    # Fechas
    if start_date and end_date and 'timestamp' in df_filtered.columns:
        mask_date = (df_filtered['timestamp'].dt.date >= start_date) & (df_filtered['timestamp'].dt.date <= end_date)
        df_filtered = df_filtered.loc[mask_date]

    if selected_type != "Todos":
        df_filtered = df_filtered[df_filtered['file_type'] == selected_type]
        
    if selected_source != "Todos" and 'source_type' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['source_type'] == selected_source]
        
    return df_filtered

def render_transcription_filters(df_trans):
    """Renderiza filtros para log de transcripciones."""
    st.markdown("##### Filtros de Transcripciones")
    c1, c2 = st.columns(2)
    with c1:
        if not df_trans.empty and 'source' in df_trans.columns:
            sources = sorted([str(x) for x in df_trans['source'].unique() if pd.notna(x)])
            sources = ["Todos"] + sources
        else:
            sources = ["Todos"]
        selected_source = st.selectbox("Fuente Transcripción", sources, key="trans_source_filter")
    with c2:
        if not df_trans.empty and 'language_name' in df_trans.columns:
            langs = sorted([str(x) for x in df_trans['language_name'].unique() if pd.notna(x)])
            langs = ["Todos"] + langs
        else:
            langs = ["Todos"]
        selected_lang = st.selectbox("Idioma", langs, key="trans_lang_filter")
        
    st.divider()
    return selected_source, selected_lang

def apply_transcription_filters(df, start_date, end_date, selected_source, selected_lang):
    """Aplica filtros de transcripciones."""
    df_filtered = df.copy()
    
    # Fechas (si existe timestamp)
    if start_date and end_date and 'timestamp' in df_filtered.columns:
        # Asegurar datetime
        if not pd.api.types.is_datetime64_any_dtype(df_filtered['timestamp']):
             df_filtered['timestamp'] = pd.to_datetime(df_filtered['timestamp'], errors='coerce')
             
        mask_date = (df_filtered['timestamp'].dt.date >= start_date) & (df_filtered['timestamp'].dt.date <= end_date)
        df_filtered = df_filtered.loc[mask_date]

    if selected_source != "Todos" and 'source' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['source'] == selected_source]
        
    if selected_lang != "Todos" and 'language_name' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['language_name'] == selected_lang]
        
    return df_filtered
