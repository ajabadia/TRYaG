# path: src/components/audit/details.py
# Creado: 2025-11-21
# Última modificación: 2025-11-21
"""
Componente para la visualización de detalles de un registro de auditoría.
"""
import streamlit as st
import pandas as pd
import os
from utils.image_utils import get_or_create_thumbnail_base64
from components.common.media_viewer import open_media_viewer

def render_audit_details(selected_records, df_files):
    """
    Renderiza el panel de detalles para los registros seleccionados.
    """
    st.markdown("### Detalle del Registro")
    if len(selected_records) > 1:
        st.info("Seleccione un solo registro para ver el detalle completo.", icon=":material/info:")
    
    for _, row in selected_records.iterrows():
        with st.container(border=True):
            st.markdown(f"**ID:** `{row['audit_id']}`")
            st.markdown(f"**Fecha:** `{pd.to_datetime(row['timestamp']).strftime('%d/%m/%Y %H:%M')}`")
            st.markdown(f"**Motivo:** {row['motivo_consulta']}")
            st.markdown(f"**Edad:** {row['edad']} | **Dolor:** {row['dolor']}")
            st.divider()
            st.markdown(f"**🤖 IA:** {row['sugerencia_ia']}")
            st.markdown(f"**👤 Humano:** {row['nivel_corregido']}")
            if pd.notna(row['justificacion_humana']):
                st.markdown(f"**Justificación:** *{row['justificacion_humana']}*")
            
            # --- Ficheros Asociados ---
            if not df_files.empty:
                files_associated = df_files[df_files['audit_id'] == row['audit_id']]
                if not files_associated.empty:
                    st.divider()
                    st.markdown("**📎 Ficheros Adjuntos:**")
                    for _, file_row in files_associated.iterrows():
                        file_ext = str(file_row.get('file_type', '')).lower()
                        file_path = os.path.join('data', 'import_files', f"{file_row['file_md5']}.{file_ext}")
                        
                        col_img, col_btn = st.columns([1, 2])
                        with col_img:
                            if file_ext in ['png', 'jpg', 'jpeg'] and os.path.exists(file_path):
                                thumbnail = get_or_create_thumbnail_base64(file_path, file_row['file_md5'], size=(100, 100))
                                if thumbnail:
                                    st.markdown(f'<img src="{thumbnail}" style="border-radius:5px; width:100%">', unsafe_allow_html=True)
                            else:
                                st.markdown(f"📄 `{file_ext}`")
                        
                        with col_btn:
                            st.caption(file_row['file_name'])
                            if os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    st.download_button("Descargar", f.read(), file_row['file_name'], key=f"dl_{file_row['file_md5']}", icon=":material/download:")
                            
                            # --- Botón Visualizar ---
                            if os.path.exists(file_path):
                                # Crear lista con un solo archivo para mantener compatibilidad
                                single_file_list = [{
                                    'path': file_path,
                                    'name': file_row['file_name'],
                                    'ext': file_ext,
                                    'md5': file_row['file_md5']
                                }]
                                open_media_viewer(single_file_list, start_index=0, key=f"view_btn_{file_row['file_md5']}")

                                st.markdown('<div class="debug-footer">src/components/audit/details.py</div>', unsafe_allow_html=True)
