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

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/hospitalization_history.py</div>', unsafe_allow_html=True)
