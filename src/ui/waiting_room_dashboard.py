# path: src/ui/waiting_room_dashboard.py
import streamlit as st
from services.patient_flow_service import obtener_vista_global_salas
from services.room_service import obtener_salas_por_tipo
from ui.components.waiting_list import render_waiting_list_component



def render_waiting_room_dashboard():
    """
    Renderiza el tablero principal de la Sala de Espera.
    Muestra estadísticas y la lista priorizada de pacientes.
    """
    st.header("🪑 Sala de Espera")
    
    # Fragment logic for auto-refresh
    if hasattr(st, "fragment"):
        # Auto-refresh every 30 seconds
        @st.fragment(run_every=30)
        def _render_dashboard_content():
            _render_waiting_logic()
    else:
        def _render_dashboard_content():
            _render_waiting_logic()
            if st.button("🔄 Actualizar"):
                st.rerun()

    _render_dashboard_content()
    
    st.markdown('<div class="debug-footer">src/ui/waiting_room_dashboard.py</div>', unsafe_allow_html=True)

def _render_waiting_logic():
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
    
    # 3. Calcular Tiempos Estimados (Smart Queue)
    # -------------------------------------------------------------------------
    # Supuesto: 3 Doctores, 15 min media por paciente
    NUM_DOCTORS = 3 
    AVG_CONSULT_TIME = 20 # minutos
    
    # Ordenar localmente para proyección (Simulando la lógica de sort_queue)
    # Prioridad: Rojo(1) > Naranja(2) > Amarillo(3) > Verde(4) > Azul(5)
    def get_priority(p):
        lvl = str(p.get('nivel_triaje', ''))
        if "Rojo" in lvl or "Nivel I" in lvl: return 1
        if "Naranja" in lvl or "Nivel II" in lvl: return 2
        if "Amarillo" in lvl or "Nivel III" in lvl: return 3
        if "Verde" in lvl or "Nivel IV" in lvl: return 4
        return 5
        
    # Ordenar por prioridad ASC y luego por hora de llegada ASC
    pacientes_espera.sort(key=lambda x: (get_priority(x), x.get('wait_start', '')))

    current_accumulated_min = 0
    for i, p in enumerate(pacientes_espera):
        # Cada doctor toma un paciente en paralelo.
        # Si hay 3 docs, los primeros 3 entran "ya" (0 wait).
        # El 4º espera a que el primero termine (AVG_TIME).
        
        # Formula simple: (Posición // Num_Docs) * Avg_Time
        wait_cycles = i // NUM_DOCTORS
        est_min = wait_cycles * AVG_CONSULT_TIME
        
        # Ajuste: Si ya lleva esperando mucho, el estimado baja? 
        # No, el estimado es "cuánto falta". 
        # Pero simplificaremos: "Tiempo Total Estimado de Espera" = est_min
        # "Cuanto le falta" = max(0, est_min - tiempo_ya_esperado)
        
        p['estimated_wait_minutes'] = est_min
        
    # Visualización de métricas extra
    with st.expander("📊 Métricas de Operación (Smart Room)", expanded=False):
        c_docs, c_avg, c_flow = st.columns(3)
        c_docs.metric("Doctores Activos", NUM_DOCTORS)
        c_avg.metric("Tiempo Medio Atención", f"{AVG_CONSULT_TIME} min")
        next_free = max(0, (len(pacientes_espera) // NUM_DOCTORS) * AVG_CONSULT_TIME)
        c_flow.metric("Prox. Hueco Est.", f"en {next_free} min")

    st.divider()
    
    # 4. Renderizar Lista
    if pacientes_espera:
        render_waiting_list_component(pacientes_espera, context="dashboard")
    else:
        st.info("La sala de espera está vacía. ¡Buen trabajo!")
