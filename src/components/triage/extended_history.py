import streamlit as st
from components.triage.history.family_history import render_family_history_form
from components.triage.history.psych_history import render_psych_history_form
from components.triage.history.nutrition_history import render_nutrition_history_form
from components.triage.history.travel_history import render_travel_history_form
from components.triage.history.sensory_history import render_sensory_history_form
from components.triage.history.pain_history import render_pain_history_form
from components.triage.history.hospitalization_history import render_hospitalization_history_form
from components.triage.history.forensic_history import render_forensic_history_form

def render_extended_history_form(disabled: bool = False):
    """
    Renderiza el formulario de Historia Clínica Integral (Antecedentes detallados).
    Organizado en secciones plegables para no saturar la vista.
    """
    st.markdown("##### 📚 Historia Clínica Integral")
    
    # Recuperar contador para keys únicas
    reset_count = st.session_state.get('reset_counter', 0)
    
    # Renderizar módulos
    render_family_history_form(reset_count, disabled)
    render_psych_history_form(reset_count, disabled)
    render_nutrition_history_form(reset_count, disabled)
    render_travel_history_form(reset_count, disabled)
    render_sensory_history_form(reset_count, disabled)
    render_pain_history_form(reset_count, disabled)
    render_hospitalization_history_form(reset_count, disabled)
    render_forensic_history_form(reset_count, disabled)

    # --- AGREGACIÓN DE DATOS (Historia Integral) ---
    # Construimos un texto consolidado para 'historia_integral' que se pasará a la IA
    history_parts = []
    dp = st.session_state.datos_paciente

    # 1. Familiares
    fam_parts = []
    if dp.get('ant_fam_cardio'): fam_parts.append(f"Cardio ({dp.get('ant_fam_cardio_det', '')})")
    if dp.get('ant_fam_cancer'): fam_parts.append(f"Cáncer ({dp.get('ant_fam_cancer_det', '')})")
    if dp.get('ant_fam_diabetes'): fam_parts.append(f"Diabetes ({dp.get('ant_fam_diabetes_det', '')})")
    if dp.get('ant_fam_genetica'): fam_parts.append(f"Genética: {dp.get('ant_fam_genetica')}")
    if fam_parts: history_parts.append(f"Familiares: {', '.join(fam_parts)}")

    # 2. Psiquiatría
    if dp.get('psy_diagnostico'): history_parts.append(f"Psiquiatría Dx: {dp.get('psy_diagnostico')}")
    if dp.get('psy_suicidio'): history_parts.append(f"⚠️ RIESGO SUICIDIO: {dp.get('psy_suicidio_det', '')}")
    if dp.get('psy_medicacion'): history_parts.append(f"Psicofármacos: {dp.get('psy_medicacion')}")

    # 3. Nutrición
    if dp.get('nut_dieta'): history_parts.append(f"Dieta: {dp.get('nut_dieta')}")
    if dp.get('nut_disfagia'): history_parts.append(f"Disfagia: {dp.get('nut_disfagia_det', '')}")
    if dp.get('nut_peso'): history_parts.append(f"Pérdida Peso: {dp.get('nut_peso_det', '')}")
    if dp.get('nut_alergias_alim'): history_parts.append(f"Alergias Alim.: {dp.get('nut_alergias_alim')}")

    # 4. Viajes/Expo
    if dp.get('travel_recent'): history_parts.append(f"Viajes: {dp.get('travel_recent')}")
    if dp.get('exp_animales'): history_parts.append(f"Animales: {dp.get('exp_animales_det', '')}")
    if dp.get('exp_ocupacional'): history_parts.append(f"Ocupacional: {dp.get('exp_ocupacional')}")

    # 5. Sensorial
    if dp.get('sens_auditivo'): history_parts.append(f"Déficit Auditivo: {dp.get('sens_auditivo_det', '')}")
    if dp.get('sens_visual'): history_parts.append(f"Déficit Visual: {dp.get('sens_visual_det', '')}")
    if dp.get('sens_idioma'): history_parts.append(f"Idioma: {dp.get('sens_idioma')}")
    if dp.get('sens_protesis'): history_parts.append(f"Prótesis: {dp.get('sens_protesis')}")

    # 6. Dolor
    if dp.get('pain_cronico'): history_parts.append(f"Dolor Crónico: {dp.get('pain_cronico_det', '')}")
    if dp.get('pain_opioides'): history_parts.append(f"Uso Opioides: Sí")

    # 7. Hospital/Legal
    if dp.get('hosp_recent'): history_parts.append(f"Ingresos Recientes: {dp.get('hosp_recent')}")
    if dp.get('leg_tutor'): history_parts.append(f"Tutor: {dp.get('leg_tutor')}")
    if dp.get('leg_cuidador'): history_parts.append(f"Cuidador: {dp.get('leg_cuidador')}")
    if dp.get('hosp_legal'): history_parts.append(f"Problemas Legales: {dp.get('hosp_legal_det', '')}")
    if dp.get('hosp_voluntades'): history_parts.append(f"Voluntades Anticipadas: Sí")

    # 8. Forense
    if dp.get('for_violencia'): history_parts.append(f"⚠️ VIOLENCIA: {dp.get('for_violencia_det', '')}")
    if dp.get('for_cultural'): history_parts.append(f"Cultural: {dp.get('for_cultural')}")
    if dp.get('cult_religion'): history_parts.append(f"Religión: {dp.get('cult_religion')}")

    full_history = "\n".join(history_parts)
    st.session_state.datos_paciente['historia_integral'] = full_history

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/extended_history.py</div>', unsafe_allow_html=True)
