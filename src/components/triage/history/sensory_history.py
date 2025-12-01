import streamlit as st

def render_sensory_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Déficits Sensoriales y Ayudas en un acordeón.
    """
    with st.expander("👂 Déficits Sensoriales y Ayudas", expanded=False):
        from db.repositories.clinical_options import get_clinical_options_repository
        repo = get_clinical_options_repository()
        
        c_sen1, c_sen2 = st.columns(2)
        with c_sen1:
            has_auditory = st.checkbox("🦻 Déficit Auditivo (Usa audífonos)", value=st.session_state.datos_paciente.get('sens_auditivo', False), disabled=disabled, key=f"sens_aud_{reset_count}", help="Hipoacusia o sordera")
            st.session_state.datos_paciente['sens_auditivo'] = has_auditory
            if has_auditory:
                opt_auditory = repo.get_options("sensory_auditory")
                st.session_state.datos_paciente['sens_auditivo_det'] = st.multiselect(
                    "Detalles Auditivo",
                    options=[opt.label for opt in opt_auditory],
                    default=st.session_state.datos_paciente.get('sens_auditivo_det', []) if isinstance(st.session_state.datos_paciente.get('sens_auditivo_det'), list) else [],
                    disabled=disabled, key=f"sens_aud_det_{reset_count}",
                    help="Grado de afectación"
                )

            has_visual = st.checkbox("👓 Déficit Visual (Usa gafas/lentes)", value=st.session_state.datos_paciente.get('sens_visual', False), disabled=disabled, key=f"sens_vis_{reset_count}", help="Ceguera parcial o total")
            st.session_state.datos_paciente['sens_visual'] = has_visual
            if has_visual:
                opt_visual = repo.get_options("sensory_visual")
                st.session_state.datos_paciente['sens_visual_det'] = st.multiselect(
                    "Detalles Visual",
                    options=[opt.label for opt in opt_visual],
                    default=st.session_state.datos_paciente.get('sens_visual_det', []) if isinstance(st.session_state.datos_paciente.get('sens_visual_det'), list) else [],
                    disabled=disabled, key=f"sens_vis_det_{reset_count}",
                    help="Grado de afectación"
                )

        with c_sen2:
            opt_lang = repo.get_options("sensory_language")
            st.session_state.datos_paciente['sens_idioma'] = st.multiselect(
                "🗣️ Idioma Principal / Necesidad Intérprete",
                options=[opt.label for opt in opt_lang],
                default=st.session_state.datos_paciente.get('sens_idioma', []) if isinstance(st.session_state.datos_paciente.get('sens_idioma'), list) else [],
                disabled=disabled, key=f"sens_lang_{reset_count}",
                help="Lengua materna y si requiere traducción"
            )
            st.session_state.datos_paciente['sens_idioma_otros'] = st.text_input("Otro Idioma", value=st.session_state.datos_paciente.get('sens_idioma_otros', ''), key=f"sens_lang_oth_{reset_count}", disabled=disabled)

            opt_pros = repo.get_options("sensory_prosthesis")
            st.session_state.datos_paciente['sens_protesis'] = st.multiselect(
                "🦾 Prótesis / Órtesis",
                options=[opt.label for opt in opt_pros],
                default=st.session_state.datos_paciente.get('sens_protesis', []) if isinstance(st.session_state.datos_paciente.get('sens_protesis'), list) else [],
                disabled=disabled, key=f"sens_prot_{reset_count}",
                help="Dispositivos de ayuda física"
            )
            st.session_state.datos_paciente['sens_protesis_otros'] = st.text_input("Otras Prótesis", value=st.session_state.datos_paciente.get('sens_protesis_otros', ''), key=f"sens_prot_oth_{reset_count}", disabled=disabled)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/sensory_history.py</div>', unsafe_allow_html=True)
