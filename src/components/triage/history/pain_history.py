import streamlit as st

def render_pain_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Historial de Dolor y Opioides en un acordeón.
    """
    with st.expander("💊 Historial de Dolor y Opioides", expanded=False):
        c_pain1, c_pain2 = st.columns(2)
        with c_pain1:
            st.session_state.datos_paciente['pain_chronic'] = st.checkbox("Dolor Crónico Diagnosticado", value=st.session_state.datos_paciente.get('pain_chronic', False), disabled=disabled, key=f"pain_chr_{reset_count}")
        with c_pain2:
            st.session_state.datos_paciente['pain_opioids'] = st.checkbox("Uso crónico de Opioides (Tolerancia)", value=st.session_state.datos_paciente.get('pain_opioids', False), disabled=disabled, key=f"pain_opi_{reset_count}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/pain_history.py</div>', unsafe_allow_html=True)
