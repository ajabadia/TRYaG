# path: src/components/admission/step_sala_admision.py
# Creado: 2025-11-24
# Última modificación: 2025-11-24
"""
Paso 1 del flujo de admisión: Selección de Sala de Admisión.
"""
import streamlit as st
from services.room_service import obtener_salas_por_tipo
from components.common.room_card import render_room_grid


def render_step_sala_admision() -> bool:
    """
    Renderiza la selección de sala de admisión.
    
    Returns:
        bool: True si se ha seleccionado una sala, False en caso contrario.
    """
    st.subheader("1️⃣ Selección de Sala de Admisión")
    
    salas_adm = obtener_salas_por_tipo("admision")
    
    if not salas_adm:
        st.warning("⚠️ No hay salas de admisión configuradas.")
        return False
    
    # Inicializar estado si no existe
    if 'admission_sala_admision_code' not in st.session_state:
        st.session_state.admission_sala_admision_code = None
    
    # Mostrar sala seleccionada (Ahora arriba)
    if st.session_state.admission_sala_admision_code:
        col_info, col_change = st.columns([3, 1])
        with col_info:
            st.info(f"📍 Sala seleccionada: **{st.session_state.admission_sala_admision_code}**")
        with col_change:
            if st.button("🔄 Cambiar Sala", key="change_adm_room"):
                st.session_state.admission_sala_admision_code = None
                st.rerun()
        return True

    # Renderizar grid de salas usando componente reutilizable
    selected = render_room_grid(
        salas=salas_adm,
        selected_code=st.session_state.admission_sala_admision_code,
        button_key_prefix="sel_adm"
    )
    
    # Actualizar estado si se seleccionó una sala
    if selected:
        st.session_state.admission_sala_admision_code = selected
        st.rerun()
    
    return False
