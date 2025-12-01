import streamlit as st

def render_safety_alerts_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Alertas de Seguridad (Transfusiones, Aislamiento, DNR) en un acordeón.
    """
    with st.expander("⚠️ Alertas de Seguridad y Otros", expanded=False):
        # Transfusiones
        transfusions = st.checkbox(
            "🩸 Transfusiones Previas",
            value=st.session_state.datos_paciente.get('alert_transfusiones', False),
            disabled=disabled, key=f"alert_transf_{reset_count}",
            help="Antecedentes de recepción de hemoderivados"
        )
        st.session_state.datos_paciente['alert_transfusiones'] = transfusions
        
        if transfusions:
            st.session_state.datos_paciente['alert_transfusiones_det'] = st.text_input(
                "📝 Fecha / Reacción",
                value=st.session_state.datos_paciente.get('alert_transfusiones_det', ''),
                disabled=disabled, key=f"alert_transf_det_{reset_count}",
                help="¿Hubo complicaciones?"
            )

        # MRSA / Multirresistentes
        mrsa = st.checkbox(
            "🦠 Historial MRSA / Multirresistentes",
            value=st.session_state.datos_paciente.get('alert_mrsa', False),
            disabled=disabled, key=f"alert_mrsa_{reset_count}",
            help="Colonización previa por bacterias multirresistentes"
        )
        st.session_state.datos_paciente['alert_mrsa'] = mrsa
        
        if mrsa:
            st.session_state.datos_paciente['alert_mrsa_det'] = st.text_input(
                "📝 Microorganismo / Ubicación",
                value=st.session_state.datos_paciente.get('alert_mrsa_det', ''),
                disabled=disabled, key=f"alert_mrsa_det_{reset_count}",
                help="Tipo de bacteria y lugar de aislamiento"
            )

        # DNR
        dnr = st.checkbox(
            "🛑 Voluntades Anticipadas / DNR",
            value=st.session_state.datos_paciente.get('alert_dnr', False),
            disabled=disabled, key=f"alert_dnr_{reset_count}",
            help="Orden de No Reanimación Cardiopulmonar"
        )
        st.session_state.datos_paciente['alert_dnr'] = dnr
        
        if dnr:
            st.error("⚠️ ORDEN DE NO REANIMACIÓN")
            st.session_state.datos_paciente['alert_dnr_det'] = st.text_input(
                "📝 Detalles / Documento",
                value=st.session_state.datos_paciente.get('alert_dnr_det', ''),
                disabled=disabled, key=f"alert_dnr_det_{reset_count}",
                help="Referencia al documento legal"
            )

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/safety_alerts.py</div>', unsafe_allow_html=True)
