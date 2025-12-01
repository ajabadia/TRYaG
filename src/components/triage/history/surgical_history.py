import streamlit as st

def render_surgical_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Antecedentes Quirúrgicos en un acordeón.
    """
    with st.expander("🔪 Antecedentes Quirúrgicos", expanded=False):
        st.session_state.datos_paciente['ant_quirurgicos_txt'] = st.text_area(
            "🏥 Cirugías Previas (Tipo y Año)",
            value=st.session_state.datos_paciente.get('ant_quirurgicos_txt', ''),
            placeholder="Ej. Apendicectomía (2010), Prótesis Cadera Izq (2022)...",
            height=68, disabled=disabled, key=f"ant_surg_{reset_count}",
            help="Liste las operaciones realizadas y fecha aproximada"
        )
        
        c1, c2 = st.columns(2)
        with c1:
            anesthesia_comp = st.checkbox(
                "⚠️ Complicaciones Anestésicas Previas",
                value=st.session_state.datos_paciente.get('ant_anestesia', False),
                disabled=disabled, key=f"ant_anes_{reset_count}",
                help="Reacciones adversas a la anestesia en el pasado"
            )
            st.session_state.datos_paciente['ant_anestesia'] = anesthesia_comp
            
            if anesthesia_comp:
                st.session_state.datos_paciente['ant_anestesia_det'] = st.text_input(
                    "📝 ¿Qué complicaciones?",
                    value=st.session_state.datos_paciente.get('ant_anestesia_det', ''),
                    disabled=disabled, key=f"ant_anes_det_{reset_count}",
                    help="Describa la reacción anestésica"
                )
        
        with c2:
            implants = st.checkbox(
                "🔩 Portador de Implantes / Dispositivos",
                value=st.session_state.datos_paciente.get('ant_implantes', False),
                disabled=disabled, key=f"ant_imp_{reset_count}",
                help="Marcapasos, prótesis metálicas, válvulas..."
            )
            st.session_state.datos_paciente['ant_implantes'] = implants
            
            if implants:
                from src.db.repositories.clinical_options import get_clinical_options_repository
                repo = get_clinical_options_repository()
                opt_implants = repo.get_options("implant")
                
                st.session_state.datos_paciente['ant_implantes_det'] = st.multiselect(
                    "ℹ️ Dispositivos Portados",
                    options=[opt.label for opt in opt_implants],
                    default=st.session_state.datos_paciente.get('ant_implantes_det', []) if isinstance(st.session_state.datos_paciente.get('ant_implantes_det'), list) else [],
                    disabled=disabled, key=f"ant_imp_det_{reset_count}",
                    help="Seleccione los dispositivos que porta el paciente"
                )
                
                st.session_state.datos_paciente['ant_implantes_otros'] = st.text_input(
                    "Otros Dispositivos / Detalles",
                    value=st.session_state.datos_paciente.get('ant_implantes_otros', ''),
                    disabled=disabled, key=f"ant_imp_other_{reset_count}"
                )

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/surgical_history.py</div>', unsafe_allow_html=True)
