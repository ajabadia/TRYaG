import streamlit as st

def render_family_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Antecedentes Familiares en un acordeón.
    """
    with st.expander("👨‍👩‍👧‍👦 Antecedentes Familiares", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.datos_paciente['ant_fam_cardio'] = st.checkbox("Enfermedad Cardiovascular (Infarto, Ictus)", value=st.session_state.datos_paciente.get('ant_fam_cardio', False), disabled=disabled, key=f"af_cardio_{reset_count}")
            st.session_state.datos_paciente['ant_fam_cancer'] = st.checkbox("Cáncer (Cualquier tipo)", value=st.session_state.datos_paciente.get('ant_fam_cancer', False), disabled=disabled, key=f"af_cancer_{reset_count}")
        with c2:
            st.session_state.datos_paciente['ant_fam_diabetes'] = st.checkbox("Diabetes Mellitus", value=st.session_state.datos_paciente.get('ant_fam_diabetes', False), disabled=disabled, key=f"af_diabetes_{reset_count}")
            st.session_state.datos_paciente['ant_fam_genetica'] = st.text_input("Otros / Genéticos", value=st.session_state.datos_paciente.get('ant_fam_genetica', ''), placeholder="Ej. Huntington, Fibrosis Quística...", disabled=disabled, key=f"af_gen_{reset_count}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/family_history.py</div>', unsafe_allow_html=True)
