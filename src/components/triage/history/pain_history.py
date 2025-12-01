import streamlit as st

def render_pain_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Historial de Dolor y Opioides en un acordeón.
    """
    with st.expander("💊 Historial de Dolor y Opioides", expanded=False):
        c_pain1, c_pain2 = st.columns(2)
        with c_pain1:
            has_chronic_pain = st.checkbox("Dolor Crónico Diagnosticado", value=st.session_state.datos_paciente.get('pain_cronico', False), disabled=disabled, key=f"pain_chr_{reset_count}")
            st.session_state.datos_paciente['pain_cronico'] = has_chronic_pain
            if has_chronic_pain:
                st.session_state.datos_paciente['pain_cronico_det'] = st.text_input("Localización / Origen", value=st.session_state.datos_paciente.get('pain_cronico_det', ''), key=f"pain_chr_det_{reset_count}", disabled=disabled)

        with c_pain2:
            st.session_state.datos_paciente['pain_opioides'] = st.checkbox("Uso crónico de Opioides", value=st.session_state.datos_paciente.get('pain_opioides', False), disabled=disabled, key=f"pain_op_{reset_count}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/pain_history.py</div>', unsafe_allow_html=True)
