import streamlit as st

def render_family_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Antecedentes Familiares en un acordeón.
    """
    with st.expander("👨‍👩‍👧‍👦 Antecedentes Familiares", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            # Cardiovascular
            has_cardio = st.checkbox("❤️ Enfermedad Cardiovascular (Infarto, Ictus)", value=st.session_state.datos_paciente.get('ant_fam_cardio', False), disabled=disabled, key=f"af_cardio_{reset_count}", help="Antecedentes de IAM, ACV o muerte súbita en familiares de primer grado")
            st.session_state.datos_paciente['ant_fam_cardio'] = has_cardio
            if has_cardio:
                st.session_state.datos_paciente['ant_fam_cardio_det'] = st.text_input("📝 Detalles Cardiovascular", value=st.session_state.datos_paciente.get('ant_fam_cardio_det', ''), key=f"af_cardio_det_{reset_count}", disabled=disabled, help="Especifique quién y qué patología")

            # Cáncer
            has_cancer = st.checkbox("🎗️ Cáncer (Cualquier tipo)", value=st.session_state.datos_paciente.get('ant_fam_cancer', False), disabled=disabled, key=f"af_cancer_{reset_count}", help="Antecedentes oncológicos familiares")
            st.session_state.datos_paciente['ant_fam_cancer'] = has_cancer
            if has_cancer:
                st.session_state.datos_paciente['ant_fam_cancer_det'] = st.text_input("📝 Tipo/Familiar", value=st.session_state.datos_paciente.get('ant_fam_cancer_det', ''), key=f"af_cancer_det_{reset_count}", disabled=disabled, help="Tipo de cáncer y parentesco")

        with c2:
            # Diabetes
            has_diabetes = st.checkbox("🍬 Diabetes Mellitus", value=st.session_state.datos_paciente.get('ant_fam_diabetes', False), disabled=disabled, key=f"af_diabetes_{reset_count}", help="Antecedentes de diabetes en padres o hermanos")
            st.session_state.datos_paciente['ant_fam_diabetes'] = has_diabetes
            if has_diabetes:
                st.session_state.datos_paciente['ant_fam_diabetes_det'] = st.text_input("📝 Detalles Diabetes", value=st.session_state.datos_paciente.get('ant_fam_diabetes_det', ''), key=f"af_diabetes_det_{reset_count}", disabled=disabled, help="Tipo 1 o 2, insulinodependiente...")

            st.session_state.datos_paciente['ant_fam_genetica'] = st.text_input("🧬 Otros / Genéticos", value=st.session_state.datos_paciente.get('ant_fam_genetica', ''), placeholder="Ej. Huntington, Fibrosis Quística...", disabled=disabled, key=f"af_gen_{reset_count}", help="Enfermedades hereditarias conocidas")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/family_history.py</div>', unsafe_allow_html=True)
