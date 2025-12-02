# path: src/components/common/audio_recorder.py
import streamlit as st
from datetime import datetime
from utils.file_handler import save_file_to_temp, TempFileWrapper

def render_audio_recorder(key_prefix="audio", on_audio_ready=None, disabled=False):
    """
    Renderiza un componente reutilizable para grabar audio.
    
    Args:
        key_prefix (str): Prefijo para las claves de los widgets.
        on_audio_ready (callable): Función a llamar cuando se confirma el audio. 
                                   Recibe el objeto TempFileWrapper del audio.
        disabled (bool): Si es True, deshabilita los controles.
    """
    st.markdown("##### 🎤 Grabadora de Voz")
    
    # Inicializar lista de audios en staging
    if f"{key_prefix}_audios" not in st.session_state:
        st.session_state[f"{key_prefix}_audios"] = []

    # Clave dinámica para reiniciar el widget de audio
    if f"{key_prefix}_uploader_key" not in st.session_state:
        st.session_state[f"{key_prefix}_uploader_key"] = 0
        
    audio_key = f"{key_prefix}_recorder_{st.session_state[f'{key_prefix}_uploader_key']}"
    
    if disabled:
        st.info("Grabación bloqueada.")
    else:
        audio_value = st.audio_input("Grabar nota de voz", key=audio_key)
    
        # Estado local temporal para este componente (grabación actual)
        temp_audio_key = f"{key_prefix}_temp_val"
        
        if audio_value:
            # Guardar en estado temporal si no está ya o es nuevo
            if temp_audio_key not in st.session_state or st.session_state[temp_audio_key]['value'] != audio_value:
                 st.session_state[temp_audio_key] = {
                     'value': audio_value,
                     'timestamp': datetime.now()
                 }

    # Mostrar controles si hay audio temporal (grabación actual pendiente de añadir)
    temp_audio_key = f"{key_prefix}_temp_val"
    has_current_audio = temp_audio_key in st.session_state
    
    if has_current_audio:
        st.audio(st.session_state[temp_audio_key]['value'], format='audio/wav')
        
        # Botón para añadir a la lista (Staging)
        def handle_add_to_list():
            try:
                audio_val = st.session_state[temp_audio_key]['value']
                # Guardar en disco temporal
                file_info = save_file_to_temp(audio_val, default_ext=".wav")
                
                # Crear wrapper
                audio_wrapper = TempFileWrapper(audio_val, file_info['name'], temp_path=file_info['path'], file_type="audio/wav")
                
                # Añadir a la lista
                st.session_state[f"{key_prefix}_audios"].append(audio_wrapper)
                
                # Limpiar grabación actual y reiniciar widget
                del st.session_state[temp_audio_key]
                st.session_state[f"{key_prefix}_uploader_key"] += 1
                # No hacemos rerun aquí para que sea fluido, o sí? 
                # Si no hacemos rerun, el widget st.audio_input seguirá mostrando el audio antiguo hasta que se repinte.
                # Necesitamos rerun para que el key cambie y se limpie el input.
                # st.rerun() # Rerun necesario
                
            except Exception as e:
                st.error(f"Error al procesar audio: {e}")

        if st.button("⬇️ Añadir a la lista", key=f"{key_prefix}_add_btn", use_container_width=True, type="secondary", on_click=handle_add_to_list):
            pass

    # --- STAGING AREA (LISTA DE AUDIOS) ---
    audios_list = st.session_state[f"{key_prefix}_audios"]
    if audios_list:
        st.divider()
        st.markdown(f"**Grabaciones listas ({len(audios_list)}):**")
        
        for i, audio in enumerate(audios_list):
            with st.container(border=True):
                c_play, c_del = st.columns([4, 1])
                with c_play:
                    st.caption(f"Audio {i+1}")
                    # Reproducir desde path temporal si existe
                    if hasattr(audio, 'temp_path') and audio.temp_path:
                        st.audio(audio.temp_path, format='audio/wav')
                    else:
                        st.audio(audio.file_obj, format='audio/wav')
                with c_del:
                    if st.button("🗑️", key=f"{key_prefix}_del_{i}", help="Eliminar grabación"):
                        st.session_state[f"{key_prefix}_audios"].pop(i)
                        st.rerun()

    st.divider()
    c_accept, c_cancel = st.columns(2)
    
    with c_accept:
        # Usamos lógica imperativa para asegurar que el diálogo se cierre
        if st.button("✅ Guardar y Cerrar", key=f"{key_prefix}_save_all", use_container_width=True, type="primary", disabled=not audios_list or disabled):
            if on_audio_ready:
                # Devolver la lista completa
                current_audios = st.session_state.get(f"{key_prefix}_audios", [])
                on_audio_ready(current_audios)
            
            # Limpiar todo
            if f"{key_prefix}_audios" in st.session_state:
                del st.session_state[f"{key_prefix}_audios"]
            if temp_audio_key in st.session_state:
                del st.session_state[temp_audio_key]
            
            st.rerun()
                
    with c_cancel:
        if st.button("❌ Cancelar", key=f"{key_prefix}_cancel", use_container_width=True, disabled=disabled):
            # Limpiar todo
            if f"{key_prefix}_audios" in st.session_state:
                del st.session_state[f"{key_prefix}_audios"]
            if temp_audio_key in st.session_state:
                del st.session_state[temp_audio_key]
            
            st.rerun()

    st.markdown('<div class="debug-footer">src/components/common/audio_recorder.py</div>', unsafe_allow_html=True)
