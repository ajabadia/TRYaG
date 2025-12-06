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
    from components.common.speech_to_text import speech_to_text
    
    # Colocar el micro al pie, justo antes del chat_input? 
    # Streamlit no deja poner cosas "debajo" del chat_input.
    # Lo pondremos arriba del historial o flotando.
    # Mejor opción UX: Cerca del título para que sea visible.
    
    # Variable para procesar
    input_text = None
    
    # Renderizar historial
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ---------------------------------------------------------
    # LAYOUT DE ENTRADA (HÍBRIDO)
    # ---------------------------------------------------------
    
    # 1. Componente de Voz (Invisible si no se usa, o discreto)
    # Lo ponemos en un contenedor para darle estilo
    c_mic, c_space = st.columns([1, 15])
    with c_mic:
        voice_result = speech_to_text(key="chat_mic")
    with c_space:
        if voice_result and voice_result.get('isListening'):
            st.caption("🔴 Escuchando...")
    
    # Lógica de detección de voz
    if voice_result and voice_result.get('text') and voice_result.get('isFinal'):
        new_voice_text = voice_result.get('text')
        # Evitar procesar lo mismo dos veces
        if new_voice_text != st.session_state.get('last_chat_voice', ''):
            input_text = new_voice_text
            st.session_state.last_chat_voice = new_voice_text

    # 2. Componente de Texto
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
