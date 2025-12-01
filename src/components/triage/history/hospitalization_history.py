import streamlit as st

def render_hospitalization_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Hospitalizaciones y Legal en un acordeón.
    """
    with st.expander("🏥 Hospitalizaciones y Legal", expanded=False):
        st.session_state.datos_paciente['hosp_recent'] = st.text_area("Ingresos Hospitalarios Recientes (3-6 meses)", value=st.session_state.datos_paciente.get('hosp_recent', ''), height=68, disabled=disabled, key=f"hosp_rec_{reset_count}")
        
        c_leg1, c_leg2 = st.columns(2)
        with c_leg1:
            st.session_state.datos_paciente['leg_tutor'] = st.text_input("Tutor Legal / Apoderado", value=st.session_state.datos_paciente.get('leg_tutor', ''), placeholder="Nombre y Teléfono", disabled=disabled, key=f"leg_tut_{reset_count}")
        with c_leg2:
            st.session_state.datos_paciente['leg_cuidador'] = st.text_input("Cuidador Principal", value=st.session_state.datos_paciente.get('leg_cuidador', ''), placeholder="Nombre y Relación", disabled=disabled, key=f"leg_care_{reset_count}")

        # New section for legal issues and advanced directives
        st.markdown("---") # Separator for clarity
        c_legal_issues1, c_legal_issues2 = st.columns(2)
        with c_legal_issues1:
            has_legal = st.checkbox("Problemas Legales / Judiciales", value=st.session_state.datos_paciente.get('hosp_legal', False), disabled=disabled, key=f"hosp_leg_{reset_count}")
            st.session_state.datos_paciente['hosp_legal'] = has_legal
            if has_legal:
                st.session_state.datos_paciente['hosp_legal_det'] = st.text_input("Detalles Legales", value=st.session_state.datos_paciente.get('hosp_legal_det', ''), key=f"hosp_leg_det_{reset_count}", disabled=disabled)
        with c_legal_issues2:
            st.session_state.datos_paciente['hosp_voluntades'] = st.checkbox("Documento Voluntades Anticipadas", value=st.session_state.datos_paciente.get('hosp_voluntades', False), disabled=disabled, key=f"hosp_vol_{reset_count}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/hospitalization_history.py</div>', unsafe_allow_html=True)
