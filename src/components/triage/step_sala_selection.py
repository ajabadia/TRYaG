# path: src/components/triage/step_sala_selection.py
# Creado: 2025-11-24
# Última modificación: 2025-11-24
"""
Paso 1 del Asistente de Triaje: Selección de Sala.
"""
import streamlit as st
from services.room_service import obtener_salas_por_tipo
from components.common.room_card import render_room_list

def render_step_sala_selection() -> bool:
    """
    Renderiza la selección de sala de triaje.
    
    Returns:
        bool: True si hay sala seleccionada, False en caso contrario.
    """
    st.subheader("1️⃣ Selección de Sala de Triaje")
    st.info("💡 Indique en qué sala se encuentra realizando el triaje.")

    salas = obtener_salas_por_tipo("triaje")
    # Filtrar solo salas de atención (donde está el médico)
    salas = [s for s in salas if s.get('subtipo') == 'atencion']
    
    if not salas:
        st.error("❌ No hay salas de atención de triaje configuradas.")
        return False

    # Inicializar estado si no existe
    if 'triage_room_code' not in st.session_state:
        st.session_state.triage_room_code = None

    # Mostrar sala seleccionada (Ahora arriba)
    if st.session_state.triage_room_code:
        col_info, col_change = st.columns([3, 1])
        with col_info:
            st.info(f"📍 Sala seleccionada: **{st.session_state.triage_room_code}**")
        with col_change:
            if st.button("🔄 Cambiar Sala", key="change_triage_room"):
                st.session_state.triage_room_code = None
                st.rerun()
        return True

    # Renderizar lista de salas usando componente reutilizable
    selected = render_room_list(
        salas=salas,
        selected_code=st.session_state.triage_room_code,
        button_key_prefix="triage_sala"
    )
    
    # Actualizar estado si se seleccionó una sala
    if selected:
        st.session_state.triage_room_code = selected
        st.rerun()
    
    return False
