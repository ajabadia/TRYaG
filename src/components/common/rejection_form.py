# path: src/components/common/rejection_form.py
# Creado: 2025-11-25
"""
Componente reutilizable para el formulario de rechazo de pacientes.
Muestra input de motivo y botones de confirmación/cancelación.
"""
import streamlit as st

def render_rejection_form(
    key_prefix: str,
    on_confirm: callable,
    on_cancel: callable,
    default_reason: str = ""
):
    """
    Renderiza un formulario de rechazo estandarizado.
    
    Args:
        key_prefix: Prefijo para las claves de los widgets.
        on_confirm: Función callback(motivo) a ejecutar al confirmar.
        on_cancel: Función callback() a ejecutar al cancelar.
        default_reason: Motivo por defecto (opcional).
    """
    st.warning("⚠️ Proceso de rechazo de paciente")
    
    motivo_key = f"{key_prefix}_rejection_reason"
    
    # Input de motivo
    motivo = st.text_input(
        "Motivo del rechazo *", 
        value=default_reason,
        key=motivo_key,
        placeholder="Especifique la razón del rechazo..."
    )
    
    col_confirm, col_cancel = st.columns(2)
    
    with col_confirm:
        if st.button("🚨 Confirmar Rechazo", type="primary", use_container_width=True, key=f"{key_prefix}_confirm_btn"):
            if not motivo.strip():
                st.error("❌ Debe especificar un motivo.")
            else:
                on_confirm(motivo)
    
    with col_cancel:
        if st.button("Cancelar", use_container_width=True, key=f"{key_prefix}_cancel_btn"):
            on_cancel()
