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
        
        with col_btns:
            c_btn_algo, c_btn_ai = st.columns(2)
            
            # Botón Algoritmo (Sin IA) - Izquierda
            with c_btn_algo:
                if st.button("Verificar riesgos sin IA", help="Analizar signos vitales mediante algoritmo clínico estándar", key="btn_predictive_check_algo", use_container_width=True):
                    with st.spinner("Calculando riesgos..."):
                        configs = get_all_configs(patient_data.get('edad', 40))
                        triage_result = calculate_worst_case(patient_data.get('vital_signs', {}), configs)
                        
                        # Mapear prioridad a nivel de riesgo
                        priority = triage_result.get('final_priority', 0)
                        alerts = []
                        
                        # Generar alertas basadas en detalles
                        for detail in triage_result.get('details', []):
                            if detail.get('priority', 0) > 0:
                                alerts.append(f"{detail.get('metric', '').upper()}: {detail.get('value')} ({detail.get('label')})")
                        
                        risk_level = "Low"
                        if priority >= 3:
                            risk_level = "High"
                        elif priority == 2:
                            risk_level = "Medium"
                            
                        st.session_state.predictive_result = {
                            "status": "SUCCESS",
                            "risk_level": risk_level,
                            "alerts": alerts
                        }
                        st.session_state.predictive_source = "ALGO"

            # Botón IA - Derecha (Primary)
            with c_btn_ai:
                if st.button("Verificar riesgos con IA", type="primary", help="Analizar signos vitales con IA para detectar riesgos inminentes", key="btn_predictive_check_ai", use_container_width=True):
                    with st.spinner("Analizando riesgos con IA..."):
                        antecedentes_txt = patient_data.get('antecedentes', '')
                        alergias_txt = patient_data.get('alergias_txt', '')
                        historia_integral = patient_data.get('historia_integral', '')
                        
                        # Construir HDA (ALICIA)
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
                        
                        # Construir Contexto Clínico
                        ctx_fields = []
                        if patient_data.get('criterio_geriatrico'):
                            ctx_fields.append("Criterio Geriátrico: SÍ")
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
                        st.session_state.predictive_result = pred_result
                        st.session_state.predictive_source = "AI"
        
        with col_res:
            if 'predictive_result' in st.session_state and st.session_state.predictive_result:
                res = st.session_state.predictive_result
                source = st.session_state.get('predictive_source', 'AI')
                
                # Etiqueta de origen
                if source == "AI":
                    st.caption("🤖 Análisis IA Generativa")
                else:
                    st.caption("🧮 Algoritmo Clínico")
                
                if res.get("status") == "ERROR":
                    st.error(f"Error en análisis: {res.get('msg')}")
                else:
                    risk = res.get("risk_level", "Low")
                    alerts = res.get("alerts", [])
                    
                    if risk == "High":
                        st.error(f"🚨 RIESGO ALTO DETECTADO")
                        for alert in alerts:
                            st.markdown(f"- **{alert}**")
                    elif risk == "Medium":
                        st.warning(f"⚠️ RIESGO MODERADO")
                        for alert in alerts:
                            st.markdown(f"- {alert}")
                    else:
                        st.success("✅ Sin riesgos inminentes detectados.")
                        if alerts:
                            for alert in alerts:
                                st.caption(f"- {alert}")
                    
                    # --- VALIDACIÓN HUMANA ---
                    st.divider()
                    st.markdown("**¿Es correcta esta predicción?**")
                    c_val_1, c_val_2 = st.columns(2)
                    
                    # Claves únicas para los botones
                    key_up = "pred_val_up"
                    key_down = "pred_val_down"
                    
                    if st.button("👍 Correcto", key=key_up, use_container_width=True):
                        st.toast("Gracias por tu feedback (Positivo)", icon="✅")
                        st.session_state.predictive_feedback = "positive"
                        
                    if st.button("👎 Incorrecto", key=key_down, use_container_width=True):
                        st.toast("Gracias por tu feedback (Negativo)", icon="📝")
                        st.session_state.predictive_feedback = "negative"
                        
                    if 'predictive_feedback' in st.session_state:
                        if st.session_state.predictive_feedback == "positive":
                            st.caption("✅ Validado positivamente")
                        else:
                            st.caption("❌ Marcado como incorrecto")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/risk_analysis_panel.py</div>', unsafe_allow_html=True)
