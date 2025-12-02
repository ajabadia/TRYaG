# path: src/ui/waiting_room_dashboard.py
import streamlit as st
from services.patient_flow_service import obtener_vista_global_salas
from services.room_service import obtener_salas_por_tipo
from ui.components.waiting_list import render_waiting_list_component

from ui.components.common.tools_panel import render_tools_panel

def render_waiting_room_dashboard():
    """
    Renderiza el tablero principal de la Sala de Espera.
    Muestra estadísticas y la lista priorizada de pacientes.
    """
    st.header("🪑 Sala de Espera")
    
    # Panel de Herramientas
    render_tools_panel("Sala de Espera", show_pdf=False)
    
    # 1. Obtener pacientes en espera
    vista_global = obtener_vista_global_salas()
    
    # Filtrar solo los que están en salas de espera (DERIVADO)
    salas_box = obtener_salas_por_tipo('box')
    salas_espera = [s for s in salas_box if s.get('subtipo') == 'espera']
    codigos_espera = [s['codigo'] for s in salas_espera]
    
    pacientes_espera = []
    for codigo in codigos_espera:
        pacientes_espera.extend(vista_global.get(codigo, []))
        
    # 2. Estadísticas Rápidas
    total = len(pacientes_espera)
    criticos = sum(1 for p in pacientes_espera if "Rojo" in str(p.get('nivel_triaje', '')) or "Nivel I" in str(p.get('nivel_triaje', '')))
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total en Espera", total)
    c2.metric("Críticos / Nivel I", criticos, delta_color="inverse")
    
    st.divider()
    
    # 3. Renderizar Lista
    if pacientes_espera:
        render_waiting_list_component(pacientes_espera, context="dashboard")
    else:
        st.info("La sala de espera está vacía. ¡Buen trabajo!")

    st.markdown('<div class="debug-footer">src/ui/waiting_room_dashboard.py</div>', unsafe_allow_html=True)
