# path: src/ui/audit_panel/tab_audit.py
# Creado: 2025-11-23
"""
Módulo para la pestaña "Registros de Auditoría".
"""
import streamlit as st
import pandas as pd
import os
import io
from utils.pdf_utils import PDF
from components.audit.filters import render_audit_specific_filters, apply_audit_filters
from components.audit.table import render_audit_table
from components.audit.details import render_audit_details

# Constantes
AUDIT_LOG_FILE = os.path.join('data', 'audit_log.csv')
PAGE_SIZE = 25

def generate_pdf_datos_brutos(df, start_date, end_date):
    """Genera un PDF con los datos en bruto filtrados."""
    pdf = PDF(orientation='L')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Filtros Aplicados', ln=1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f" - Desde: {start_date.strftime('%d/%m/%Y')}", ln=1)
    pdf.cell(0, 8, f" - Hasta: {end_date.strftime('%d/%m/%Y')}", ln=1)
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Registros de Auditoría', ln=1)
    
    df_pdf = df[['timestamp', 'sugerencia_ia', 'nivel_corregido', 'decision_humana']].copy()
    df_pdf['timestamp'] = df_pdf['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    
    pdf.set_font("Arial", size=8)
    with pdf.table(col_widths=(60, 70, 70, 60), text_align="CENTER", line_height=5, borders_layout="ALL") as table:
        pdf.set_font("Arial", "B", 8)
        header = table.row()
        for col in df_pdf.columns:
            header.cell(col)
        
        pdf.set_font("Arial", "", 8)
        for _, data_row in df_pdf.iterrows():
            row = table.row()
            for datum in data_row:
                row.cell(str(datum))
    
    return bytes(pdf.output())

def render_tab_audit(df_audit_base, df_files, start_date, end_date):
    """Renderiza el contenido de la pestaña de auditoría."""
    st.markdown("Aquí se muestran todas las decisiones de triaje.")
    
    # Filtros Específicos
    search_text, age_range, pain_range, show_discrepancies_only = render_audit_specific_filters(df_audit_base)
    
    # Aplicar filtros
    df_datos = apply_audit_filters(df_audit_base, start_date, end_date, search_text, age_range, pain_range, show_discrepancies_only)
    
    # --- Botonera ---
    from ui.audit_panel.components import render_action_bar
    
    def on_refresh_audit():
        st.session_state.num_audit_records_to_show = PAGE_SIZE
        st.rerun()

    render_action_bar(
        key_prefix="audit_log",
        df=df_datos,
        on_refresh=on_refresh_audit,
        pdf_generator=lambda: generate_pdf_datos_brutos(df_datos, start_date, end_date),
        excel_filename="auditoria.xlsx",
        share_params={
            "tab": "datos",
            "datos_start": start_date.isoformat(),
            "datos_end": end_date.isoformat()
        }
    )

    
    # --- Layout Dividido: Tabla (Izquierda) | Detalles (Derecha) ---
    has_selection = len(st.session_state.selected_audit_ids) > 0
    
    if has_selection:
        col_table, col_details = st.columns([4, 6])
    else:
        col_table = st.container()
        col_details = None
    
    with col_table:
        render_audit_table(df_datos, has_selection)
    
    if has_selection and col_details:
        with col_details:
            selected_records = df_datos[df_datos['audit_id'].isin(st.session_state.selected_audit_ids)]
            with st.container(height=800, border=False):
                render_audit_details(selected_records, df_files)
