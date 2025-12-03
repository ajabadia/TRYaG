# path: src/components/triage/results_display.py
# Creado: 2025-11-21
# Última modificación: 2025-11-22
"""
Componente para mostrar los resultados y sugerencias del asistente de triaje.
"""
import streamlit as st
from utils.icons import render_icon
from utils.session_utils import reset_session_state

def render_results_display():
    """
    Renderiza la sección de resultados y sugerencias de la IA.
    """
    if st.session_state.resultado:
        resultado = st.session_state.resultado
        datos_paciente = st.session_state.datos_paciente

        if resultado.get("status") in ["ERROR", "EXCLUDED"]:
            st.error(f"Error en el análisis: {resultado.get('msg', 'Desconocido')}")
            st.info("💡 Puede volver al paso de selección de paciente para iniciar un nuevo análisis.")
        else:
            st.divider()
            
            # --- WARNINGS DISPLAY ---
            if "warnings" in resultado and resultado["warnings"]:
                for w in resultado["warnings"]:
                    st.warning(w, icon="⚠️")
            
            # Cabecera con icono
            c_head_icon, c_head_text = st.columns([1, 20])
            with c_head_icon:
                render_icon("robot", size=24, color="#007bff")
            with c_head_text:
                st.header("2. Sugerencia del Asistente")

            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"### Sugerencia\n:traffic_light: **{resultado['nivel']['text']}**")
                st.markdown(f"<div style='background-color:{resultado['nivel']['color']};height:30px;border-radius:5px;'></div>", unsafe_allow_html=True)
                if datos_paciente.get('imagenes_confirmadas_ia'):
                    st.markdown("---")
                    st.markdown("##### Archivos Enviados")
                    # Iterar para mostrar imágenes o audios según corresponda
                    for f in datos_paciente['imagenes_confirmadas_ia']:
                        # Verificar si es audio (por nombre o extensión)
                        # Nota: f es un TempFileWrapper
                        is_audio = f.name.startswith("audio_") or f.name.endswith(('.wav', '.mp3', '.ogg'))
                        
                        if is_audio:
                            st.caption(f"🎤 {f.name}")
                            # Si queremos reproducirlo:
                            # st.audio(f.temp_path if f.temp_path else f.file_obj)
                        else:
                            # Es imagen
                            # Usar temp_path si existe para evitar problemas con wrappers
                            img_source = f.temp_path if hasattr(f, 'temp_path') and f.temp_path else f
                            
                            # Validar existencia si es path
                            import os
                            if isinstance(img_source, str) and not os.path.exists(img_source):
                                st.warning(f"⚠️ Imagen no disponible: {f.name}")
                            else:
                                st.image(img_source, width=150, caption=f.name)
                
                # --- PTR DISPLAY ---
                if "ptr_result" in resultado:
                    ptr = resultado["ptr_result"]
                    st.divider()
                    st.markdown(f"#### 🧮 PTR: {ptr['score']}")
                    st.caption(f"Nivel: {ptr['level_text']}")
                    
                    # Barra de progreso visual (Max estimado 20)
                    st.progress(min(ptr['score'] / 20, 1.0))
                    
                    with st.expander("Detalles del Cálculo"):
                        for det in ptr['details']:
                            st.text(f"• {det}")

            with c2:
                st.markdown("### Explicabilidad")
                
                razones = resultado.get("razones", [])
                
                # Función callback para actualizar feedback
                def update_reason_feedback(idx, field, value):
                    st.session_state.resultado["razones"][idx][field] = value
                    # Actualizar borrador en BD
                    if st.session_state.get('triage_record_id'):
                        from services.triage_service import update_triage_draft
                        # Convertir razones a formato compatible (lista de dicts)
                        update_triage_draft(st.session_state.triage_record_id, {
                            "razones_ia": st.session_state.resultado["razones"]
                        })

                for i, r in enumerate(razones):
                    # Manejo de compatibilidad (si r es string)
                    if isinstance(r, str):
                        r = {"text": r, "human_eval": None, "included_in_decision": True}
                        st.session_state.resultado["razones"][i] = r
                    
                    text = r.get("text", "")
                    eval_val = r.get("human_eval")
                    included = r.get("included_in_decision", True)
                    
                    # Contenedor visual para cada razón
                    with st.container(border=True):
                        c_info_icon, c_info_text = st.columns([1, 15])
                        with c_info_icon:
                            render_icon("info", size=16, color="#17a2b8")
                        with c_info_text:
                            st.markdown(f"**{text}**")
                        
                        # Controles de evaluación
                        c_eval, c_include = st.columns([2, 2])
                        with c_eval:
                            # Botones tipo toggle
                            col_up, col_down = st.columns(2)
                            with col_up:
                                if st.button("👍", key=f"up_{i}", type="primary" if eval_val == "positive" else "secondary", use_container_width=True):
                                    update_reason_feedback(i, "human_eval", "positive")
                                    st.rerun()
                            with col_down:
                                if st.button("👎", key=f"down_{i}", type="primary" if eval_val == "negative" else "secondary", use_container_width=True):
                                    update_reason_feedback(i, "human_eval", "negative")
                                    # Si es negativo, sugerir no incluir
                                    update_reason_feedback(i, "included_in_decision", False)
                                    st.rerun()
                        
                        with c_include:
                            if st.checkbox("Tener en cuenta", value=included, key=f"inc_{i}"):
                                if not included: # Cambio de False a True
                                    update_reason_feedback(i, "included_in_decision", True)
                                    st.rerun()
                            else:
                                if included: # Cambio de True a False
                                    update_reason_feedback(i, "included_in_decision", False)
                                    st.rerun()

            st.divider()
            st.markdown("##### Califique la respuesta")
            if st.session_state.calificacion_humana is None:
                col_ok, col_bad = st.columns(2)
                with col_ok:
                    if st.button("Correcto", use_container_width=True, icon=":material/thumb_up:"):
                        st.session_state.calificacion_humana = "Correcto"
                        st.rerun()
                with col_bad:
                    if st.button("Incorrecto", use_container_width=True, icon=":material/thumb_down:"):
                        st.session_state.calificacion_humana = "Incorrecto"
                        st.rerun()
            else:
                st.success(f"Calificación: **{st.session_state.calificacion_humana}**")
            
            # --- INTEROPERABILIDAD (SIMULACIÓN FHIR) ---
            st.divider()
            st.markdown("##### 🌍 Interoperabilidad")
            
            @st.dialog("📡 Enviar a Historia Clínica (FHIR)", width="large")
            def dialog_fhir():
                st.info("Simulando envío de recurso **Encounter** al servidor FHIR del hospital...")
                
                import json
                from datetime import datetime
                
                # Obtener datos reales del paciente (desde selección previa)
                patient_info = st.session_state.get('triage_patient', {})
                p_ref = f"Patient/{patient_info.get('id') or datos_paciente.get('patient_code') or 'UNKNOWN'}"
                p_name = f"{patient_info.get('nombre', '')} {patient_info.get('apellido1', '')}".strip()
                if not p_name: p_name = "Paciente Desconocido"

                # Simular Payload
                fhir_payload = {
                    "resourceType": "Encounter",
                    "status": "finished",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "EMER",
                        "display": "emergency"
                    },
                    "subject": {
                        "reference": p_ref,
                        "display": p_name
                    },
                    "period": {
                        "start": datetime.now().isoformat(),
                        "end": datetime.now().isoformat()
                    },
                    "reasonCode": [
                        {
                            "text": datos_paciente.get('texto_medico', 'No especificado')
                        }
                    ],
                    "priority": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                                "code": resultado['nivel']['text'],
                                "display": resultado['nivel']['text']
                            }
                        ]
                    }
                }
                
                st.code(json.dumps(fhir_payload, indent=2, ensure_ascii=False), language="json")
                
                import time
                with st.spinner("Conectando con bus de integración..."):
                    time.sleep(1.5)
                
                st.success(f"✅ Éxito. Registro de Triaje enviado y confirmado por el HCE.")
                st.caption("ID Transacción: `FHIR-ACK-2025-X99283`")
                
                if st.button("Cerrar", type="primary", use_container_width=True):
                    st.rerun()

            if st.button("📤 Enviar Registro y Cerrar Atención", type="primary", use_container_width=True):
                dialog_fhir()

    st.markdown('<div class="debug-footer">src/components/triage/results_display.py</div>', unsafe_allow_html=True)
