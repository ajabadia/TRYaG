import streamlit as st

def render_forensic_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Forense, Cultural y Escalas en un acordeón.
    """
    with st.expander("⚖️ Forense, Cultural y Escalas", expanded=False):
        from db.repositories.clinical_options import get_clinical_options_repository
        repo = get_clinical_options_repository()
        
        st.markdown("**Protocolo Forense**")
        c_for1, c_for2 = st.columns(2)
        with c_for1:
            has_violence = st.checkbox("⚠️ Sospecha Violencia (Género/Doméstica)", value=st.session_state.datos_paciente.get('for_violencia', False), disabled=disabled, key=f"for_viol_{reset_count}", help="Signos físicos o conductuales de maltrato")
            st.session_state.datos_paciente['for_violencia'] = has_violence
            if has_violence:
                st.error("ACTIVAR PROTOCOLO VIOLENCIA")
                opt_violence = repo.get_options("forensic_violence")
                st.session_state.datos_paciente['for_violencia_det'] = st.multiselect(
                    "Tipo Violencia",
                    options=[opt.label for opt in opt_violence],
                    default=st.session_state.datos_paciente.get('for_violencia_det', []) if isinstance(st.session_state.datos_paciente.get('for_violencia_det'), list) else [],
                    disabled=disabled, key=f"for_viol_det_{reset_count}",
                    help="Describa los hallazgos o sospechas"
                )
                st.session_state.datos_paciente['for_violencia_otros'] = st.text_input("Otros Violencia", value=st.session_state.datos_paciente.get('for_violencia_otros', ''), key=f"for_viol_oth_{reset_count}", disabled=disabled)

        with c_for2:
            opt_cult = repo.get_options("forensic_cultural")
            st.session_state.datos_paciente['for_cultural'] = st.multiselect(
                "🌍 Consideraciones Culturales",
                options=[opt.label for opt in opt_cult],
                default=st.session_state.datos_paciente.get('for_cultural', []) if isinstance(st.session_state.datos_paciente.get('for_cultural'), list) else [],
                disabled=disabled, key=f"for_cult_{reset_count}",
                help="Barreras idiomáticas, costumbres..."
            )
            st.session_state.datos_paciente['for_cultural_otros'] = st.text_input("Otras Culturales", value=st.session_state.datos_paciente.get('for_cultural_otros', ''), key=f"for_cult_oth_{reset_count}", disabled=disabled)
        
        st.divider()
        st.markdown("**Cultural y Espiritual**")
        opt_rel = repo.get_options("forensic_religion")
        st.session_state.datos_paciente['cult_religion'] = st.multiselect(
            "🛐 Preferencias Religiosas/Culturales",
            options=[opt.label for opt in opt_rel],
            default=st.session_state.datos_paciente.get('cult_religion', []) if isinstance(st.session_state.datos_paciente.get('cult_religion'), list) else [],
            disabled=disabled, key=f"cult_rel_{reset_count}",
            help="Creencias que afecten al tratamiento"
        )
        st.session_state.datos_paciente['cult_religion_otros'] = st.text_input("Otras Religiosas", value=st.session_state.datos_paciente.get('cult_religion_otros', ''), key=f"cult_rel_oth_{reset_count}", disabled=disabled)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/forensic_history.py</div>', unsafe_allow_html=True)
