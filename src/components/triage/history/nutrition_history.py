import streamlit as st

def render_nutrition_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Nutrición y Dieta en un acordeón.
    """
    with st.expander("🍎 Nutrición y Dieta", expanded=False):
        c_nut1, c_nut2 = st.columns(2)
        with c_nut1:
            st.session_state.datos_paciente['nut_dieta'] = st.selectbox("Tipo de Dieta Habitual", ["Normal", "Diabética", "Hiposódica", "Vegetariana/Vegana", "Triturada", "Otra"], index=0, disabled=disabled, key=f"nut_diet_{reset_count}")
            st.session_state.datos_paciente['nut_disfagia'] = st.checkbox("⚠️ Disfagia (Dificultad para tragar)", value=st.session_state.datos_paciente.get('nut_disfagia', False), disabled=disabled, key=f"nut_dys_{reset_count}")
        with c_nut2:
            st.session_state.datos_paciente['nut_peso'] = st.checkbox("Pérdida de peso no intencionada (>5% en 3 meses)", value=st.session_state.datos_paciente.get('nut_peso', False), disabled=disabled, key=f"nut_weight_{reset_count}")
            st.session_state.datos_paciente['nut_alergias_alim'] = st.text_input("Alergias/Intolerancias Alimentarias", value=st.session_state.datos_paciente.get('nut_alergias_alim', ''), disabled=disabled, key=f"nut_alg_{reset_count}")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/nutrition_history.py</div>', unsafe_allow_html=True)
