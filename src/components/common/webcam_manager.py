# path: src/components/common/webcam_manager.py
import streamlit as st
import os
from datetime import datetime
from utils.file_handler import save_file_to_temp, TempFileWrapper

def render_webcam_manager(key_prefix="webcam", on_close=None, disabled=False):
    """
    Renderiza un gestor de webcam reutilizable con lógica de auto-captura y staging.
    
    Args:
        key_prefix (str): Prefijo para las claves de los widgets.
        on_close (callable): Función a llamar al cerrar. Recibe la lista de fotos confirmadas.
        disabled (bool): Si es True, deshabilita las interacciones.
    """
    
    # Inicializar estado local para este componente si no existe
    if f"{key_prefix}_photos" not in st.session_state:
        st.session_state[f"{key_prefix}_photos"] = []
    
    if f"{key_prefix}_reset_counter" not in st.session_state:
        st.session_state[f"{key_prefix}_reset_counter"] = 0

    st.markdown("##### 📷 Tomar fotografía/imagen")

    # Callback para auto-add
    def on_camera_change():
        pass 

    # Renderizar cámara
    # Usamos un contador en la key para forzar el remount y limpiar la vista tras captura
    cam_key = f"{key_prefix}_rec_{st.session_state[f'{key_prefix}_reset_counter']}"
    
    if disabled:
        st.info("Cámara bloqueada.")
    else:
        # st.camera_input devuelve el valor. Si hay valor, procesamos inmediatamente (Auto-add logic simulada en flujo imperativo)
        video_val = st.camera_input("Capturar imagen", key=cam_key, label_visibility="collapsed")
        
        if video_val:
            try:
                # Guardar inmediatamente
                file_info = save_file_to_temp(video_val, default_ext=".jpg") 
                wrapper = TempFileWrapper(video_val, f"cam_{datetime.now().strftime('%H%M%S')}.jpg", temp_path=file_info['path'], file_type="image/jpeg")
                
                # Añadir a staging
                st.session_state[f"{key_prefix}_photos"].append(wrapper)
                
                # Incrementar contador para limpiar
                st.session_state[f"{key_prefix}_reset_counter"] += 1
                st.rerun()
                
            except Exception as e:
                st.error(f"Error guardando captura: {e}")

    # --- STAGING AREA (CARRUSEL) ---
    photos = st.session_state[f"{key_prefix}_photos"]
    if photos:
        st.divider()
        st.markdown(f"**Fotos tomadas ({len(photos)}):**")
        
        cols = st.columns(4)
        for i, photo in enumerate(photos):
            with cols[i % 4]:
                if hasattr(photo, 'temp_path') and os.path.exists(photo.temp_path):
                    st.image(photo.temp_path, use_container_width=True)
                else:
                    st.image(photo.file_obj if hasattr(photo, 'file_obj') else photo, use_container_width=True)
                
                if st.button("🗑️", key=f"{key_prefix}_del_{i}", help="Eliminar foto", disabled=disabled):
                    st.session_state[f"{key_prefix}_photos"].pop(i)
                    st.rerun()

    st.divider()
    c_save, c_cancel = st.columns(2)
    
    with c_save:
        # Callback para guardar
        def handle_save():
            if on_close:
                # Recuperar fotos del estado antes de borrar
                current_photos = st.session_state.get(f"{key_prefix}_photos", [])
                on_close(current_photos)
            
            # Limpiar estado
            if f"{key_prefix}_photos" in st.session_state:
                del st.session_state[f"{key_prefix}_photos"]
            
            # No es necesario st.rerun() dentro de un callback

        # Botón Guardar y Cerrar
        st.button("✅ Guardar y Cerrar", key=f"{key_prefix}_save", type="primary", use_container_width=True, disabled=not photos or disabled, on_click=handle_save)

    with c_cancel:
        # Callback para cancelar
        def handle_cancel():
            # Limpiar estado
            if f"{key_prefix}_photos" in st.session_state:
                del st.session_state[f"{key_prefix}_photos"]
            
            if on_close:
                on_close(None) # None indica cancelación

        st.button("❌ Cancelar", key=f"{key_prefix}_cancel", use_container_width=True, on_click=handle_cancel, disabled=disabled)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/common/webcam_manager.py</div>', unsafe_allow_html=True)
