import streamlit as st

def render_medications_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Farmacología en un acordeón.
    """
    with st.expander("💊 Farmacología y Medicación Habitual", expanded=False):
        st.session_state.datos_paciente['medication_list'] = st.text_area(
            "Medicación Actual (Nombre, Dosis, Horario)",
            value=st.session_state.datos_paciente.get('medication_list', ''),
            placeholder="Ej. Enalapril 20mg 1-0-0, Metformina 850mg 1-0-1...",
            height=100, disabled=disabled, key=f"med_list_{reset_count}"
        )
        
        c1, c2 = st.columns(2)
        with c1:
            takes_anticoagulants = st.checkbox(
                "🔴 Toma Anticoagulantes / Antiagregantes",
                value=st.session_state.datos_paciente.get('med_anticoagulantes', False),
                disabled=disabled, key=f"med_ac_{reset_count}"
            )
            st.session_state.datos_paciente['med_anticoagulantes'] = takes_anticoagulants
            
            if takes_anticoagulants:
                st.warning("⚠️ Riesgo de Sangrado")
                st.session_state.datos_paciente['med_anticoagulantes_det'] = st.text_input(
                    "¿Cuál/es?", 
                    value=st.session_state.datos_paciente.get('med_anticoagulantes_det', ''),
                    disabled=disabled, key=f"med_ac_det_{reset_count}"
                )

        with c2:
            vaccines_ok = st.checkbox(
                "Vacunación al día (Tétanos/Gripe/COVID)",
                value=st.session_state.datos_paciente.get('med_vacunas', False),
                disabled=disabled, key=f"med_vac_{reset_count}"
            )
            st.session_state.datos_paciente['med_vacunas'] = vaccines_ok
            
            if vaccines_ok:
                st.session_state.datos_paciente['med_vacunas_det'] = st.text_input(
                    "Detalles (Opcional)",
                    value=st.session_state.datos_paciente.get('med_vacunas_det', ''),
                    disabled=disabled, key=f"med_vac_det_{reset_count}"
                )

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/medications.py</div>', unsafe_allow_html=True)
