import streamlit as st
from services.predictive_service import generar_alertas_predictivas
from components.triage.vital_signs import get_all_configs
from components.triage.triage_logic import calculate_worst_case

def render_risk_analysis_panel(patient_data, enable_predictive=True):
    """
    Renderiza el panel de análisis de riesgos (Pre-Triaje).
    Permite verificar riesgos con IA o mediante algoritmo determinista.
    
    Args:
        patient_data (dict): Datos del paciente (edad, signos vitales, antecedentes, alergias).
        enable_predictive (bool): Si está habilitado el análisis predictivo en configuración.
    """
    if not patient_data.get('vital_signs') or not enable_predictive:
        return

    with st.expander("🛡️ Análisis de Riesgos (Pre-Triaje)", expanded=True):
        col_btns, col_res = st.columns([1, 2])
        
        # Recuperar resultados existentes o inicializar
        if 'predictive_results' not in st.session_state:
            st.session_state.predictive_results = {}
        
        current_results = st.session_state.predictive_results
        has_algo = "ALGO" in current_results
        has_ai = "AI" in current_results
        
        with col_btns:
            # Botones de Análisis
            # 1. Sin IA
            if st.button("Verificar riesgos sin IA", 
                         help="Analizar signos vitales mediante algoritmo clínico estándar", 
                         key="btn_predictive_check_algo", 
                         use_container_width=True,
                         disabled=has_algo):
                
                with st.spinner("Calculando riesgos (Algoritmo)..."):
                    configs = get_all_configs(patient_data.get('edad', 40))
                    triage_result = calculate_worst_case(patient_data.get('vital_signs', {}), configs)
                    
                    priority = triage_result.get('final_priority', 0)
                    alerts = []
                    for detail in triage_result.get('details', []):
                        if detail.get('priority', 0) > 0:
                            alerts.append(f"{detail.get('metric', '').upper()}: {detail.get('value')} ({detail.get('label')})")
                    
                    risk_level = "Low"
                    if priority >= 3: risk_level = "High"
                    elif priority == 2: risk_level = "Medium"
                    
                    # --- INTEGRACIÓN RAG (Protocolos de Riesgo) ---
                    rag_alerts = []
                    try:
                        from services.rag_service import get_rag_service
                        rag = get_rag_service()
                        # Buscar protocolos relacionados con el motivo
                        query_text = patient_data.get('texto_medico', '') + " " + patient_data.get('antecedentes', '')
                        rag_docs = rag.search_documents(query_text, n_results=2)
                        
                        if rag_docs:
                            for doc in rag_docs:
                                source = doc['metadata'].get('source', 'Desconocido')
                                # Solo mostramos el nombre del protocolo como alerta
                                rag_alerts.append(f"📚 Protocolo Sugerido: {source}")
                    except Exception as e:
                        print(f"RAG Error in Risk Panel: {e}")
                        
                    # Combinar alertas
                    all_alerts = alerts + rag_alerts

                    st.session_state.predictive_results["ALGO"] = {
                        "status": "SUCCESS",
                        "risk_level": risk_level,
                        "alerts": all_alerts
                    }
                    st.rerun()

            # 2. Con IA
            if st.button("Verificar riesgos con IA", 
                         type="primary", 
                         help="Analizar signos vitales con IA", 
                         key="btn_predictive_check_ai", 
                         use_container_width=True,
                         disabled=has_ai):
                
                with st.spinner("Analizando riesgos (IA)..."):
                    # Preparar datos IA
                    antecedentes_txt = patient_data.get('antecedentes', '')
                    alergias_txt = patient_data.get('alergias_txt', '')
                    historia_integral = patient_data.get('historia_integral', '')
                    
                    # HDA
                    hda_fields = [
                        f"Aparición: {patient_data.get('hda_aparicion', '')}",
                        f"Localización: {patient_data.get('hda_localizacion', '')}",
                        f"Intensidad: {patient_data.get('hda_intensidad', '')}",
                        f"Características: {patient_data.get('hda_caracteristicas', '')}",
                        f"Irradiación: {patient_data.get('hda_irradiacion', '')}",
                        f"Alivio/Agravantes: {patient_data.get('hda_alivio', '')}",
                        f"Síntomas Asoc.: {patient_data.get('hda_sintomas_asoc', '')}",
                        f"Tratamiento Casa: {patient_data.get('hda_tratamiento_casa', '')}"
                    ]
                    hda_str = "\n".join([f for f in hda_fields if len(f.split(': ')[1]) > 0])
                    
                    # Contexto
                    ctx_fields = []
                    if patient_data.get('criterio_geriatrico'): ctx_fields.append("Criterio Geriátrico: SÍ")
                    if patient_data.get('criterio_inmunodeprimido'):
                         det = patient_data.get('criterio_inmunodeprimido_det', '')
                         ctx_fields.append(f"Inmunodeprimido: SÍ ({det})")
                    ctx_str = "\n".join(ctx_fields)
                    
                    pred_result, _ = generar_alertas_predictivas(
                        edad=patient_data.get('edad'),
                        vital_signs=patient_data.get('vital_signs'),
                        antecedentes=antecedentes_txt,
                        alergias=alergias_txt,
                        historia_integral=historia_integral,
                        hda=hda_str,
                        contexto_clinico=ctx_str
                    )
                    st.session_state.predictive_results["AI"] = pred_result
                    st.rerun()

            # 3. Ambos
            if st.button("🔍 Analizar AMBOS", 
                         help="Ejecutar ambos análisis y comparar", 
                         key="btn_predictive_check_both", 
                         use_container_width=True,
                         disabled=(has_algo and has_ai)):
                
                with st.spinner("Ejecutando análisis completo..."):
                    # 1. ALGO (Solo si falta)
                    if not has_algo:
                        configs = get_all_configs(patient_data.get('edad', 40))
                        triage_result = calculate_worst_case(patient_data.get('vital_signs', {}), configs)
                        priority = triage_result.get('final_priority', 0)
                        alerts_algo = []
                        for detail in triage_result.get('details', []):
                            if detail.get('priority', 0) > 0:
                                alerts_algo.append(f"{detail.get('metric', '').upper()}: {detail.get('value')} ({detail.get('label')})")
                        risk_algo = "Low"
                        if priority >= 3: risk_algo = "High"
                        elif priority == 2: risk_algo = "Medium"
                        
                        st.session_state.predictive_results["ALGO"] = {
                            "status": "SUCCESS", 
                            "risk_level": risk_algo, 
                            "alerts": alerts_algo
                        }

                    # 2. IA (Solo si falta)
                    if not has_ai:
                        antecedentes_txt = patient_data.get('antecedentes', '')
                        alergias_txt = patient_data.get('alergias_txt', '')
                        historia_integral = patient_data.get('historia_integral', '')
                        
                        hda_fields = [
                            f"Aparición: {patient_data.get('hda_aparicion', '')}",
                            f"Localización: {patient_data.get('hda_localizacion', '')}",
                            f"Intensidad: {patient_data.get('hda_intensidad', '')}",
                            f"Características: {patient_data.get('hda_caracteristicas', '')}",
                            f"Irradiación: {patient_data.get('hda_irradiacion', '')}",
                            f"Alivio/Agravantes: {patient_data.get('hda_alivio', '')}",
                            f"Síntomas Asoc.: {patient_data.get('hda_sintomas_asoc', '')}",
                            f"Tratamiento Casa: {patient_data.get('hda_tratamiento_casa', '')}"
                        ]
                        hda_str = "\n".join([f for f in hda_fields if len(f.split(': ')[1]) > 0])
                        
                        ctx_fields = []
                        if patient_data.get('criterio_geriatrico'): ctx_fields.append("Criterio Geriátrico: SÍ")
                        if patient_data.get('criterio_inmunodeprimido'):
                             det = patient_data.get('criterio_inmunodeprimido_det', '')
                             ctx_fields.append(f"Inmunodeprimido: SÍ ({det})")
                        ctx_str = "\n".join(ctx_fields)

                        pred_result_ai, _ = generar_alertas_predictivas(
                            edad=patient_data.get('edad'),
                            vital_signs=patient_data.get('vital_signs'),
                            antecedentes=antecedentes_txt,
                            alergias=alergias_txt,
                            historia_integral=historia_integral,
                            hda=hda_str,
                            contexto_clinico=ctx_str
                        )
                        st.session_state.predictive_results["AI"] = pred_result_ai
                    
                    st.rerun()
        
        with col_res:
            if 'predictive_results' in st.session_state and st.session_state.predictive_results:
                results = st.session_state.predictive_results
                
                # Función helper para renderizar un resultado
                def render_result(title, res, icon):
                    st.markdown(f"##### {icon} {title}")
                    if res.get("status") == "ERROR":
                        st.error(f"Error: {res.get('msg')}")
                    else:
                        risk = res.get("risk_level", "Low")
                        alerts = res.get("alerts", [])
                        
                        if risk == "High":
                            st.error(f"🚨 RIESGO ALTO")
                        elif risk == "Medium":
                            st.warning(f"⚠️ RIESGO MODERADO")
                        else:
                            st.success("✅ RIESGO BAJO")
                            
                        if alerts:
                            for alert in alerts:
                                st.caption(f"- {alert}")
                        else:
                            st.caption("Sin alertas específicas.")

                # Renderizar según lo que haya
                if "AI" in results and "ALGO" in results:
                    c_ai, c_algo = st.columns(2)
                    with c_ai: render_result("Análisis IA", results["AI"], "🤖")
                    with c_algo: render_result("Algoritmo", results["ALGO"], "🧮")
                elif "AI" in results:
                    render_result("Análisis IA", results["AI"], "🤖")
                elif "ALGO" in results:
                    render_result("Algoritmo Clínico", results["ALGO"], "🧮")
                    
                # --- VALIDACIÓN HUMANA ---
                st.divider()
                
                # --- RECOMENDACIONES DE AUTOCUIDADO (ELIMINADO - MOVIDO AL FINAL DEL TRIAJE) ---
                pass

    st.markdown('<div class="debug-footer">src/components/triage/risk_analysis_panel.py</div>', unsafe_allow_html=True)
