import streamlit as st

def render_forensic_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Forense, Cultural y Escalas en un acordeón.
    """
    with st.expander("⚖️ Forense, Cultural y Escalas", expanded=False):
        st.markdown("**Protocolo Forense**")
        c_for1, c_for2 = st.columns(2)
        with c_for1:
            st.session_state.datos_paciente['for_trauma'] = st.checkbox("Trauma: Discrepancia relato/lesión", value=st.session_state.datos_paciente.get('for_trauma', False), disabled=disabled, key=f"for_trau_{reset_count}")
        with c_for2:
            st.session_state.datos_paciente['for_abuse'] = st.checkbox("Sospecha de Abuso/Negligencia", value=st.session_state.datos_paciente.get('for_abuse', False), disabled=disabled, key=f"for_abus_{reset_count}")
        
        st.divider()
        st.markdown("**Cultural y Espiritual**")
        st.session_state.datos_paciente['cult_religion'] = st.text_input("Preferencias Religiosas/Culturales", value=st.session_state.datos_paciente.get('cult_religion', ''), placeholder="Objeción a transfusiones, dieta...", disabled=disabled, key=f"cult_rel_{reset_count}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/forensic_history.py</div>', unsafe_allow_html=True)
