# path: src/components/audit/table.py
# Creado: 2025-11-21
# Última modificación: 2025-11-21
"""
Componente para la visualización de la tabla de registros en el panel de auditoría.
"""
import streamlit as st
import pandas as pd

PAGE_SIZE = 25

def render_audit_table(df_display, has_selection):
    """
    Renderiza la tabla de auditoría y gestiona la selección.
    """
    # Preparamos datos para la tabla
    df_display['seleccionar'] = df_display['audit_id'].apply(lambda id: id in st.session_state.selected_audit_ids)
    cols = ['seleccionar'] + [col for col in df_display.columns if col != 'seleccionar']
    
    total_records = len(df_display)
    if 'num_audit_records_to_show' not in st.session_state:
        st.session_state.num_audit_records_to_show = PAGE_SIZE
    
    records_to_show = min(st.session_state.num_audit_records_to_show, total_records)
    df_shown = df_display[cols].head(records_to_show)
    
    edited_df_audit = st.data_editor(
        df_shown, hide_index=True, use_container_width=True, 
        key="audit_log_editor", disabled=df_shown.columns.drop("seleccionar"),
        height=600 if has_selection else 400 # Ajustamos altura si hay selección
    )
    
    # Actualizamos selección
    new_selection = set(edited_df_audit[edited_df_audit['seleccionar']]['audit_id'])
    if new_selection != st.session_state.selected_audit_ids:
        st.session_state.selected_audit_ids = new_selection
        st.rerun()

    if records_to_show < total_records:
        st.button("Cargar más", on_click=lambda: st.session_state.update(num_audit_records_to_show=st.session_state.num_audit_records_to_show + PAGE_SIZE), use_container_width=True)
