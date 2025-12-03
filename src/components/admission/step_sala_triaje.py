# path: src/components/admission/step_sala_triaje.py
# Creado: 2025-11-24
# Última modificación: 2025-11-24
"""
Paso 3 del flujo de admisión: Selección de Sala de Triaje.
"""
import streamlit as st
from services.room_service import obtener_salas_por_tipo
from components.common.room_card import render_room_grid


def render_step_sala_triaje() -> bool:
    """
    Renderiza la selección de sala de triaje con información de ocupación.
    
    Returns:
        bool: True si se ha seleccionado una sala, False en caso contrario.
    """
    st.subheader("3️⃣ Selección de Sala de Triaje")
    
    salas_triaje = obtener_salas_por_tipo("triaje")
    # Filtrar solo salas de espera (donde va el paciente)
    salas_triaje = [s for s in salas_triaje if s.get('subtipo') == 'espera']
    
    if not salas_triaje:
        st.warning("⚠️ No hay salas de espera de triaje configuradas.")
        return False
    
    # Inicializar estado si no existe
    if 'admission_sala_triaje_code' not in st.session_state:
        st.session_state.admission_sala_triaje_code = None
    
    # Renderizar grid de salas usando componente reutilizable
    selected = render_room_grid(
        salas=salas_triaje,
        selected_code=st.session_state.admission_sala_triaje_code,
        button_key_prefix="sel_triaje"
    )
    
    # Actualizar estado si se seleccionó una sala
    if selected:
        st.session_state.admission_sala_triaje_code = selected
        st.rerun()
    
    # Mostrar sala seleccionada
    if st.session_state.admission_sala_triaje_code:
        # La visualización de la selección se maneja en el componente padre (admission_view)
        return True
    
    return None

    st.markdown('<div class="debug-footer">src/components/admission/step_sala_triaje.py</div>', unsafe_allow_html=True)
