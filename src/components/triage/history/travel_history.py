import streamlit as st

def render_travel_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Viajes y Exposición en un acordeón.
    """
    with st.expander("✈️ Viajes y Exposición", expanded=False):
        from src.db.repositories.clinical_options import get_clinical_options_repository
        repo = get_clinical_options_repository()
        
        st.session_state.datos_paciente['travel_recent'] = st.text_input("🌍 Viajes recientes (últimos 3 meses)", value=st.session_state.datos_paciente.get('travel_recent', ''), placeholder="País/Zona, Fecha...", disabled=disabled, key=f"trav_rec_{reset_count}", help="Estancias en el extranjero o zonas endémicas")
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            has_animals = st.checkbox("🐾 Contacto con animales exóticos/granja", value=st.session_state.datos_paciente.get('exp_animales', False), disabled=disabled, key=f"exp_anim_{reset_count}", help="Exposición a vectores zoonóticos")
            st.session_state.datos_paciente['exp_animales'] = has_animals
            if has_animals:
                opt_animals = repo.get_options("animal_contact")
                
                st.session_state.datos_paciente['exp_animales_det'] = st.multiselect(
                    "📝 Tipo Animal / Contacto",
                    options=[opt.label for opt in opt_animals],
                    default=st.session_state.datos_paciente.get('exp_animales_det', []) if isinstance(st.session_state.datos_paciente.get('exp_animales_det'), list) else [],
                    disabled=disabled, key=f"exp_anim_det_{reset_count}",
                    help="Especie y tipo de contacto"
                )
                st.session_state.datos_paciente['exp_animales_otros'] = st.text_input("Otros Animales", value=st.session_state.datos_paciente.get('exp_animales_otros', ''), key=f"exp_anim_oth_{reset_count}", disabled=disabled)

        with c_exp2:
            opt_occ = repo.get_options("occupational_risk")
            st.session_state.datos_paciente['exp_ocupacional'] = st.multiselect(
                "☣️ Riesgo Ocupacional",
                options=[opt.label for opt in opt_occ],
                default=st.session_state.datos_paciente.get('exp_ocupacional', []) if isinstance(st.session_state.datos_paciente.get('exp_ocupacional'), list) else [],
                disabled=disabled, key=f"exp_occ_{reset_count}",
                help="Exposición laboral a tóxicos o patógenos"
            )
            st.session_state.datos_paciente['exp_ocupacional_otros'] = st.text_input("Otro Riesgo Ocupacional", value=st.session_state.datos_paciente.get('exp_ocupacional_otros', ''), key=f"exp_occ_oth_{reset_count}", disabled=disabled)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/travel_history.py</div>', unsafe_allow_html=True)
