import streamlit as st
from components.triage.history.allergies import render_allergies_form
from components.triage.history.medications import render_medications_form
from components.triage.history.medical_history import render_medical_history_form
from components.triage.history.surgical_history import render_surgical_history_form
from components.triage.history.obgyn_history import render_obgyn_history_form
from components.triage.history.social_history import render_social_history_form
from components.triage.history.safety_alerts import render_safety_alerts_form

def render_patient_background_form(reset_count: int, disabled: bool = False):
    """
    Renderiza el formulario de antecedentes clínicos (Alergias, Farmacología, etc.).
    
    Args:
        reset_count: Contador para forzar el reset de los widgets si es necesario.
        disabled: Si el formulario debe estar deshabilitado.
    """
    st.subheader("Antecedentes Clínicos")
    
    # Renderizar módulos (Acordeones)
    render_allergies_form(reset_count, disabled)
    render_medications_form(reset_count, disabled)
    render_medical_history_form(reset_count, disabled)
    render_surgical_history_form(reset_count, disabled)
    render_obgyn_history_form(reset_count, disabled)
    render_social_history_form(reset_count, disabled)
    render_safety_alerts_form(reset_count, disabled)

    # --- AGREGACIÓN DE DATOS ---
    # Construimos un texto consolidado para 'antecedentes' que se pasará a la IA
    background_parts = []
    dp = st.session_state.datos_paciente
    
    # 1. Patologías (Medical History)
    pathologies = dp.get('ant_patologias_sel', [])
    if pathologies: background_parts.append(f"Patologías: {', '.join(pathologies)}")
    if dp.get('ant_otros_medicos'): background_parts.append(f"Otros Médicos: {dp.get('ant_otros_medicos')}")
    
    # 2. Medicación
    if dp.get('medication_list'): background_parts.append(f"Medicación: {dp.get('medication_list')}")
    
    if dp.get('med_anticoagulantes'): 
        background_parts.append(f"🔴 ANTICOAGULADO: {dp.get('med_anticoagulantes_det', '')}")
    
    if dp.get('med_vacunas'):
        background_parts.append(f"Vacunación al día: {dp.get('med_vacunas_det', '')}")
        
    # 3. Quirúrgicos
    if dp.get('ant_quirurgicos_txt'): background_parts.append(f"Quirúrgicos: {dp.get('ant_quirurgicos_txt')}")
    
    if dp.get('ant_anestesia'):
        background_parts.append(f"Complicaciones Anestesia: {dp.get('ant_anestesia_det', '')}")
    if dp.get('ant_implantes'):
        background_parts.append(f"Implantes: {dp.get('ant_implantes_det', '')}")
        
    # 4. Gineco-Obs
    if dp.get('ant_go_embarazo'): 
        background_parts.append(f"Posible Embarazo: {dp.get('ant_go_detalles', '')}")
    if dp.get('ant_go_fur'):
        background_parts.append(f"FUR: {dp.get('ant_go_fur')}")
        
    # 5. Social
    habits = dp.get('soc_habitos', [])
    if habits: background_parts.append(f"Hábitos: {', '.join(habits)}")
    
    if dp.get('soc_convivencia'): background_parts.append(f"Social: {dp.get('soc_convivencia')}")
    if dp.get('soc_funcional'): background_parts.append(f"Funcional: {dp.get('soc_funcional')}")
    
    if dp.get('soc_caidas'): 
        background_parts.append(f"Caídas Recientes: {dp.get('soc_caidas_det', '')}")
    if dp.get('soc_cognitivo'): 
        background_parts.append(f"Cognitivo: {dp.get('soc_cognitivo_det', '')}")
        
    # 6. Alertas de Seguridad
    if dp.get('alert_transfusiones'):
        background_parts.append(f"Transfusiones: {dp.get('alert_transfusiones_det', '')}")
    if dp.get('alert_mrsa'): 
        background_parts.append(f"Aislamiento (MRSA/Multi): {dp.get('alert_mrsa_det', '')}")
    if dp.get('alert_dnr'): 
        background_parts.append(f"⚠️ DNR (No Reanimar): {dp.get('alert_dnr_det', '')}")
    
    full_background = "\n".join(background_parts)
    st.session_state.datos_paciente['antecedentes'] = full_background
    
    # --- RESUMEN PLEGABLE (VISTA PREVIA IA) ---
    with st.expander("📄 Resumen Antecedentes (Vista Previa IA)", expanded=False):
        alergias_str = dp.get('alergias_info_completa', 'No conocidas')
        if full_background or (alergias_str and alergias_str != "No"):
            st.markdown("**Alergias:**")
            st.info(alergias_str)
            st.markdown("**Antecedentes:**")
            st.code(full_background if full_background else "Sin antecedentes registrados", language="text")
        else:
            st.caption("No hay datos registrados.")

    st.markdown('<div class="debug-footer">src/components/triage/patient_background_form.py</div>', unsafe_allow_html=True)
