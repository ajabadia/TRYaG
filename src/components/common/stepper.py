# path: src/components/common/stepper.py
# Creado: 2025-11-24
"""
Componente reutilizable para visualizar un stepper vertical.
Versión simplificada usando Markdown nativo para evitar problemas de renderizado HTML.
"""
import streamlit as st

def render_horizontal_stepper(steps: list[str], current_step: int):
    """
    Renderiza un indicador de progreso horizontal estilo Angular Material.
    
    Args:
        steps: Lista de títulos de los pasos.
        current_step: Índice del paso actual (0-indexed).
    """
    # Crear columnas para cada paso
    cols = st.columns(len(steps))
    
    for i, (col, step_label) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                # Paso completado (Círculo verde con check)
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <span style="
                            display: inline-block;
                            width: 30px;
                            height: 30px;
                            border-radius: 50%;
                            background-color: #4CAF50;
                            color: white;
                            text-align: center;
                            line-height: 30px;
                            font-weight: bold;
                            margin-bottom: 5px;">
                            ✓
                        </span>
                        <br>
                        <small style="color: #4CAF50; font-weight: bold;">{step_label}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif i == current_step:
                # Paso actual (Círculo azul activo)
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <span style="
                            display: inline-block;
                            width: 30px;
                            height: 30px;
                            border-radius: 50%;
                            background-color: #2196F3;
                            color: white;
                            text-align: center;
                            line-height: 30px;
                            font-weight: bold;
                            margin-bottom: 5px;
                            box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);">
                            {i + 1}
                        </span>
                        <br>
                        <strong style="color: #2196F3;">{step_label}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                # Paso pendiente (Círculo gris)
                st.markdown(
                    f"""
                    <div style="text-align: center; opacity: 0.6;">
                        <span style="
                            display: inline-block;
                            width: 30px;
                            height: 30px;
                            border-radius: 50%;
                            background-color: #e0e0e0;
                            color: #757575;
                            text-align: center;
                            line-height: 30px;
                            font-weight: bold;
                            margin-bottom: 5px;">
                            {i + 1}
                        </span>
                        <br>
                        <small style="color: #757575;">{step_label}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    # Línea separadora sutil
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border: 0; border-top: 1px solid #eee;'/>", unsafe_allow_html=True)
