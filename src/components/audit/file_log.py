# path: src/components/audit/file_log.py
# Creado: 2025-11-21
# Última modificación: 2025-11-22
"""
Componente para la visualización del log de ficheros importados.
"""
import streamlit as st
import pandas as pd
import os
import io
from utils.pdf_utils import PDF
from utils.image_utils import get_or_create_thumbnail_base64
from components.common.media_viewer import open_media_viewer

IMPORT_FILES_LOG = os.path.join('data', 'import_files_log.csv')

def file_preview_style():
    """Inyecta CSS para estilizar el cuadro de previsualización de ficheros."""
    # Cargar CSS externo
    from utils.ui_utils import load_css
    load_css("src/assets/css/components/tables.css")

def deselect_file_row(index_to_deselect):
    """Callback para cerrar una card de fichero y deseleccionar la fila."""
    st.session_state.visualized_file_indices.remove(index_to_deselect)

def generate_pdf_file_log(df, start_date, end_date):
    """Genera un PDF con el log de ficheros."""
    pdf = PDF(orientation='L')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Filtros Aplicados', ln=1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f" - Desde: {start_date.strftime('%d/%m/%Y')}", ln=1)
    pdf.cell(0, 8, f" - Hasta: {end_date.strftime('%d/%m/%Y')}", ln=1)
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Log de Ficheros Importados', ln=1)
    
    df_pdf = df.copy()
    if 'timestamp' in df_pdf.columns:
        df_pdf['timestamp'] = df_pdf['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Columns to show
    cols_to_show = ['timestamp', 'file_name', 'file_type']
    # Filter columns if they exist
    existing_cols = [col for col in cols_to_show if col in df_pdf.columns]
    df_pdf = df_pdf[existing_cols]

    pdf.set_font("Arial", size=8)
    # Adjust column widths based on expected content. Total width approx 270 for Landscape A4 margins
    # timestamp: 40, file_name: 180, file_type: 30 = 250
    with pdf.table(col_widths=(40, 180, 30), text_align="CENTER", line_height=5, borders_layout="ALL") as table:
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

def render_file_details(selected_records):
    """Renderiza el detalle de los ficheros seleccionados."""
    st.markdown("### Detalle del Fichero")
    file_preview_style()
    
    for _, row in selected_records.iterrows():
        with st.container(border=True):
            col_img, col_info = st.columns([1, 2])
            
            file_ext = str(row.get('file_type', '')).lower()
            file_path = os.path.join('data', 'import_files', f"{row['file_md5']}.{file_ext}")
            
            with col_img:
                if file_ext in ['png', 'jpg', 'jpeg', 'gif', 'webp'] and os.path.exists(file_path):
                    thumb = get_or_create_thumbnail_base64(file_path, row['file_md5'], size=(300, 300))
                    if thumb:
                        st.markdown(f'<div class="file-preview-frame"><img src="{thumb}"></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="file-preview-frame"><div class="file-type-text">{file_ext}</div></div>', unsafe_allow_html=True)
            
            with col_info:
                st.markdown(f"**Nombre:** {row['file_name']}")
                st.markdown(f"**Tipo:** {row['file_type']}")
                if 'timestamp' in row:
                    st.markdown(f"**Fecha:** {row['timestamp']}")
                
                # Botón para abrir visor
                # Preparamos la lista para el visor (solo este archivo por simplicidad en single selection, 
                # o podríamos pasar todos los filtrados si quisiéramos navegación)
                if os.path.exists(file_path):
                    media_item = [{
                        'path': file_path,
                        'name': row['file_name'],
                        'ext': file_ext,
                        'md5': row['file_md5']
                    }]
                    open_media_viewer(media_item, start_index=0, key=f"view_log_{row['file_md5']}")


def render_file_log(df_files_view, start_date, end_date, key_prefix="files_log"):
    """
    Renderiza la pestaña de log de ficheros.
    df_files_view ya viene filtrado desde raw_data_panel.
    """
    # Botonera para el log de ficheros
    from ui.audit_panel.components import render_action_bar
    
    render_action_bar(
        key_prefix=key_prefix,
        df=df_files_view,
        on_refresh=lambda: st.rerun(),
        pdf_generator=lambda: generate_pdf_file_log(df_files_view, start_date, end_date),
        excel_filename="ficheros_log.xlsx",
        share_params={
            "tab": "datos",
            "datos_start": start_date.isoformat(),
            "datos_end": end_date.isoformat()
        }
    )

    if df_files_view.empty:
        st.info("No hay ficheros registrados en este periodo.")
        return

    # --- Estado de Selección ---
    if f'{key_prefix}_selected_file_indices' not in st.session_state:
        st.session_state[f'{key_prefix}_selected_file_indices'] = []

    # --- Layout Dividido: Tabla (Izquierda) | Detalles (Derecha) ---
    has_selection = len(st.session_state[f'{key_prefix}_selected_file_indices']) > 0
    
    if has_selection:
        col_table, col_details = st.columns([4, 6])
    else:
        col_table = st.container()
        col_details = None
        
    with col_table:
        event = st.dataframe(
            df_files_view,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"{key_prefix}_table"
        )
        
        # Actualizar estado para el próximo rerun
        current_selection = event.selection.rows
        if current_selection != st.session_state[f'{key_prefix}_selected_file_indices']:
            st.session_state[f'{key_prefix}_selected_file_indices'] = current_selection
            st.rerun()

    if has_selection and col_details:
        with col_details:
            selected_indices = st.session_state[f'{key_prefix}_selected_file_indices']
            if selected_indices:
                try:
                    selected_records = df_files_view.iloc[selected_indices]
                    with st.container(height=800, border=False):
                        render_file_details(selected_records)
                except IndexError:
                    st.session_state[f'{key_prefix}_selected_file_indices'] = []
                    st.rerun()
