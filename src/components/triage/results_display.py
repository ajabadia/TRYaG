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

            with c2:
                st.markdown("### Explicabilidad")
                for r in resultado["razones"]:
                    c_info_icon, c_info_text = st.columns([1, 20])
                    with c_info_icon:
                        render_icon("info", size=16, color="#17a2b8")
                    with c_info_text:
                        st.info(f"{r}")

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
                        "reference": f"Patient/{datos_paciente.get('patient_code', 'UNKNOWN')}",
                        "display": f"{datos_paciente.get('nombre', 'Paciente')} {datos_paciente.get('apellido1', '')}"
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
                
                st.code(json.dumps(fhir_payload, indent=2), language="json")
                
                import time
                with st.spinner("Conectando con bus de integración..."):
                    time.sleep(1.5)
                
                st.success(f"✅ Éxito. Registro de Triaje enviado y confirmado por el HCE.")
                st.caption("ID Transacción: `FHIR-ACK-2025-X99283`")
                
                if st.button("Cerrar", type="primary", use_container_width=True):
                    st.rerun()

            if st.button("📤 Enviar Registro y Cerrar Atención", type="primary", use_container_width=True):
                dialog_fhir()

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/results_display.py</div>', unsafe_allow_html=True)
