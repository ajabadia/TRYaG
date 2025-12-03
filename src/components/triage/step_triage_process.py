# path: src/components/triage/step_triage_process.py
# Creado: 2025-11-24
"""
Paso 3 del Asistente de Triaje: Proceso de Triaje.
Orquesta los sub-pasos: entrada de datos, análisis IA y validación humana.
"""
import streamlit as st
from .input_form import render_input_form
from .results_display import render_results_display
from .validation_form import render_validation_form
from services.recommendation_service import RecommendationService
from components.triage.recommendations_card import render_recommendations_card

def render_step_triage_process() -> bool:
    """
    Renderiza el proceso completo de triaje con sus sub-pasos.
    
    Returns:
        bool: True si la validación está completa, False en caso contrario.
    """
    st.subheader("3️⃣ Realizar Triaje")
    
    # Verificar que hay paciente seleccionado
    p = st.session_state.get('triage_patient')
    if not p:
        st.warning("⚠️ No hay paciente seleccionado.")
        return False
    
    # Mostrar información del paciente (Unificada)
    from ui.components.common.patient_card import render_patient_header
    render_patient_header(p, st.session_state.get('resultado'))
    
    # --- HERRAMIENTAS (MOVIDO A MAIN VIEW) ---
    # La sección de herramientas y descarga de PDF se ha movido al panel superior en main_view.py
    
    st.divider()
    
    # Sub-paso 1: Entrada de datos (motivo, dolor, imágenes, audio)
    analysis_done = st.session_state.get('analysis_complete', False)
    validation_done = st.session_state.get('validation_complete', False)
    
    # Plegar entrada si ya hay análisis
    with st.expander("📝 **1. Entrada de Datos**", expanded=not analysis_done):
        render_input_form()
        
        # --- AUTO-SAVE HOOK ---
        # Guardar borrador si hay cambios en datos clave
        if st.session_state.get('triage_record_id'):
            from services.triage_service import update_triage_draft
            # Recopilar datos actuales dinámicamente
            # Guardamos todo lo que hay en datos_paciente excepto objetos binarios/temporales
            data_to_save = {k: v for k, v in st.session_state.datos_paciente.items() 
                           if k not in ['imagenes', 'imagenes_confirmadas_ia']}
            
            # Mapeos de compatibilidad (Legacy)
            if 'texto_medico' in data_to_save:
                data_to_save['motivo_consulta'] = data_to_save['texto_medico']

            # Añadir estados externos a datos_paciente
            data_to_save['gi_responses'] = st.session_state.get('gi_responses', {})
            
            # Actualizar silenciosamente (sin rerun)
            update_triage_draft(st.session_state.triage_record_id, data_to_save)
    
    # --- RECOMENDACIONES (MOVIDO AL FINAL) ---
    
    st.divider()
    
    # Sub-paso 2: Resultados y sugerencias de la IA
    # Se muestra expandido si hay análisis pero aún no se ha calificado
    results_reviewed = st.session_state.get('calificacion_humana') is not None
    with st.expander("🤖 **2. Análisis y Sugerencias de IA**", expanded=analysis_done and not results_reviewed):
        render_results_display()
    
    st.divider()
    
    # Sub-paso 3: Validación humana
    # Se expande automáticamente SOLO si ya se ha calificado la IA
    with st.expander("✅ **3. Validación Humana**", expanded=results_reviewed):
        if results_reviewed:
            render_validation_form()
        else:
            st.info("Por favor, califique la respuesta de la IA en el paso anterior para continuar.")
    
    # --- RECOMENDACIONES (MOVIDO AL FINAL) ---
    # Se muestran siempre que haya un resultado de triaje (aunque sea preliminar)
    if analysis_done:
        st.divider()
        st.markdown("### 🩹 Recomendaciones al Paciente")
        
        # Obtener datos para recomendaciones
        # Intentamos obtener el nivel final validado, si no el de la IA
        triage_level = 5 # Default
        
        # Si hay validación final
        if validation_done and st.session_state.get('final_triage_level'):
             triage_level = st.session_state.get('final_triage_level')
        # Si hay resultado de IA
        elif st.session_state.get('resultado'):
             # Mapear color/nivel IA a número
             res = st.session_state.get('resultado')
             # Asumimos que 'nivel' viene como int o string parseable
             try:
                 triage_level = int(res.get('nivel_numero', 5))
             except:
                 pass
        
        # Signos vitales y dolor
        vs = st.session_state.datos_paciente.get('vital_signs', {})
        pain = vs.get('dolor', 0)
        if not pain: pain = st.session_state.datos_paciente.get('hda_intensidad', 0)
        try: pain = int(pain)
        except: pain = 0
        
        # Motivo
        symptom = st.session_state.datos_paciente.get('motivo_consulta', '')
        
        # Entrevista
        interview = st.session_state.get('gi_responses', {})
        
        # Generar
        recs = RecommendationService.get_recommendations(
            triage_level=triage_level,
            main_symptom=symptom,
            pain_level=pain,
            interview_data=interview
        )
        
        render_recommendations_card(recs)
        
        # Guardar en session state para el reporte
        st.session_state.current_recommendations = recs
        
        # Guardar en BD (Borrador) para que salgan en el reporte si se genera desde backend
        if st.session_state.get('triage_record_id'):
            from services.triage_service import update_triage_draft
            update_triage_draft(st.session_state.triage_record_id, {
                "recommendations": recs
            })

    # Retornar si la validación está completa
    st.markdown('<div class="debug-footer">src/components/triage/step_triage_process.py</div>', unsafe_allow_html=True)
    return st.session_state.get('validation_complete', False)
