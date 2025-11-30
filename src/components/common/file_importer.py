# path: src/components/common/file_importer.py
import streamlit as st
from utils.file_handler import save_file_to_temp, TempFileWrapper

def render_file_importer(key_prefix="files", on_files_ready=None, disabled=False):
    """
    Renderiza un componente reutilizable para subir archivos.
    
    Args:
        key_prefix (str): Prefijo para las claves de los widgets.
        on_files_ready (callable): Función a llamar cuando se confirman los archivos.
                                   Recibe una lista de objetos TempFileWrapper.
        disabled (bool): Si es True, deshabilita las interacciones.
    """
    st.markdown("##### 📁 Subir Archivos")
    
    if f"{key_prefix}_reset_counter" not in st.session_state:
        st.session_state[f"{key_prefix}_reset_counter"] = 0
        
    uploaded_files = st.file_uploader(
        "Seleccione archivos (Imágenes, Audio, Video, Docs)", 
        type=["png", "jpg", "jpeg", "wav", "mp3", "ogg", "mp4", "mov", "avi", "pdf", "txt", "md", "doc", "docx", "xls", "xlsx"],
        accept_multiple_files=True,
        key=f"{key_prefix}_upload_{st.session_state[f'{key_prefix}_reset_counter']}",
        disabled=disabled
    )
    
    def handle_add_files():
        if not uploaded_files: return

        processed_files = []
        errors = []
        
        for uf in uploaded_files:
            try:
                file_info = save_file_to_temp(uf)
                wrapper = TempFileWrapper(uf, uf.name, temp_path=file_info['path'], file_type=uf.type)
                processed_files.append(wrapper)
            except Exception as e:
                errors.append(f"{uf.name}: {str(e)}")
        
        if errors:
            st.error(f"Errores al procesar archivos: {'; '.join(errors)}")
        
        if processed_files and on_files_ready:
            on_files_ready(processed_files)
            
        st.session_state[f"{key_prefix}_reset_counter"] += 1
        st.rerun()

    st.divider()
    c_add, c_cancel = st.columns(2)
    
    with c_add:
        if st.button("✅ Añadir Archivos", key=f"{key_prefix}_add_btn", disabled=not uploaded_files or disabled, use_container_width=True):
            handle_add_files()
        
    with c_cancel:
        if st.button("❌ Cancelar", key=f"{key_prefix}_cancel", use_container_width=True, disabled=disabled):
            st.rerun()

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/common/file_importer.py</div>', unsafe_allow_html=True)
