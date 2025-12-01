import streamlit as st

def render_psych_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Psiquiatría y Salud Mental en un acordeón.
    """
    with st.expander("🧠 Psiquiatría y Salud Mental", expanded=False):
        from src.db.repositories.clinical_options import get_clinical_options_repository
        repo = get_clinical_options_repository()
        
        c_psy1, c_psy2 = st.columns(2)
        with c_psy1:
            opt_dx = repo.get_options("psych_diagnosis")
            st.session_state.datos_paciente['psy_diagnostico'] = st.multiselect(
                "📋 Diagnósticos Psiquiátricos",
                options=[opt.label for opt in opt_dx],
                default=st.session_state.datos_paciente.get('psy_diagnostico', []) if isinstance(st.session_state.datos_paciente.get('psy_diagnostico'), list) else [],
                disabled=disabled, key=f"psy_dx_{reset_count}",
                help="Enfermedades mentales diagnosticadas"
            )
            st.session_state.datos_paciente['psy_diagnostico_otros'] = st.text_input("Otros Diagnósticos Psiquiátricos", value=st.session_state.datos_paciente.get('psy_diagnostico_otros', ''), key=f"psy_dx_oth_{reset_count}", disabled=disabled)

        with c_psy2:
            has_suicide = st.checkbox("⚠️ Riesgo de Suicidio / Autolesión", value=st.session_state.datos_paciente.get('psy_suicidio', False), disabled=disabled, key=f"psy_suicide_{reset_count}", help="Ideación o intentos autolíticos recientes")
            st.session_state.datos_paciente['psy_suicidio'] = has_suicide
            
            if has_suicide:
                st.warning("Protocolo de Seguridad Activado: Notificar a Psiquiatría de Guardia.")
                st.session_state.datos_paciente['psy_suicidio_det'] = st.text_input("📝 Detalles Riesgo", value=st.session_state.datos_paciente.get('psy_suicidio_det', ''), key=f"psy_suicide_det_{reset_count}", disabled=disabled, help="Planificación, intentos previos, método...")
            
            opt_meds = repo.get_options("psych_medication")
            st.session_state.datos_paciente['psy_medicacion'] = st.multiselect(
                "💊 Medicación Psicotrópica",
                options=[opt.label for opt in opt_meds],
                default=st.session_state.datos_paciente.get('psy_medicacion', []) if isinstance(st.session_state.datos_paciente.get('psy_medicacion'), list) else [],
                disabled=disabled, key=f"psy_meds_{reset_count}",
                help="Tratamiento farmacológico actual"
            )
            st.session_state.datos_paciente['psy_medicacion_otros'] = st.text_input("Otra Medicación Psicotrópica", value=st.session_state.datos_paciente.get('psy_medicacion_otros', ''), key=f"psy_meds_oth_{reset_count}", disabled=disabled)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/psych_history.py</div>', unsafe_allow_html=True)
