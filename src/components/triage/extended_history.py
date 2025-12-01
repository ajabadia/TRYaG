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

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/extended_history.py</div>', unsafe_allow_html=True)
