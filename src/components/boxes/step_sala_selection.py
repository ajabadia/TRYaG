# path: src/components/boxes/step_sala_selection.py
# Creado: 2025-11-24
"""
Paso 1 de Gestión de Boxes: Selección de Sala de Atención (Consulta/Box).
"""
import streamlit as st
from services.room_service import obtener_salas_por_tipo
from components.common.room_card import render_room_grid

def render_step_sala_selection() -> bool:
    """
    Renderiza la selección de sala de atención para boxes/consultas.
    
    Returns:
        bool: True si hay sala seleccionada, False en caso contrario.
    """
    st.subheader("1️⃣ Selección de Consulta / Box")
    st.info("💡 Indique en qué consulta o box se encuentra trabajando.")

    # Obtener salas de tipo 'box'
    salas = obtener_salas_por_tipo("box")
    
    # Filtrar solo salas de atención (donde está el médico)
    salas_atencion = [s for s in salas if s.get('subtipo') == 'atencion']
    
    if not salas_atencion:
        st.error("❌ No hay consultas ni boxes de atención configurados.")
        return False

    # Inicializar estado si no existe
    if 'boxes_room_code' not in st.session_state:
        st.session_state.boxes_room_code = None

    # Renderizar grid de salas
    selected = render_room_grid(
        salas=salas_atencion,
        selected_code=st.session_state.boxes_room_code,
        button_key_prefix="boxes_sala"
    )
    
    # Actualizar estado si se seleccionó una sala
    if selected:
        st.session_state.boxes_room_code = selected
        st.rerun()

    # Mostrar sala seleccionada
    if st.session_state.boxes_room_code:
        st.divider()
        st.info(f"📍 Trabajando en: **{st.session_state.boxes_room_code}**")
        return True
    
    return False
