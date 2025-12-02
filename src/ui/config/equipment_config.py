import streamlit as st

def render_equipment_config():
    """
    Renderiza la configuración de equipamiento (Audio/Video).
    Simula la detección y selección de dispositivos.
    """
    st.subheader("📷 Configuración de Equipo")
    st.caption("Selecciona los dispositivos predeterminados para la captura de audio y video.")

    # Simulación de dispositivos detectados
    audio_devices = ["Predeterminado del sistema", "Micrófono (Realtek Audio)", "Micrófono (USB PnP Audio Device)"]
    video_devices = ["Predeterminado del sistema", "Cámara Integrada (0)", "Logitech C920 (1)"]
    
    # Cargar configuración actual (simulada en session_state por ahora)
    if 'equipment_config' not in st.session_state:
        st.session_state.equipment_config = {
            "audio_input": audio_devices[0],
            "video_input": video_devices[0],
            "video_quality": "Media (720p)"
        }
    
    config = st.session_state.equipment_config

    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎤 Audio")
            selected_audio = st.selectbox(
                "Dispositivo de Entrada (Micrófono)",
                options=audio_devices,
                index=audio_devices.index(config.get("audio_input", audio_devices[0])) if config.get("audio_input") in audio_devices else 0,
                key="equip_audio_input"
            )
            
        with col2:
            st.markdown("#### 📹 Video")
            selected_video = st.selectbox(
                "Dispositivo de Entrada (Cámara)",
                options=video_devices,
                index=video_devices.index(config.get("video_input", video_devices[0])) if config.get("video_input") in video_devices else 0,
                key="equip_video_input"
            )
            
            selected_quality = st.selectbox(
                "Calidad de Video",
                options=["Baja (480p)", "Media (720p)", "Alta (1080p)"],
                index=["Baja (480p)", "Media (720p)", "Alta (1080p)"].index(config.get("video_quality", "Media (720p)")),
                key="equip_video_quality"
            )

        if st.button("💾 Guardar Configuración de Equipo", type="primary"):
            st.session_state.equipment_config = {
                "audio_input": selected_audio,
                "video_input": selected_video,
                "video_quality": selected_quality
            }
            st.success("✅ Configuración de equipo guardada correctamente.")

    st.markdown('<div class="debug-footer">src/ui/config/equipment_config.py</div>', unsafe_allow_html=True)
