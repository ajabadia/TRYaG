import streamlit as st

def render_forensic_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Forense, Cultural y Escalas en un acordeón.
    """
    with st.expander("⚖️ Forense, Cultural y Escalas", expanded=False):
        st.markdown("**Protocolo Forense**")
        c_for1, c_for2 = st.columns(2)
        with c_for1:
            has_violence = st.checkbox("⚠️ Sospecha Violencia (Género/Doméstica)", value=st.session_state.datos_paciente.get('for_violencia', False), disabled=disabled, key=f"for_viol_{reset_count}", help="Signos físicos o conductuales de maltrato")
            st.session_state.datos_paciente['for_violencia'] = has_violence
            if has_violence:
                st.error("ACTIVAR PROTOCOLO VIOLENCIA")
                st.session_state.datos_paciente['for_violencia_det'] = st.text_input("📝 Detalles / Tipo Violencia", value=st.session_state.datos_paciente.get('for_violencia_det', ''), key=f"for_viol_det_{reset_count}", disabled=disabled, help="Describa los hallazgos o sospechas")

        with c_for2:
            st.session_state.datos_paciente['for_cultural'] = st.text_input("🌍 Consideraciones Culturales/Religiosas", value=st.session_state.datos_paciente.get('for_cultural', ''), disabled=disabled, key=f"for_cult_{reset_count}", help="Barreras idiomáticas, costumbres...")
        
        st.divider()
        st.markdown("**Cultural y Espiritual**")
        st.session_state.datos_paciente['cult_religion'] = st.text_input("🛐 Preferencias Religiosas/Culturales", value=st.session_state.datos_paciente.get('cult_religion', ''), placeholder="Objeción a transfusiones, dieta...", disabled=disabled, key=f"cult_rel_{reset_count}", help="Creencias que afecten al tratamiento")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/forensic_history.py</div>', unsafe_allow_html=True)
