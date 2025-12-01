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
            val_immuno = st.session_state.datos_paciente.get('criterio_inmunodeprimido', False)
            criterio_inmunodeprimido = st.checkbox("🛡️ Inmunodeprimido / Oncológico", value=val_immuno, disabled=disabled, key=f"ctx_immuno_{reset_count}", help="Paciente con sistema inmune comprometido (Cáncer, VIH, Trasplante...)")
            st.session_state.datos_paciente['criterio_inmunodeprimido'] = criterio_inmunodeprimido
            
            if criterio_inmunodeprimido:
                st.session_state.datos_paciente['criterio_inmunodeprimido_det'] = st.text_input("📝 Detalles Inmunosupresión", value=st.session_state.datos_paciente.get('criterio_inmunodeprimido_det', ''), key=f"ctx_immuno_det_{reset_count}", disabled=disabled, help="Especifique la condición (ej: Quimioterapia activa)")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/clinical_context.py</div>', unsafe_allow_html=True)
