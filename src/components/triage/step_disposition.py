# path: src/components/triage/step_disposition.py
# Creado: 2025-11-24
"""
Paso 3 del Asistente de Triaje: Derivación / Destino.
Permite asignar sala de espera, rechazar o devolver a admisión.
"""
import streamlit as st
from datetime import datetime
from services.patient_flow_service import completar_triaje, rechazar_paciente, reassign_patient_flow, save_triage_data
from services.room_service import obtener_salas_por_tipo

def render_step_disposition():
    """Renderiza las opciones de destino post-triaje."""
    st.markdown("### 4. Derivación y Destino")
    
    p = st.session_state.get('triage_patient')
    if not p:
        st.error("No hay paciente activo.")
        return False
        
    st.info(f"Triaje completado para: **{p.get('nombre')} {p.get('apellido1')}**")
    
    # --- ÓRDENES Y PLANIFICACIÓN ---
    from components.triage.disposition_form import render_disposition_form
    render_disposition_form()
    
    st.divider()
    
    col_prev, col_next = st.columns([1, 4])
    with col_next:
        if st.button("Continuar a Destino (Derivación) →", type="primary", use_container_width=True):
            st.session_state.triage_step = 5
            st.rerun()

    st.markdown('<div class="debug-footer">src/components/triage/step_disposition.py</div>', unsafe_allow_html=True)
    return True
