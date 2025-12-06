import streamlit as st
from services.conversational_service import ConversationalService

def render_conversational_chat():
    """Renderiza la interfaz de chat para triaje conversacional."""
    
    c_title, c_reset = st.columns([8, 2])
    with c_title:
        st.markdown("### 💬 Asistente de Triaje")
        st.caption("Dialoga con la IA para completar la información clínica automáticamente.")
    with c_reset:
        if st.button("🧼 Limpiar", help="Reiniciar conversación"):
            st.session_state.chat_history = []
            st.rerun()

    # Inicializar historial
    if "chat_history" not in st.session_state or not st.session_state.chat_history:
        st.session_state.chat_history = []
        # Mensaje inicial
        greeting = ConversationalService.get_initial_greeting()
        st.session_state.chat_history.append({"role": "assistant", "content": greeting})

    # --- CONTROL DE VOZ ---
    # (Componente legado eliminado por solicitud del usuario. Se usa st.audio_input nativo)

    # Variable para procesar
    input_text = None
    
    # Renderizar historial
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ---------------------------------------------------------
    # LAYOUT DE ENTRADA
    # ---------------------------------------------------------

    # 2. Componente de Texto
    
    # --- NUEVO: Entrada de Voz Nativa (Streamlit >= 1.40) ---
    # Intentamos usar el input nativo de audio si existe, o un uploader si no.
    # Esto corre en paralelo al componente legacy 'speech_to_text' para no romper nada.
    
    native_audio_buffer = None
    from services.contingency_service import is_contingency_active
    
    if is_contingency_active():
        st.caption("🚫 Voz desactivada (Modo Contingencia)")
    else:
        try:
            # Check if st.audio_input exists (Streamlit 1.40+)
            if hasattr(st, "audio_input"):
                native_audio_buffer = st.audio_input("🎙️ Grabar respuesta (Nativo)")
            else:
                 # Fallback visual
                 with st.expander("🎙️ Subir nota de voz (Alternativa)", expanded=False):
                    native_audio_buffer = st.file_uploader("Subir audio", type=["wav", "mp3", "ogg"], key="chat_audio_upload")
        except Exception as e:
            print(f"Audio Input Error: {e}")

    if native_audio_buffer:
        # Procesar audio nativo
        from services.transcription_service import transcribir_audio
        
        # Usamos un hash del buffer para no reprocesar lo mismo en cada rerun
        import hashlib
        audio_bytes = native_audio_buffer.getvalue()
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        
        if st.session_state.get("last_processed_audio_hash") != audio_hash:
            with st.spinner("🎧 Transcribiendo audio..."):
                resp_data, trans_text = transcribir_audio(native_audio_buffer)
                
                if resp_data.get("status") == "OK" or trans_text:
                    # Usamos el texto de la IA (translated_ia_text) o el raw
                    final_transcription = resp_data.get("translated_ia_text", trans_text)
                    if not final_transcription and "text" in resp_data:
                         final_transcription = resp_data["text"]
                    
                    if final_transcription:
                        input_text = final_transcription
                        st.session_state.last_processed_audio_hash = audio_hash
                        st.toast("✅ Audio transcrito correctamente", icon="🎤")
                    else:
                        st.error("No se pudo extraer texto del audio.")
                else:
                    st.error(f"Error en transcripción: {resp_data.get('msg', 'Desconocido')}")

    chat_input_val = st.chat_input("Escribe o usa el micrófono 🎤...")
    if chat_input_val:
        input_text = chat_input_val

    # ---------------------------------------------------------
    # PROCESAMIENTO UNIFICADO
    # ---------------------------------------------------------
    if input_text:
        # 1. Mostrar usuario
        with st.chat_message("user"):
            st.write(input_text)
        st.session_state.chat_history.append({"role": "user", "content": input_text})

        # 2. Procesar con IA
        with st.spinner("Analizando..."):
            result = ConversationalService.process_message(input_text, st.session_state.chat_history)
            response = result.get("response", "Error al procesar.")
            data = result.get("extracted_data", {})
            status = result.get("interview_status", "CONTINUE")

        # 3. Mostrar respuesta IA
        with st.chat_message("assistant"):
            st.write(response)
            if data:
                # Mostrar feedback visual de extracción
                with st.status("📝 Extrayendo datos...", expanded=False):
                    if "sintomas" in data:
                        st.write(f"**Síntomas:** {', '.join(data['sintomas'])}")
                        # Sincronizar con el Formulario Principal
                        current_text = st.session_state.datos_paciente.get('texto_medico', '')
                        # Evitar duplicados si ya existe
                        sintomas_str = ', '.join(data['sintomas'])
                        if sintomas_str not in current_text:
                            new_text = f" [Chat: {sintomas_str}]"
                            st.session_state.datos_paciente['texto_medico'] = current_text + new_text
                            
                    if "critical_alert" in data and data["critical_alert"]:
                        st.error(f"🚩 ALERTA: {data['critical_alert']}")
                    
                    if "vital_signs_suggestion" in data:
                         st.info(f"Sugerencia: {data['vital_signs_suggestion']}")

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Guardar estado de finalización
        if status == "COMPLETED":
            st.session_state.chat_completed = True
            st.rerun()
            
    # --- UI DE FINALIZACIÓN ---
    if st.session_state.get("chat_completed", False):
        st.success("✅ **Entrevista Clínica Completada**")
        st.info("La IA ha recabado suficiente información. Los datos se han transferido al formulario inferior.")
        
        c_reopen, c_void = st.columns([3, 7])
        with c_reopen:
             if st.button("🔓 Reabrir Chat", help="Continuar hablando"):
                 st.session_state.chat_completed = False
                 st.rerun()
