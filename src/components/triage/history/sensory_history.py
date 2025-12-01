import streamlit as st

def render_sensory_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Déficits Sensoriales y Ayudas en un acordeón.
    """
    with st.expander("👂 Déficits Sensoriales y Ayudas", expanded=False):
        c_sen1, c_sen2 = st.columns(2)
        with c_sen1:
            has_auditory = st.checkbox("🦻 Déficit Auditivo (Usa audífonos)", value=st.session_state.datos_paciente.get('sens_auditivo', False), disabled=disabled, key=f"sens_aud_{reset_count}", help="Hipoacusia o sordera")
            st.session_state.datos_paciente['sens_auditivo'] = has_auditory
            if has_auditory:
                st.session_state.datos_paciente['sens_auditivo_det'] = st.text_input("📝 Detalles Auditivo", value=st.session_state.datos_paciente.get('sens_auditivo_det', ''), key=f"sens_aud_det_{reset_count}", disabled=disabled, help="Grado de afectación")

            has_visual = st.checkbox("👓 Déficit Visual (Usa gafas/lentes)", value=st.session_state.datos_paciente.get('sens_visual', False), disabled=disabled, key=f"sens_vis_{reset_count}", help="Ceguera parcial o total")
            st.session_state.datos_paciente['sens_visual'] = has_visual
            if has_visual:
                st.session_state.datos_paciente['sens_visual_det'] = st.text_input("📝 Detalles Visual", value=st.session_state.datos_paciente.get('sens_visual_det', ''), key=f"sens_vis_det_{reset_count}", disabled=disabled, help="Grado de afectación")

        with c_sen2:
            st.session_state.datos_paciente['sens_idioma'] = st.text_input("🗣️ Idioma Principal / Necesidad Intérprete", value=st.session_state.datos_paciente.get('sens_idioma', ''), placeholder="Español, Inglés...", disabled=disabled, key=f"sens_lang_{reset_count}", help="Lengua materna y si requiere traducción")
            st.session_state.datos_paciente['sens_protesis'] = st.text_input("🦾 Prótesis / Órtesis", value=st.session_state.datos_paciente.get('sens_protesis', ''), placeholder="Dental, Pierna...", disabled=disabled, key=f"sens_prot_{reset_count}", help="Dispositivos de ayuda física")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/sensory_history.py</div>', unsafe_allow_html=True)
