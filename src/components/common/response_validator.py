import streamlit as st

def render_response_validator(key_prefix: str, label: str = "Calificación de la Respuesta"):
    """
    Componente reutilizable para validar respuestas de la IA.
    Maneja el estado de "Mano Arriba" / "Mano Abajo" y solicita explicación si es negativa.
    
    Args:
        key_prefix (str): Prefijo único para las claves de sesión.
        label (str): Título de la sección.
        
    Returns:
        dict: {
            "status": "valid" | "pending",
            "rating": "positive" | "negative" | None,
            "reason": str (opcional)
        }
    """
    
    # Session State Keys
    k_rating = f"{key_prefix}_rating"
    k_reason = f"{key_prefix}_reason"
    k_submitted = f"{key_prefix}_submitted"
    
    # Initialize State
    if k_rating not in st.session_state:
        st.session_state[k_rating] = None
    if k_reason not in st.session_state:
        st.session_state[k_reason] = ""
    if k_submitted not in st.session_state:
        st.session_state[k_submitted] = False

    st.markdown(f"##### {label}")
    
    # Si ya se envió/validó, mostrar resultado estático (o permitir editar)
    if st.session_state[k_submitted]:
        rating = st.session_state[k_rating]
        reason = st.session_state[k_reason]
        
        if rating == "positive":
            st.success("✅ Calificación: **Correcto**")
        else:
            st.error(f"❌ Calificación: **Incorrecto**")
            if reason:
                st.caption(f"Motivo: {reason}")
            
        if st.button("Cambiar calificación", key=f"{key_prefix}_reset"):
            st.session_state[k_submitted] = False
            st.session_state[k_rating] = None
            st.session_state[k_reason] = ""
            st.rerun()
            
        return {
            "status": "valid", 
            "rating": rating, 
            "reason": reason
        }

    # UI de Selección - SOLO mostrar si NO hay una calificación pendiente de confirmación (negativo sin enviar)
    # Si ya se eligió negativo, pasamos a modo "Formulario de Detalle"
    current_rating = st.session_state[k_rating]
    
    if current_rating == "negative":
        st.warning("Por favor, indique el motivo para mejorar el sistema.")
        reason_input = st.text_area("Motivo de la corrección:", value=st.session_state[k_reason], key=f"{key_prefix}_txt_reason")
        
        # Actualizar estado del texto
        st.session_state[k_reason] = reason_input
        
        c_confirm, c_cancel = st.columns([1, 1])
        with c_confirm:
            if st.button("✅ Confirmar Calificación", key=f"{key_prefix}_submit_neg", type="primary", use_container_width=True):
                if not reason_input.strip():
                    st.error("El motivo es obligatorio.")
                else:
                    st.session_state[k_submitted] = True
                    st.rerun()
        
        with c_cancel:
            if st.button("❌ Cancelar / Volver", key=f"{key_prefix}_cancel_neg", use_container_width=True):
                st.session_state[k_rating] = None
                st.session_state[k_reason] = ""
                st.rerun()

    else:
        # Modo Selección Inicial (Neutral o Positivo -> AutoSubmit)
        col_up, col_down = st.columns(2)
        
        with col_up:
            if st.button("👍 Correcto", key=f"{key_prefix}_btn_up", type="secondary", use_container_width=True):
                st.session_state[k_rating] = "positive"
                st.session_state[k_reason] = ""
                # Auto-submit para positivo
                st.session_state[k_submitted] = True
                st.rerun()

        with col_down:
            if st.button("👎 Incorrecto", key=f"{key_prefix}_btn_down", type="secondary", use_container_width=True):
                st.session_state[k_rating] = "negative"
                st.rerun()
    
    return {
        "status": "pending",
        "rating": current_rating,
        "reason": st.session_state[k_reason]
    }
