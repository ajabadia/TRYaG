import streamlit as st

def render_obgyn_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Antecedentes Gineco-Obstétricos en un acordeón.
    """
    with st.expander("🤰 Gineco-Obstetricia", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.datos_paciente['ant_go_fur'] = st.date_input(
                "📅 Fecha Última Regla (FUR)",
                value=st.session_state.datos_paciente.get('ant_go_fur', None),
                disabled=disabled, key=f"ant_go_fur_{reset_count}",
                help="Fecha del primer día de la última menstruación"
            )
        
        with c2:
            possible_pregnancy = st.checkbox(
                "🤰 Posible Embarazo",
                value=st.session_state.datos_paciente.get('ant_go_embarazo', False),
                disabled=disabled, key=f"ant_go_preg_{reset_count}",
                help="Marque si existe posibilidad de embarazo actual"
            )
            st.session_state.datos_paciente['ant_go_embarazo'] = possible_pregnancy
            
            if possible_pregnancy:
                st.session_state.datos_paciente['ant_go_detalles'] = st.text_input(
                    "📝 Semanas / Detalles",
                    value=st.session_state.datos_paciente.get('ant_go_detalles', ''),
                    disabled=disabled, key=f"ant_go_det_{reset_count}",
                    help="Semanas de gestación (G) y partos previos (P)"
                )

    st.markdown('<div class="debug-footer">src/components/triage/history/obgyn_history.py</div>', unsafe_allow_html=True)
