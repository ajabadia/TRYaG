import streamlit as st
from ui.components.common.patient_search import render_patient_search
from services.second_opinion_service import get_second_opinion_service
import json

def render_second_opinion_view():
    st.header("🧠 Segunda Opinión - Razonamiento Clínico Avanzado")
    st.markdown("Herramienta de soporte para casos complejos utilizando **Inteligencia Artificial Deductiva**.")
    
    # 1. Selector de Paciente
    patient = render_patient_search(key_prefix="sec_op")
    
    if not patient:
        st.info("Seleccione un paciente para iniciar el análisis.")
        return

    st.divider()
    
    # 2. Área de Trabajo
    col_context, col_analysis = st.columns([1, 1])
    
    service = get_second_opinion_service()
    
    # --- Context Column ---
    with col_context:
        st.subheader("📋 Contexto Agregado")
        
        # Recuperar lista de triajes disponibles para selección
        try:
             available_triages = service.get_available_triages(patient["patient_code"])
        except Exception as e:
             st.error(f"Error recuperando historial: {e}")
             available_triages = []

        # Selector de Historial
        st.write("Seleccione los episodios a cargar en contexto:")
        
        # Mapear para display
        options_map = {t["audit_id"]: f"{t['date'].strftime('%d/%m/%Y %H:%M')} - {t['summary']} (Nivel {t['level']})" for t in available_triages}
        
        # Default: El más reciente (primero de la lista)
        default_selected = [available_triages[0]["audit_id"]] if available_triages else []
        
        selected_ids = st.multiselect(
            "Triajes Previos",
            options=options_map.keys(),
            format_func=lambda x: options_map[x],
            default=default_selected,
            label_visibility="collapsed",
            placeholder="Seleccione historial para incluir..."
        )

        
        # Toggle de visualización
        view_mode = st.radio("Modo de Vista", ["👁️ Visual", "💻 Datos Crudos (JSON)"], horizontal=True, label_visibility="collapsed")
        
        # Recuperar contexto para pre-visualizar (FILTRADO)
        context = service._build_patient_context(patient["patient_code"], target_audit_ids=selected_ids)
        
        if view_mode == "💻 Datos Crudos (JSON)":
            with st.expander("Perfil y Antecedentes", expanded=True):
                st.json(context.get("patient_profile", {}))
                
            with st.expander(f"Historial de Triajes ({len(context.get('triage_history', []))} cargados)", expanded=True):
                st.json(context.get("triage_history", []))
                    
            with st.expander("Estado Actual"):
                st.json(context.get("current_status", "Paciente no activo en flujo"))
        else:
            # MODO VISUAL
            profile = context.get("patient_profile", {})
            st.markdown("#### 👤 Perfil del Paciente")
            p_cols = st.columns(2)
            with p_cols[0]:
                st.markdown(f"**Edad:** {profile.get('age', 'N/A')}")
                st.markdown(f"**Sexo:** {profile.get('gender', 'N/A')}")
            with p_cols[1]:
                 hist = profile.get('background', 'No registrado')
                 if isinstance(hist, list): hist = ", ".join(hist)
                 st.markdown(f"**Antecedentes:** {hist}")
            
            st.divider()
            
            st.markdown("#### 🏥 Historial Reciente (Selección para AI)")
            
            # --- SIMULACIÓN IMPORTACIÓN HCE ---
            col_imp_btn, col_imp_info = st.columns([0.4, 0.6])
            with col_imp_btn:
                if st.button("📥 Importar Historial HCE", help="Simulacion: Conectar con HIS/EHR"):
                    with st.spinner("Conectando con Servidor de Historia Clínica..."):
                        import time
                        time.sleep(1.5)
                    st.toast("✅ Historial Clínico Importado (Simulación)", icon="🏥")
                    st.session_state["hce_imported"] = True
            
            if st.session_state.get("hce_imported"):
                st.markdown("""
                <div style="background-color:#e6fffa;padding:10px;border-radius:5px;border:1px solid #4fd1c5;margin-bottom:10px;font-size:0.9em;">
                    <b>Datos Externos:</b> Se han anexado 3 episodios previos del Hospital General.
                </div>
                """, unsafe_allow_html=True)


            history = context.get("triage_history", [])
            selected_indices = []
            
            if not history:
                st.info("Sin registros de triaje previos.")
            else:
                for idx, item in enumerate(history):
                    # Usar expander para mostrar detalle completo
                    with st.expander(f"{item.get('date', '')[:10]} - {item.get('main_complaint', 'Sin motivo')} (Nivel {item.get('ai_level', '?')})", expanded=False):
                        
                        # Checkbox de selección (Header del contenido)
                        c_check, c_content = st.columns([0.1, 0.9])
                        with c_check:
                             if st.checkbox("Incluir", value=True, key=f"hist_sel_{idx}", help="Incluir este episodio en el análisis de segunda opinión"):
                                 selected_indices.append(idx)
                        
                        with c_content:
                            # Detalle Completo
                            st.write(f"**Motivo Consulta:** {item.get('medical_text', '-')}")
                            st.write(f"**Dolor:** {item.get('pain_level')}/10")
                            
                            # Vitals Row
                            vitals = item.get('vitals', {})
                            if vitals:
                                v_cols = st.columns(4)
                                v_cols[0].metric("TA", f"{vitals.get('sistolica')}/{vitals.get('diastolica')}")
                                v_cols[1].metric("FC", vitals.get('frecuencia_cardiaca'))
                                v_cols[2].metric("SatO2", vitals.get('saturacion'))
                                v_cols[3].metric("Temp", vitals.get('temperatura'))
                            
                            st.markdown("---")
                            st.write(f"**🤖 Razonamiento AI Prévio:**")
                            st.info(item.get('ai_reasoning', 'No disponible'))
                            
                            if item.get('allergies'):
                                st.write(f"**Alergias:** {item.get('allergies')}")
                                
                            # Adjuntos
                            files = item.get('attached_files', [])
                            if files:
                                st.caption(f"📂 Adjuntos: {', '.join(files)}")
            
            # FILTRAR CONTEXTO PARA LLAMADA A LA IA
            # Solo guardamos los índices seleccionados
            filtered_history = [history[i] for i in selected_indices]
            # Actualizamos context copy para el dump (no modificamos el original para no romper visuals)
            analysis_context = context.copy()
            analysis_context["triage_history"] = filtered_history
            
            st.divider()

            # --- SECCION ARCHIVOS ADJUNTOS (NUEVO) ---
            st.markdown("#### 📂 Archivos Adjuntos")
            
            # Inicializar estado de archivos si no existe
            if "sec_op_files" not in st.session_state:
                st.session_state["sec_op_files"] = []
            if "sec_op_selection" not in st.session_state:
                st.session_state["sec_op_selection"] = {} # Dict para tracking de seleccionados

            from components.common.file_importer import render_file_importer
            from components.triage.media_cards import render_media_card

            def on_files_uploaded(new_files):
                st.session_state["sec_op_files"].extend(new_files)
                # Auto-seleccionar nuevos
                for f in new_files:
                    st.session_state["sec_op_selection"][f.name] = True
            
            render_file_importer(key_prefix="sec_op", on_files_ready=on_files_uploaded)
            
            # Renderizar Cards de archivos existentes
            current_files = st.session_state["sec_op_files"]
            if current_files:
                # Filtrar borrados
                deleted = st.session_state.get("deleted_filenames", set())
                active_files = [f for f in current_files if f.name not in deleted]
                st.session_state["sec_op_files"] = active_files # Limpiar estado
                
                # Render grid
                cols = st.columns(3)
                for idx, f_obj in enumerate(active_files):
                    with cols[idx % 3]:
                        # Usar selection_key personalizado para aislar el estado del triaje
                        render_media_card(f_obj, idx, selection_key="sec_op_selection")
            else:
                st.caption("No hay archivos adjuntos.")

            st.divider()
            
            st.markdown("#### 📍 Estado Actual")
            curr = context.get("current_status")
            if not curr or curr == "Paciente no activo en flujo":
                st.warning("Paciente no activo actualmente.")
            else:
                st.success(f"**Ubicación:** {curr.get('location', 'Desconocida')} ({curr.get('state', 'Unknown')})")
                st.caption(f"Entrada: {curr.get('entry_time', '')}")
            
    # --- Analysis Column ---
    with col_analysis:
        st.subheader("💡 Análisis de Razonamiento (Gemini 2.5)")
        
        notes = st.text_area("Notas Clínicas / Duda Específica", placeholder="Ej: Paciente con dolor abdominal atípico y ECG normal. ¿Considerar isquemia mesentérica?")
        
        # Opciones de Análisis
        col_opts, col_btn = st.columns([0.6, 0.4])
        with col_opts:
            include_rag = st.checkbox("🔍 Incluir Protocolos (RAG)", value=True, help="Busca protocolos institucionales relevantes y los adjunta al contexto.")
        
        # Botón de Análisis
        with col_btn:
            btn_analyze = st.button("🚀 Analizar", type="primary", use_container_width=True)

        if btn_analyze:
            
            # Verificar Contingencia
            if st.session_state.get("contingency_mode", False):
                st.error("⛔ Servicio no disponible en Modo Manual (Sin IA).")
                st.info("Desactive el modo manual en la barra lateral para utilizar la IA.")
                return

            with st.spinner("🔄 Analizando caso completo... (Esto puede tardar unos segundos)"):
                try:
                    # 1. Obtener configuración dinámica (Prompt + Modelo)
                    config = service.get_active_configuration()
                    active_model = config["model"]
                    system_prompt = config["content"]
                    
                    # 2. Construir contenido del prompt (USANDO CONTEXTO FILTRADO)
                    context_str = json.dumps(analysis_context, indent=2, ensure_ascii=False)
                    
                    final_prompt_list = []
                    
                    # --- RAG LOGIC ---
                    rag_context_str = ""
                    if include_rag:
                        from services.rag_service import get_rag_service
                        rag_service = get_rag_service()
                        # Usar notas + queja principal del ultimo triaje como query
                        last_complaint = analysis_context.get("triage_history", [{}])[0].get("main_complaint", "")
                        query = f"{notes} {last_complaint}".strip()
                        if query:
                            docs = rag_service.search_context(query, n_results=3)
                            if docs:
                                rag_context_str = "\n\n[MEMORIA INSTITUCIONAL (Protocolos Local)]:\n" + "\n".join(docs)
                                # Guardar en contexto para el reporte PDF
                                analysis_context["rag_protocols"] = docs 

                    if "{data_aggregation}" in system_prompt:
                         final_prompt_text = system_prompt.replace("{data_aggregation}", context_str)
                         if notes:
                             final_prompt_text += f"\n\nNOTA CLINICA ADICIONAL: {notes}"
                         if rag_context_str:
                             final_prompt_text += rag_context_str
                         final_prompt_list.append(final_prompt_text)
                    else:
                         # Fallback concatenado
                         final_prompt_list.append(system_prompt)
                         final_prompt_list.append(f"CONTEXTO: {context_str}")
                         final_prompt_list.append(f"CONSULTA: {notes}")
                         if rag_context_str:
                             final_prompt_list.append(rag_context_str)

                    # 3. Incorporar Archivos Seleccionados (Multimodal)
                    selected_files_objs = []
                    files_metadata_str = []
                    
                    for f_obj in st.session_state.get("sec_op_files", []):
                        if st.session_state.get("sec_op_selection", {}).get(f_obj.name, False):
                            # Preparar objeto para Gemini (Image/Audio)
                            # Necesitamos leer el contenido. MediaCards ya sabe leerlo, pero aquí lo hacemos manual
                            # o usamos una utilidad. Prompt Manager / Gemini Client manejan Part?
                            # Asumimos que Gemini Client wrapper acepta objetos PIL Image o bytes.
                            
                            # Intentar leer contenido
                            content = None
                            if hasattr(f_obj, "temp_path") and f_obj.temp_path:
                                try:
                                    # Para imagenes, mejor pasar path o PIL
                                    fname = f_obj.name.lower()
                                    if fname.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                        from PIL import Image
                                        img = Image.open(f_obj.temp_path)
                                        selected_files_objs.append(img)
                                        files_metadata_str.append(f"[IMAGEN: {f_obj.name}]")
                                    # Audio/Video se suelen pasar como File API URI, pero si el wrapper lo soporta:
                                    # Por ahora la integracion basica suele sert imagenes.
                                    # Si es texto/pdf:
                                    elif fname.endswith(('.txt', '.md')):
                                        with open(f_obj.temp_path, 'r', encoding='utf-8') as tf:
                                            final_prompt_list.append(f"CONTENIDO DE {f_obj.name}:\n{tf.read()}")
                                            files_metadata_str.append(f"[TEXTO: {f_obj.name}]")
                                except Exception as e:
                                    print(f"Error loading file {f_obj.name}: {e}")
                            
                            # Add to list for Report
                    
                    # Store selected files metadata in context for Report
                    analysis_context["analyzed_files"] = files_metadata_str

                    # Merge text prompts + images
                    full_payload = final_prompt_list + selected_files_objs

                    # 4. Llamada a Gemini
                    response_data, raw_prompt = service.gemini.generate_content(
                        caller_id="second_opinion_view",
                        user_id=st.session_state.get("user_info", {}).get("username", "unknown"),
                        call_type="clinical_audit",
                        prompt_type="second_opinion_reasoning",
                        prompt_version_id="active",
                        model_name=active_model,
                        prompt_content=full_payload,
                        generation_config={"temperature": 0.2}
                    )
                    
                    if response_data.get("status") == "ERROR":
                        st.error(f"Error en análisis: {response_data.get('msg')}")
                    else:
                        # STORE RESULT IN SESSION STATE
                        st.session_state["sec_op_result"] = response_data
                        st.session_state["sec_op_context"] = analysis_context
                        # Force Rerun to update UI outside this scope
                        st.rerun()

                except Exception as e:
                    st.error(f"Error de ejecución: {str(e)}")

        # --- RENDER RESULT FROM STATE ---
        if "sec_op_result" in st.session_state:
             response_data = st.session_state["sec_op_result"]
             analysis_context = st.session_state.get("sec_op_context", {})
             
             st.success("Análisis Completado")
             res_text = response_data.get("text", "")
             
             # Intentar parsear JSON para visualización rica
             parsed_response = None
             try:
                 # Limpiar bloques de código markdown si existen ```json ... ```
                 clean_text = res_text.strip()
                 if clean_text.startswith("```"):
                     import re
                     clean_text = re.sub(r"^```json\s*|\s*```$", "", clean_text, flags=re.MULTILINE)
                 
                 parsed_response = json.loads(clean_text)
             except:
                 parsed_response = None

             if parsed_response and isinstance(parsed_response, dict):
                 # --- VISUALIZACIÓN ESTRUCTURADA ---
                 
                 # 1. Resumen Clínico
                 if "clinical_summary" in parsed_response:
                     st.info(f"**Resumen:** {parsed_response['clinical_summary']}")

                 # 2. Banderas Rojas (Prioridad Alta)
                 red_flags = parsed_response.get("red_flags", [])
                 if red_flags:
                     st.markdown("##### 🚨 Alertas Clínicas (Red Flags)")
                     for rf in red_flags:
                         st.error(rf, icon="🚩")

                 # 3. Hipótesis Diagnósticas
                 diags = parsed_response.get("diagnostic_hypothesis", [])
                 if diags:
                     st.markdown("##### 🩺 Hipótesis Diagnósticas")
                     for d in diags:
                         prob = d.get('probability', 'Desconocida')
                         color = "red" if "Alta" in prob else "orange" if "Media" in prob else "green"
                         
                         with st.container(border=True):
                             c1, c2 = st.columns([3, 1])
                             c1.markdown(f"**{d.get('diagnosis')}**")
                             c1.caption(f"{d.get('justification')}")
                             c2.markdown(f":{color}[**{prob}**]")

                 # 4. Acciones Recomendadas
                 actions = parsed_response.get("recommended_actions", [])
                 if actions:
                     st.markdown("##### 📋 Plan de Acción Recomendado")
                     for act in actions:
                         st.markdown(f"- {act}")

                 # 5. Proceso de Razonamiento (CoT)
                 thought_process = parsed_response.get("thought_process")
                 if thought_process:
                     with st.expander("🧠 Ver Proceso de Razonamiento (Chain of Thought)", expanded=False):
                         st.markdown(thought_process.replace("\n", "\n\n"))

             else:
                 # Fallback: Texto plano/Markdown
                 st.markdown(res_text)
                 
             # Debug raw data
             with st.expander("Ver Respuesta Cruda (JSON)", expanded=False):
                  st.json(response_data)
             
             
             st.divider()

             # --- FEEDBACK OBLIGATORIO ---
             from components.common.response_validator import render_response_validator
             
             # Usamos prefijo unico para Second Opinion
             feedback_result = render_response_validator(key_prefix="sec_op_feedback", label="Calificación del Análisis (Obligatorio para generar reporte)")
             
             # Guardar feedback en session state para usarlo al generar PDF
             if feedback_result["status"] == "valid":
                 st.session_state["sec_op_feedback_data"] = feedback_result
             else:
                 st.session_state["sec_op_feedback_data"] = None

             st.divider()
             
             # --- PDF GENERATION ON DEMAND ---
             # Boton deshabilitado si no hay feedback valido
             can_generate_pdf = (feedback_result["status"] == "valid")
             
             if st.button("📄 Generar Informe PDF", key="btn_gen_pdf_sec_op", disabled=not can_generate_pdf):
                  with st.spinner("Generando PDF..."):
                    try:
                        from services.report_service import generate_second_opinion_report
                        from datetime import datetime
                        import os
                        
                        # Generar bytes del PDF
                        pdf_bytes = generate_second_opinion_report(patient, analysis_context, response_data)
                        
                        # Guardar en temp
                        if not os.path.exists("temp"):
                            os.makedirs("temp")
                        
                        filename = f"Informe_Reasoning_{patient.get('patient_code', 'Unk')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                        filepath = os.path.join("temp", filename)
                        
                        with open(filepath, "wb") as f:
                            f.write(pdf_bytes)
                            
                        # Download Link (Server Side Fix)
                        download_url = f"/download_file_v7?filename={filename}"
                        st.markdown(f'''
                            <div style="background-color:#d4edda;color:#155724;padding:10px;border-radius:5px;margin-bottom:10px;">
                                ✅ Informe generado correctamente.
                            </div>
                            <a href="{download_url}" target="_blank" style="text-decoration:none;">
                                <div style="display:inline-flex;align-items:center;justify-content:center;padding:0.5rem 1rem;border-radius:0.5rem;background-color:#FF4B4B;color:white;font-weight:bold;">
                                    ⬇️ Descargar Archivo
                                </div>
                            </a>
                        ''', unsafe_allow_html=True)
                        
                    except Exception as pdf_err:
                         print(f"Error generating PDF: {pdf_err}")
                         st.error(f"No se pudo generar el PDF: {pdf_err}")

    # Footer de depuración (Standard)
    st.markdown('<div class="debug-footer">src/ui/modules/second_opinion_view.py</div>', unsafe_allow_html=True)
