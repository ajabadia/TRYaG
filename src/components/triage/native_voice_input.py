
import streamlit as st
import hashlib
from services.transcription_service import transcribir_audio
from services.conversational_service import ConversationalService
from services.contingency_service import is_contingency_active

def render_native_voice_input(reset_count, target_widget_key=None):
    """
    Renderiza el componente de entrada de voz nativa (st.audio_input) 
    con lógica híbrida (Transcripción + Extracción de datos).
    
    Args:
        reset_count (int): Contador para resetear claves de estado.
        target_widget_key (str): Clave del st.text_area destino para sincronización directa.
    """
    
    # 0. Cabecera y Label (Full Width)
    c_label_icon, c_label_text = st.columns([0.5, 9.5])
    with c_label_icon:
        st.write("🎤") # Simple icon
    with c_label_text:
        if is_contingency_active():
             st.caption("Dictado desactivado (Contingencia)")
        else:
             st.caption("Dictado Inteligente")

    # 1. Contenedor de Audio (Full Width)
    native_voice_text = None
    
    
    if is_contingency_active():
        st.error("🚫 Servicio de voz no disponible offline.")
        return



    try:
        if hasattr(st, "audio_input"):
            audio_val = st.audio_input("Dictar", key=f"voice_input_native_{reset_count}", label_visibility="collapsed")
            
            # --- Botonera Auxiliar (Reprocesar / Recargar) ---
            # Solo mostrar si hay audio grabado
            if audio_val:
                c_reload, c_reprocess = st.columns(2)
                with c_reload:
                     if st.button("📤 Insertar Transcripción", key=f"btn_force_insert_{reset_count}", help="Fuerza la inserción del texto transcrito en el campo de motivo", use_container_width=True):
                         # Recuperar último texto transcrito conocido
                         last_text = st.session_state.get(f"last_voice_text_raw_{reset_count}")
                         if last_text:
                             _append_text_to_patient_data(last_text, target_widget_key)
                             st.session_state[f"show_success_{reset_count}"] = True
                             st.rerun()
                         else:
                             st.warning("No hay transcripción disponible para insertar.")

                with c_reprocess:
                    if st.button("🔄 Reprocesar Audio", key=f"btn_reprocess_{reset_count}", help="Vuelve a analizar el audio actual", use_container_width=True):
                        # Resetear hash para forzar ejecución
                        st.session_state[f"last_voice_hash_{reset_count}"] = "force_retry"
                        st.rerun()

            # --- Mensaje de éxito (Debajo de botones) ---
            if st.session_state.pop(f"show_success_{reset_count}", False):
                st.success("Texto insertado correctamente.")

            # --- Lógica Principal ---
            if audio_val:
                # Procesar audio nativo
                audio_hash = hashlib.md5(audio_val.getvalue()).hexdigest()
                last_processed = st.session_state.get(f"last_voice_hash_{reset_count}")
                
                if last_processed != audio_hash:
                    with st.spinner("Transcribiendo y Analizando (Dictado Clínico)..."):
                        # Use dedicated clinical dictation prompt
                        full_response, trans_text = transcribir_audio(audio_val, prompt_type="clinical_dictation")
                        
                        if trans_text:
                            native_voice_text = trans_text
                            st.session_state[f"last_voice_hash_{reset_count}"] = audio_hash
                            st.session_state[f"last_voice_text_raw_{reset_count}"] = trans_text # Guardar para fallback
                            
                            # --- PERSISTENCE & UNIFICATION LOGIC ---
                            # 1. Guardar Audio en Disco
                            import os
                            import time
                            from utils.file_handler import TempFileWrapper
                            from core.transcription_handler import save_transcription
                            
                            temp_dir = "temp"
                            if not os.path.exists(temp_dir):
                                os.makedirs(temp_dir)
                                
                            filename = f"voice_input_{int(time.time())}_{audio_hash[:6]}.wav"
                            file_path = os.path.join(temp_dir, filename)
                            
                            with open(file_path, "wb") as f:
                                f.write(audio_val.getvalue())
                                
                            # 2. Guardar Transcripción en BD
                            # Reconstruir objeto de respuesta compatible con save_transcription
                            # Si full_response es dict con estructura compleja, usarlo.
                            # Si es raw text, empaquetarlo.
                            transcription_data = {}
                            if isinstance(full_response, dict):
                                transcription_data = full_response
                            else:
                                transcription_data = {
                                    "original_text": native_voice_text,
                                    "translated_ia_text": native_voice_text,
                                    "language_code": "es",
                                    "language_name": "Español"
                                }
                                
                            save_transcription(audio_hash, transcription_data, source="AI")
                            
                            # 3. Añadir a la lista de archivos del paciente (Unificación UI)
                            # Verificar duplicados por nombre o hash
                            existing_files = st.session_state.datos_paciente.get('imagenes', [])
                            is_duplicate = any(calculate_md5(f) == audio_hash for f in existing_files)
                            
                            if not is_duplicate:
                                # Crear Wrapper
                                new_file = TempFileWrapper(file_path, filename, "audio/wav")
                                if 'imagenes' not in st.session_state.datos_paciente:
                                    st.session_state.datos_paciente['imagenes'] = []
                                st.session_state.datos_paciente['imagenes'].append(new_file)
                                # Marcar como seleccionado por defecto para análisis
                                if 'modal_image_selection' not in st.session_state:
                                    st.session_state.modal_image_selection = {}
                                st.session_state.modal_image_selection[filename] = True

                            # --- HYBRID VOICE LOGIC (REFINED) ---
                            analysis_result = {}
                            if isinstance(full_response, dict):
                                analysis_result = full_response.get("structured_data", {})
                                # Update native_voice_text to be just the transcription part if available
                                if "transcription" in full_response:
                                    native_voice_text = full_response["transcription"]
                            
                            # Fallback Analysis (si el prompt específico falló en estructura)
                            if not analysis_result:
                                    analysis_result = ConversationalService.analyze_clinical_text(native_voice_text)

                            # 2. Rellenar campos automáticamente
                            if analysis_result:
                                # A. Motivo de Consulta
                                extracted_motivo = analysis_result.get("motivo_consulta") or analysis_result.get("historia_actual") or analysis_result.get("transcription")
                                
                                if extracted_motivo:
                                    # NOTA: Usamos native_voice_text como fallback si el motivo es muy corto o nulo, 
                                    # pero idealmente usamos el extraído/limpio.
                                    text_to_insert = extracted_motivo if len(extracted_motivo) > 5 else native_voice_text
                                    _append_text_to_patient_data(text_to_insert, target_widget_key)
                                
                                # B. Signos Vitales
                                extracted_vitals = analysis_result.get("vital_signs", {})
                                fields_updated = []
                                if extracted_vitals:
                                    current_vitals = st.session_state.datos_paciente.get('vital_signs', {})
                                    
                                    # Helper para actualizar solo si hay valor
                                    def update_vital(key_json, key_state):
                                        val = extracted_vitals.get(key_json)
                                        if val is not None: 
                                            current_vitals[key_state] = val
                                            return True
                                        return False

                                    if update_vital('tas', 'pas'): fields_updated.append("TAS")
                                    if update_vital('tad', 'pad'): fields_updated.append("TAD")
                                    if update_vital('fc', 'fc'): fields_updated.append("FC")
                                    if update_vital('temp', 'temp'): fields_updated.append("Temp")
                                    if update_vital('spo2', 'spo2'): fields_updated.append("SpO2")
                                    
                                    st.session_state.datos_paciente['vital_signs'] = current_vitals

                                # Notificar al usuario
                                success_msg = []
                                if extracted_motivo: success_msg.append("Texto")
                                if fields_updated: success_msg.append(f"Vitales ({', '.join(fields_updated)})")
                                
                                if success_msg:
                                    st.toast(f"Datos Actualizados: {', '.join(success_msg)}", icon="✨")
                                
                                # Forzar rerun para refrescar UI
                                st.session_state[f"voice_processed_{audio_hash}"] = True
                                st.rerun()

                            else:
                                # Fallback simple (solo texto sin estructura)
                                st.toast("Texto transcrito (Sin datos estructurados)", icon="📝")
                                _append_text_to_patient_data(native_voice_text, target_widget_key)
                                st.session_state[f"voice_processed_{audio_hash}"] = True
                                st.rerun()
                                
    except Exception as e:
        st.error(f"Error de voz: {e}")

    # Debug Footer
    st.markdown('<div class="debug-footer">src/components/triage/native_voice_input.py</div>', unsafe_allow_html=True)


def _append_text_to_patient_data(new_text, widget_key=None):
    """
    Helper para añadir texto al campo médico de forma segura,
    actualizando tanto el modelo de datos como el estado del widget.
    Sigue la lógica "Añadir al final" (Append).
    """
    if not new_text: return

    current_text = st.session_state.datos_paciente.get('texto_medico', '')
    
    # Asegurar separador si hay texto previo
    if current_text and not current_text.endswith(("\n", " ")):
        current_text += " "
    
    final_text = current_text + new_text
    
    # 1. Actualizar modelo de datos
    st.session_state.datos_paciente['texto_medico'] = final_text
    
    # 2. Actualizar estado del widget directamente (CRÍTICO para que se vea en el textarea)
    if widget_key:
        st.session_state[widget_key] = final_text
