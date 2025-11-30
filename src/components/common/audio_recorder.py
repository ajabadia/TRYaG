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
    
    # Clave dinámica para reiniciar el widget de audio
    if f"{key_prefix}_uploader_key" not in st.session_state:
        st.session_state[f"{key_prefix}_uploader_key"] = 0
        
    audio_key = f"{key_prefix}_recorder_{st.session_state[f'{key_prefix}_uploader_key']}"
    # st.audio_input no soporta disabled nativamente en todas las versiones, 
    # pero podemos ocultarlo o mostrar mensaje si está disabled.
    if disabled:
        st.info("Grabación bloqueada.")
    else:
        audio_value = st.audio_input("Grabar nota de voz", key=audio_key)
    
        # Estado local temporal para este componente
        temp_audio_key = f"{key_prefix}_temp_val"
        
        if audio_value:
            # Guardar en estado temporal si no está ya o es nuevo
            if temp_audio_key not in st.session_state or st.session_state[temp_audio_key]['value'] != audio_value:
                 st.session_state[temp_audio_key] = {
                     'value': audio_value,
                     'timestamp': datetime.now()
                 }

    # Mostrar controles si hay audio temporal
    temp_audio_key = f"{key_prefix}_temp_val"
    has_audio = temp_audio_key in st.session_state
    
    if has_audio:
        st.audio(st.session_state[temp_audio_key]['value'], format='audio/wav')
        
    st.divider()
    c_accept, c_cancel = st.columns(2)
    
    with c_accept:
        def handle_accept():
            try:
                audio_val = st.session_state[temp_audio_key]['value']
                # Guardar en disco temporal
                file_info = save_file_to_temp(audio_val, default_ext=".wav")
                
                # Crear wrapper
                audio_wrapper = TempFileWrapper(audio_val, file_info['name'], temp_path=file_info['path'], file_type="audio/wav")
                
                if on_audio_ready:
                    on_audio_ready(audio_wrapper)
                
                # Limpiar
                del st.session_state[temp_audio_key]
                st.session_state[f"{key_prefix}_uploader_key"] += 1 # Reiniciar widget
                st.rerun() # Cerrar modal
                
            except Exception as e:
                st.error(f"Error al guardar audio: {e}")

        st.button("✅ Añadir Grabación", key=f"{key_prefix}_accept", use_container_width=True, on_click=handle_accept, disabled=not has_audio or disabled)
                
    with c_cancel:
        if st.button("❌ Cancelar", key=f"{key_prefix}_cancel", use_container_width=True, disabled=disabled):
            if has_audio:
                del st.session_state[temp_audio_key]
            st.rerun()

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/common/audio_recorder.py</div>', unsafe_allow_html=True)
