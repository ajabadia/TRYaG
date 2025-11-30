import streamlit as st
import base64
import time
from datetime import datetime
from utils.file_handler import save_file_to_temp, TempFileWrapper
from components.custom_video_recorder import video_recorder

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

    # Clave dinámica para reiniciar el componente
    if f"{key_prefix}_reset_counter" not in st.session_state:
        st.session_state[f"{key_prefix}_reset_counter"] = 0
        
    recorder_key = f"{key_prefix}_rec_{st.session_state[f'{key_prefix}_reset_counter']}"
    
    # Renderizar componente custom
    video_data_base64 = video_recorder(key=recorder_key)
    
    # Procesar datos recibidos
    if video_data_base64:
        try:
            # Decodificar base64
            # El formato suele ser "data:video/webm;base64,GkXfo..."
            if "," in video_data_base64:
                header, encoded = video_data_base64.split(",", 1)
            else:
                encoded = video_data_base64
                
            video_bytes = base64.b64decode(encoded)
            
            # Guardar temporalmente
            file_info = save_file_to_temp(video_bytes, default_ext=".webm")
            
            wrapper = TempFileWrapper(
                video_bytes, 
                f"video_{datetime.now().strftime('%H%M%S')}.webm", 
                temp_path=file_info['path'], 
                file_type="video/webm"
            )
            
            # Añadir a lista temporal
            if f"{key_prefix}_videos" not in st.session_state:
                st.session_state[f"{key_prefix}_videos"] = []
            
            # Evitar duplicados (el componente puede enviar el mismo valor en reruns)
            # Usamos el tamaño como proxy simple o verificamos si ya existe el último
            current_list = st.session_state[f"{key_prefix}_videos"]
            if not current_list or current_list[-1].size != len(video_bytes):
                 st.session_state[f"{key_prefix}_videos"].append(wrapper)
                 # Forzar reinicio del componente para limpiar
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

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/components/common/video_recorder.py</div>', unsafe_allow_html=True)
