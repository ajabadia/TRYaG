# path: src/components/common/stepper.py
# Creado: 2025-11-24
"""
Componente reutilizable para visualizar un stepper vertical.
Versión simplificada usando Markdown nativo para evitar problemas de renderizado HTML.
"""
import streamlit as st

def render_vertical_stepper(steps: list[str], current_step: int):
    """
    Renderiza un indicador de progreso vertical usando Markdown nativo.

    Args:
        steps: Lista de títulos de los pasos.
        current_step: Índice del paso actual (0-indexed).
    """
    st.markdown("### Pasos")
    
    for i, step_label in enumerate(steps):
        if i < current_step:
            # Paso completado
            st.markdown(f":material/check_circle: **{step_label}**")
        elif i == current_step:
            # Paso actual (destacado)
            st.info(f"**{i+1}. {step_label}**", icon="👉")
        else:
            # Paso pendiente
            st.markdown(f":material/radio_button_unchecked: {step_label}")
            
    st.divider()
