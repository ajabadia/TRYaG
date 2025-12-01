import streamlit as st

def render_clinical_context_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Contexto Clínico en un acordeón.
    """
    with st.expander("🏥 Contexto Clínico", expanded=False):
        col_ctx1, col_ctx2 = st.columns(2)
        with col_ctx1:
            # Auto-detectar geriátrico si edad >= 65
            edad_actual = st.session_state.datos_paciente.get('edad', 0)
            is_geriatric_age = edad_actual >= 65
            
            # Si detectamos que es >= 65, actualizamos el estado ANTES de renderizar el checkbox
            if is_geriatric_age:
                 st.session_state.datos_paciente['criterio_geriatrico'] = True
            
            # Recuperar valor (ahora actualizado si aplica)
            val_geriatric = st.session_state.datos_paciente.get('criterio_geriatrico', False)
            
            criterio_geriatrico = st.checkbox("👴 Criterio Geriátrico (Edad ≥ 65)", value=val_geriatric, disabled=disabled, key=f"ctx_geriatric_{reset_count}", help="Marca si el paciente tiene 65 años o más")
            st.session_state.datos_paciente['criterio_geriatrico'] = criterio_geriatrico
            
        with col_ctx2:
            # Lógica Inmunodeprimido / Oncológico
            st.markdown("**Estado Inmunológico / Oncológico**")
            c_imm, c_onc = st.columns(2)
            with c_imm:
                is_immuno = st.checkbox("🛡️ Inmunodeprimido", value=st.session_state.datos_paciente.get('ctx_is_immuno', False), disabled=disabled, key=f"ctx_is_imm_{reset_count}", help="VIH, Trasplantes, Inmunodeficiencias...")
                st.session_state.datos_paciente['ctx_is_immuno'] = is_immuno
            with c_onc:
                is_onco = st.checkbox("🎗️ Oncológico", value=st.session_state.datos_paciente.get('ctx_is_onco', False), disabled=disabled, key=f"ctx_is_onc_{reset_count}", help="Cáncer activo o en tratamiento")
                st.session_state.datos_paciente['ctx_is_onco'] = is_onco

            # Cargar opciones si alguno está marcado
            if is_immuno or is_onco:
                from db.repositories.clinical_options import get_clinical_options_repository
                repo = get_clinical_options_repository()
                all_opts = repo.get_options("immuno_onco")
                
                # Filtrar opciones según selección
                filtered_opts = []
                for opt in all_opts:
                    meta = opt.meta or {}
                    if (is_immuno and meta.get('is_immuno')) or (is_onco and meta.get('is_onco')):
                        filtered_opts.append(opt.label)
                
                # Eliminar duplicados y ordenar
                filtered_opts = sorted(list(set(filtered_opts)))

                st.session_state.datos_paciente['criterio_inmunodeprimido_det'] = st.multiselect(
                    "Condiciones Específicas",
                    options=filtered_opts,
                    default=[x for x in st.session_state.datos_paciente.get('criterio_inmunodeprimido_det', []) if x in filtered_opts] if isinstance(st.session_state.datos_paciente.get('criterio_inmunodeprimido_det'), list) else [],
                    disabled=disabled,
                    key=f"ctx_immuno_list_{reset_count}"
                )
                
                st.session_state.datos_paciente['criterio_inmunodeprimido_otros'] = st.text_input(
                    "Otros / Detalles Adicionales",
                    value=st.session_state.datos_paciente.get('criterio_inmunodeprimido_otros', ''),
                    disabled=disabled,
                    key=f"ctx_immuno_other_{reset_count}"
                )
                
                # Mantener compatibilidad con flag booleano antiguo para lógica interna
                st.session_state.datos_paciente['criterio_inmunodeprimido'] = True
            else:
                st.session_state.datos_paciente['criterio_inmunodeprimido'] = False
                st.session_state.datos_paciente['criterio_inmunodeprimido_det'] = []

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/clinical_context.py</div>', unsafe_allow_html=True)
