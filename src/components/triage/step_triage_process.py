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
            # Recopilar datos actuales
            current_data = {
                "vital_signs": st.session_state.datos_paciente.get('vital_signs'),
                "motivo_consulta": st.session_state.datos_paciente.get('texto_medico'), # Mapear a campo persistente
                "dolor": st.session_state.datos_paciente.get('dolor'),
                "antecedentes": st.session_state.datos_paciente.get('antecedentes'),
                "alergias": st.session_state.datos_paciente.get('alergias'),
                "sintomas_detectados": [], # Pendiente extraer de NLP si aplica
                # Nota: Las imágenes son archivos temporales, no se pueden guardar fácilmente en BD sin subirlos.
                # Se podría guardar metadatos si fuera crítico.
            }
            # Actualizar silenciosamente (sin rerun)
            update_triage_draft(st.session_state.triage_record_id, current_data)
    
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
    
    # Retornar si la validación está completa
    st.markdown('<div class="debug-footer">src/components/triage/step_triage_process.py</div>', unsafe_allow_html=True)
    return st.session_state.get('validation_complete', False)
