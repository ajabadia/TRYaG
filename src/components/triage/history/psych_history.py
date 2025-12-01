import streamlit as st

def render_psych_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Psiquiatría y Salud Mental en un acordeón.
    """
    with st.expander("🧠 Psiquiatría y Salud Mental", expanded=False):
        c_psy1, c_psy2 = st.columns(2)
        with c_psy1:
            st.session_state.datos_paciente['psy_diagnostico'] = st.text_area("📋 Diagnósticos Psiquiátricos", value=st.session_state.datos_paciente.get('psy_diagnostico', ''), height=68, placeholder="Depresión, Ansiedad, Bipolar...", disabled=disabled, key=f"psy_dx_{reset_count}", help="Enfermedades mentales diagnosticadas")
        with c_psy2:
            has_suicide = st.checkbox("⚠️ Riesgo de Suicidio / Autolesión", value=st.session_state.datos_paciente.get('psy_suicidio', False), disabled=disabled, key=f"psy_suicide_{reset_count}", help="Ideación o intentos autolíticos recientes")
            st.session_state.datos_paciente['psy_suicidio'] = has_suicide
            
            if has_suicide:
                st.warning("Protocolo de Seguridad Activado: Notificar a Psiquiatría de Guardia.")
                st.session_state.datos_paciente['psy_suicidio_det'] = st.text_input("📝 Detalles Riesgo", value=st.session_state.datos_paciente.get('psy_suicidio_det', ''), key=f"psy_suicide_det_{reset_count}", disabled=disabled, help="Planificación, intentos previos, método...")
            
            st.session_state.datos_paciente['psy_medicacion'] = st.text_area("💊 Medicación Psicotrópica", value=st.session_state.datos_paciente.get('psy_medicacion', ''), height=68, placeholder="Antidepresivos, Antipsicóticos...", disabled=disabled, key=f"psy_meds_{reset_count}", help="Tratamiento farmacológico actual")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/psych_history.py</div>', unsafe_allow_html=True)
