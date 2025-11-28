# path: src/components/audit/transcription_log.py
"""
Componente para la visualización del log de transcripciones.
"""
import streamlit as st
import pandas as pd
import os
import io
from utils.pdf_utils import PDF

TRANSCRIPTIONS_LOG = os.path.join('data', 'transcriptions.csv')

def generate_pdf_transcription_log(df, start_date, end_date):
    """Genera un PDF con el log de transcripciones."""
    pdf = PDF(orientation='L')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Filtros Aplicados', ln=1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f" - Desde: {start_date.strftime('%d/%m/%Y')}", ln=1)
    pdf.cell(0, 8, f" - Hasta: {end_date.strftime('%d/%m/%Y')}", ln=1)
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Log de Transcripciones', ln=1)
    
    df_pdf = df.copy()
    cols_to_show = ['file_md5', 'source', 'language_name', 'sended_text']
    
    # Filter columns if they exist
    existing_cols = [col for col in cols_to_show if col in df_pdf.columns]
    df_pdf = df_pdf[existing_cols]

    pdf.set_font("Arial", size=8)
    with pdf.table(col_widths=(50, 30, 30, 160), text_align="LEFT", line_height=5, borders_layout="ALL") as table:
        pdf.set_font("Arial", "B", 8)
        header = table.row()
        for col in df_pdf.columns:
            header.cell(col)
        
        pdf.set_font("Arial", "", 8)
        for _, data_row in df_pdf.iterrows():
            row = table.row()
            for datum in data_row:
                text_val = str(datum)
                if len(text_val) > 100:
                    text_val = text_val[:97] + "..."
                row.cell(text_val)

    return bytes(pdf.output())

def render_transcription_details(selected_records):
    """Renderiza el detalle de las transcripciones seleccionadas."""
    st.markdown("### Detalle de la Transcripción")
    
    for _, row in selected_records.iterrows():
        with st.container(border=True):
            col_info, col_text = st.columns([1, 2])
            
            with col_info:
                st.markdown(f"**Fichero:** `{row['file_md5']}`")
                st.markdown(f"**Fuente:** {row['source']}")
                st.markdown(f"**Idioma:** {row['language_name']}")
                if 'timestamp' in row:
                    st.markdown(f"**Fecha:** {row['timestamp']}")
            
            with col_text:
                st.markdown("**Texto Transcrito:**")
                st.text_area("Contenido", value=row['sended_text'], height=200, disabled=True, label_visibility="collapsed")


def render_transcription_log(df_trans_view, start_date, end_date, key_prefix="trans_log"):
    """
    Renderiza la pestaña de log de transcripciones.
    df_trans_view ya viene filtrado desde raw_data_panel.
    """
    # Botonera
    from ui.audit_panel.components import render_action_bar
    
    render_action_bar(
        key_prefix=key_prefix,
        df=df_trans_view,
        on_refresh=lambda: st.rerun(),
        pdf_generator=lambda: generate_pdf_transcription_log(df_trans_view, start_date, end_date),
        excel_filename="transcripciones_log.xlsx",
        share_params={
            "tab": "datos"
        }
    )

    if df_trans_view.empty:
        st.info("No hay transcripciones registradas.")
        return

    # --- Estado de Selección ---
    if f'{key_prefix}_selected_trans_indices' not in st.session_state:
        st.session_state[f'{key_prefix}_selected_trans_indices'] = []

    # --- Layout Dividido: Tabla (Izquierda) | Detalles (Derecha) ---
    has_selection = len(st.session_state[f'{key_prefix}_selected_trans_indices']) > 0
    
    if has_selection:
        col_table, col_details = st.columns([4, 6])
    else:
        col_table = st.container()
        col_details = None
        
    with col_table:
        event = st.dataframe(
            df_trans_view,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"{key_prefix}_table"
        )
        
        # Actualizar estado para el próximo rerun
        current_selection = event.selection.rows
        if current_selection != st.session_state[f'{key_prefix}_selected_trans_indices']:
            st.session_state[f'{key_prefix}_selected_trans_indices'] = current_selection
            st.rerun()

    if has_selection and col_details:
        with col_details:
            selected_indices = st.session_state[f'{key_prefix}_selected_trans_indices']
            if selected_indices:
                try:
                    selected_records = df_trans_view.iloc[selected_indices]
                    with st.container(height=800, border=False):
                        render_transcription_details(selected_records)
                except IndexError:
                    st.session_state[f'{key_prefix}_selected_trans_indices'] = []
                    st.rerun()
