import streamlit as st

def render_family_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Antecedentes Familiares en un acordeón.
    """
    with st.expander("👨‍👩‍👧‍👦 Antecedentes Familiares", expanded=False):
        from src.db.repositories.clinical_options import get_clinical_options_repository
        repo = get_clinical_options_repository()
        
        c1, c2 = st.columns(2)
        with c1:
            # Cardiovascular
            has_cardio = st.checkbox("❤️ Enfermedad Cardiovascular (Infarto, Ictus)", value=st.session_state.datos_paciente.get('ant_fam_cardio', False), disabled=disabled, key=f"af_cardio_{reset_count}", help="Antecedentes de IAM, ACV o muerte súbita en familiares de primer grado")
            st.session_state.datos_paciente['ant_fam_cardio'] = has_cardio
            if has_cardio:
                opt_cardio = repo.get_options("family_cardio")
                st.session_state.datos_paciente['ant_fam_cardio_det'] = st.multiselect(
                    "Detalles Cardiovascular",
                    options=[opt.label for opt in opt_cardio],
                    default=st.session_state.datos_paciente.get('ant_fam_cardio_det', []) if isinstance(st.session_state.datos_paciente.get('ant_fam_cardio_det'), list) else [],
                    disabled=disabled, key=f"af_cardio_det_{reset_count}"
                )
                st.session_state.datos_paciente['ant_fam_cardio_otros'] = st.text_input("Otros Cardio", value=st.session_state.datos_paciente.get('ant_fam_cardio_otros', ''), key=f"af_cardio_oth_{reset_count}", disabled=disabled)

            # Cáncer
            has_cancer = st.checkbox("🎗️ Cáncer (Cualquier tipo)", value=st.session_state.datos_paciente.get('ant_fam_cancer', False), disabled=disabled, key=f"af_cancer_{reset_count}", help="Antecedentes oncológicos familiares")
            st.session_state.datos_paciente['ant_fam_cancer'] = has_cancer
            if has_cancer:
                opt_cancer = repo.get_options("family_cancer")
                st.session_state.datos_paciente['ant_fam_cancer_det'] = st.multiselect(
                    "Tipo de Cáncer",
                    options=[opt.label for opt in opt_cancer],
                    default=st.session_state.datos_paciente.get('ant_fam_cancer_det', []) if isinstance(st.session_state.datos_paciente.get('ant_fam_cancer_det'), list) else [],
                    disabled=disabled, key=f"af_cancer_det_{reset_count}"
                )
                st.session_state.datos_paciente['ant_fam_cancer_otros'] = st.text_input("Otros Cáncer / Familiar", value=st.session_state.datos_paciente.get('ant_fam_cancer_otros', ''), key=f"af_cancer_oth_{reset_count}", disabled=disabled)

        with c2:
            # Diabetes
            has_diabetes = st.checkbox("🍬 Diabetes Mellitus", value=st.session_state.datos_paciente.get('ant_fam_diabetes', False), disabled=disabled, key=f"af_diabetes_{reset_count}", help="Antecedentes de diabetes en padres o hermanos")
            st.session_state.datos_paciente['ant_fam_diabetes'] = has_diabetes
            if has_diabetes:
                opt_diabetes = repo.get_options("family_diabetes")
                st.session_state.datos_paciente['ant_fam_diabetes_det'] = st.multiselect(
                    "Tipo Diabetes",
                    options=[opt.label for opt in opt_diabetes],
                    default=st.session_state.datos_paciente.get('ant_fam_diabetes_det', []) if isinstance(st.session_state.datos_paciente.get('ant_fam_diabetes_det'), list) else [],
                    disabled=disabled, key=f"af_diabetes_det_{reset_count}"
                )

            # Genética / Otros
            st.markdown("**🧬 Otros / Genéticos**")
            opt_genetic = repo.get_options("family_genetic")
            st.session_state.datos_paciente['ant_fam_genetica'] = st.multiselect(
                "Enfermedades Hereditarias",
                options=[opt.label for opt in opt_genetic],
                default=st.session_state.datos_paciente.get('ant_fam_genetica', []) if isinstance(st.session_state.datos_paciente.get('ant_fam_genetica'), list) else [],
                disabled=disabled, key=f"af_gen_{reset_count}",
                help="Enfermedades hereditarias conocidas"
            )
            st.session_state.datos_paciente['ant_fam_genetica_otros'] = st.text_input("Otras Genéticas", value=st.session_state.datos_paciente.get('ant_fam_genetica_otros', ''), key=f"af_gen_oth_{reset_count}", disabled=disabled)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/family_history.py</div>', unsafe_allow_html=True)
