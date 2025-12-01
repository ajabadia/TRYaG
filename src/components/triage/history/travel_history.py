import streamlit as st

def render_travel_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Viajes y Exposición en un acordeón.
    """
    with st.expander("✈️ Viajes y Exposición", expanded=False):
        st.session_state.datos_paciente['travel_recent'] = st.text_input("Viajes recientes (últimos 3 meses)", value=st.session_state.datos_paciente.get('travel_recent', ''), placeholder="País/Zona, Fecha...", disabled=disabled, key=f"trav_rec_{reset_count}")
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            has_animals = st.checkbox("Contacto con animales exóticos/granja", value=st.session_state.datos_paciente.get('exp_animales', False), disabled=disabled, key=f"exp_anim_{reset_count}")
            st.session_state.datos_paciente['exp_animales'] = has_animals
            if has_animals:
                st.session_state.datos_paciente['exp_animales_det'] = st.text_input("Tipo Animal / Contacto", value=st.session_state.datos_paciente.get('exp_animales_det', ''), key=f"exp_anim_det_{reset_count}", disabled=disabled)

        with c_exp2:
            st.session_state.datos_paciente['exp_ocupacional'] = st.text_input("Riesgo Ocupacional", value=st.session_state.datos_paciente.get('exp_ocupacional', ''), placeholder="Químicos, Sanitario...", disabled=disabled, key=f"exp_occ_{reset_count}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/travel_history.py</div>', unsafe_allow_html=True)
