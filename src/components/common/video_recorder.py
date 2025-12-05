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

    # --- OPCIÓN 1: GRABADOR NATIVO (JS) ---
    from components.common.webcam_video import render_js_recorder
    import os
    
    with st.expander("📹 Abrir Grabador de Cámara", expanded=False):
        st.caption("Graba tu video y espera a que aparezca el mensaje de confirmación.")
        
        # Generamos el nombre esperado
        expected_filename = render_js_recorder()
        
        # Botón para "recoger" el video subido
        if st.button("🔄 Procesar Video Grabado", key=f"{key_prefix}_check_upload"):
            with st.spinner("Procesando video..."):
                temp_path = os.path.join("temp", expected_filename)
                
                if os.path.exists(temp_path):
                    # Crear wrapper simulando upload
                    try:
                        # Leer contenido a BytesIO para compatibilidad con TempFileWrapper
                        from io import BytesIO
                        with open(temp_path, "rb") as f:
                            content = f.read()
                        
                        file_obj = BytesIO(content)
                        file_obj.name = expected_filename
                        
                        wrapper = TempFileWrapper(
                            file_obj, 
                            expected_filename, 
                            temp_path=temp_path, 
                            file_type="video/webm"
                        )
                        
                        # Añadir a lista
                        if f"{key_prefix}_videos" not in st.session_state:
                            st.session_state[f"{key_prefix}_videos"] = []
                            
                        st.session_state[f"{key_prefix}_videos"].append(wrapper)
                        st.success("Video importado correctamente.")
                        
                        # Limpiar el nombre de archivo persistido para permitir nueva grabación
                        if "recorder_filename" in st.session_state:
                            del st.session_state["recorder_filename"]
                            
                        # NO hacemos rerun aquí para evitar parpadeos/cierres del modal.
                        # Al seguir la ejecución, la lista de abajo se actualizará sola.
                        
                    except Exception as e:
                        st.error(f"Error importando video: {e}")
                else:
                    st.warning("No se encontró el video. Asegúrate de haber terminado de grabar y que salga el mensaje de confirmación.")

    # --- OPCIÓN 2: SUBIDA DE ARCHIVO (Solo si no se usa el grabador o como backup) ---
    st.markdown("##### O subir video manualmente")
    
    uploaded_video = st.file_uploader(
        "Arrastra aquí el video o selecciona uno", 
        type=['mp4', 'mov', 'avi', 'webm'], 
        accept_multiple_files=False,
        key=f"{key_prefix}_uploader_{st.session_state[f'{key_prefix}_reset_counter']}"
    )
    
    if uploaded_video:
        try:
            # Guardar temporalmente
            file_info = save_file_to_temp(uploaded_video, default_ext=f".{uploaded_video.name.split('.')[-1]}")
            
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
                 # st.rerun() # REMOVIDO: Evitar cierre prematuro
                 
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
                    # Cerrar archivo si está abierto
                    if hasattr(vid, '_file_obj') and not vid._file_obj.closed:
                         try:
                             vid._file_obj.close()
                         except: pass
                    
                    st.session_state[f"{key_prefix}_videos"].pop(i)
                    st.rerun()
    
    st.divider()
    c_save, c_cancel = st.columns(2)
    
    with c_save:
        if st.button("✅ Guardar Videos", key=f"{key_prefix}_save", type="primary", use_container_width=True, disabled=not videos or disabled):
            with st.spinner("Guardando y vinculando videos..."):
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
