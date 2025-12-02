import streamlit as st

def render_hospitalization_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Hospitalizaciones y Legal en un acordeón.
    """
    with st.expander("🏥 Hospitalizaciones y Legal", expanded=False):
        st.session_state.datos_paciente['hosp_recent'] = st.text_area(
            "🏥 Ingresos Hospitalarios Recientes (3-6 meses)",
            value=st.session_state.datos_paciente.get('hosp_recent', ''),
            height=68, disabled=disabled, key=f"hosp_rec_{reset_count}",
            help="Motivo y fecha de ingresos recientes"
        )
        
        c_leg1, c_leg2 = st.columns(2)
        with c_leg1:
            st.session_state.datos_paciente['leg_tutor'] = st.text_input("⚖️ Tutor Legal / Apoderado", value=st.session_state.datos_paciente.get('leg_tutor', ''), placeholder="Nombre y Teléfono", disabled=disabled, key=f"leg_tut_{reset_count}", help="Persona con autoridad legal para decidir")
        with c_leg2:
            st.session_state.datos_paciente['leg_cuidador'] = st.text_input("🤝 Cuidador Principal", value=st.session_state.datos_paciente.get('leg_cuidador', ''), placeholder="Nombre y Relación", disabled=disabled, key=f"leg_care_{reset_count}", help="Persona que asiste en el día a día")

        # New section for legal issues and advanced directives
        st.markdown("---") # Separator for clarity
        c_legal_issues1, c_legal_issues2 = st.columns(2)
        with c_legal_issues1:
            has_legal = st.checkbox("👮 Problemas Legales / Judiciales", value=st.session_state.datos_paciente.get('hosp_legal', False), disabled=disabled, key=f"hosp_leg_{reset_count}", help="Custodia policial, orden judicial...")
            st.session_state.datos_paciente['hosp_legal'] = has_legal
            if has_legal:
                st.session_state.datos_paciente['hosp_legal_det'] = st.text_input("📝 Detalles Legales", value=st.session_state.datos_paciente.get('hosp_legal_det', ''), key=f"hosp_leg_det_{reset_count}", disabled=disabled, help="Especifique la situación legal")
        with c_legal_issues2:
            # Sync with safety_alerts.py
            has_dnr = st.checkbox("📜 Documento Voluntades Anticipadas / DNR", value=st.session_state.datos_paciente.get('alert_dnr', False), disabled=disabled, key=f"hosp_vol_{reset_count}", help="Existe registro de instrucciones previas")
            st.session_state.datos_paciente['alert_dnr'] = has_dnr
            
            if has_dnr:
                st.warning("⚠️ VOLUNTADES ANTICIPADAS / DNR ACTIVO")
                st.session_state.datos_paciente['alert_dnr_det'] = st.text_input(
                    "📝 Detalles / Documento",
                    value=st.session_state.datos_paciente.get('alert_dnr_det', ''),
                    disabled=disabled, key=f"hosp_vol_det_{reset_count}",
                    help="Referencia al documento legal"
                )

    st.markdown('<div class="debug-footer">src/components/triage/history/hospitalization_history.py</div>', unsafe_allow_html=True)
