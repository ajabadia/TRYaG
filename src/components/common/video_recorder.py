import streamlit as st
import base64
import time
from datetime import datetime
from utils.file_handler import save_file_to_temp, TempFileWrapper


def render_video_recorder(key_prefix="video", on_video_ready=None, disabled=False):
    """
    Renderiza el componente de grabación de video.
    
    Args:
        key_prefix (str): Prefijo para claves de estado.
        on_video_ready (callable): Callback al confirmar video.
        disabled (bool): Deshabilitar controles.
    """
    st.markdown("##### 🎥 Grabar Video")
    
    if disabled:
        st.info("Grabación bloqueada.")
        return

    # Inicializar contador de reset si no existe
    if f"{key_prefix}_reset_counter" not in st.session_state:
        st.session_state[f"{key_prefix}_reset_counter"] = 0

    # --- IMPLEMENTACIÓN ROBUSTA (File Uploader) ---
    # La grabación nativa vía componente custom es inestable para videos largos (Base64 overhead).
    # Usamos file_uploader con capture="environment" (móviles) o subida directa.
    
    uploaded_video = st.file_uploader(
        "Subir video o Grabar (Móvil)", 
        type=['mp4', 'mov', 'avi', 'webm'], 
        accept_multiple_files=False,
        key=f"{key_prefix}_uploader_{st.session_state[f'{key_prefix}_reset_counter']}"
    )
    
    if uploaded_video:
        try:
            # Guardar temporalmente
            file_info = save_file_to_temp(uploaded_video.getvalue(), default_ext=f".{uploaded_video.name.split('.')[-1]}")
            
            wrapper = TempFileWrapper(
                uploaded_video, 
                uploaded_video.name, 
                temp_path=file_info['path'], 
                file_type=uploaded_video.type
            )
            
            # Añadir a lista temporal
            if f"{key_prefix}_videos" not in st.session_state:
                st.session_state[f"{key_prefix}_videos"] = []
            
            # Evitar duplicados simples
            current_list = st.session_state[f"{key_prefix}_videos"]
            is_duplicate = any(v.name == wrapper.name and v.size == wrapper.size for v in current_list)
            
            if not is_duplicate:
                 st.session_state[f"{key_prefix}_videos"].append(wrapper)
                 # Incrementar contador para limpiar uploader
                 st.session_state[f"{key_prefix}_reset_counter"] += 1
                 st.rerun()
                 
        except Exception as e:
            st.error(f"Error procesando video: {e}")

    # --- STAGING AREA ---
    videos = st.session_state.get(f"{key_prefix}_videos", [])
    
    if videos:
        st.divider()
        st.markdown(f"**Videos grabados ({len(videos)}):**")
        
        for i, vid in enumerate(videos):
            c_vid, c_del = st.columns([4, 1])
            with c_vid:
                st.video(vid.temp_path)
            with c_del:
                if st.button("🗑️", key=f"{key_prefix}_del_{i}"):
                    st.session_state[f"{key_prefix}_videos"].pop(i)
                    st.rerun()
    
    st.divider()
    c_save, c_cancel = st.columns(2)
    
    with c_save:
        if st.button("✅ Guardar Videos", key=f"{key_prefix}_save", type="primary", use_container_width=True, disabled=not videos or disabled):
            if on_video_ready:
                on_video_ready(st.session_state[f"{key_prefix}_videos"])
            # Limpiar
            if f"{key_prefix}_videos" in st.session_state:
                del st.session_state[f"{key_prefix}_videos"]
            st.rerun()
        
    with c_cancel:
        if st.button("❌ Cancelar", key=f"{key_prefix}_cancel", use_container_width=True):
            if f"{key_prefix}_videos" in st.session_state:
                del st.session_state[f"{key_prefix}_videos"]
            st.rerun()

    st.markdown('<div class="debug-footer">src/components/common/video_recorder.py</div>', unsafe_allow_html=True)
