# path: src/ui/boxes_view.py
# Creado: 2025-11-24
# Refactorizado: 2025-11-28 (Stepper)
"""
Vista principal para la Gestión de Boxes y Consultas.
Orquesta el flujo de trabajo del médico:
1. Selección de Sala
2. Selección de Paciente (si está libre)
3. Atención Clínica (si tiene paciente)
"""
import streamlit as st
from components.common.stepper import render_vertical_stepper
from components.boxes import (
    render_step_sala_selection,
    render_step_patient_selection,
    render_step_attention
)
from services.flow_manager import obtener_pacientes_en_sala

def render_boxes_view():
    """
    Renderiza la vista completa de gestión de boxes con stepper.
    """
    st.title("🩺 Gestión de Boxes y Consultas")
    
    # Inicializar paso actual
    if 'boxes_step' not in st.session_state:
        st.session_state.boxes_step = 0

    # Sincronizar estado lógico con pasos visuales
    # Si no hay sala, forzar paso 0
    if not st.session_state.get('boxes_room_code'):
        st.session_state.boxes_step = 0
    # Si hay sala pero no paciente (y no estamos en paso 0), paso 1
    elif st.session_state.get('boxes_room_code') and not st.session_state.get('active_patient_code'):
        # Verificar si hay paciente activo en sala (médico ocupado)
        pacientes_activos = obtener_pacientes_en_sala(st.session_state.boxes_room_code)
        if pacientes_activos:
             # Si hay paciente activo, deberíamos estar en atención (Paso 2)
             # Pero necesitamos saber cuál es para seleccionarlo automáticamente o dejar que el usuario lo retome
             # Por simplicidad, si hay paciente activo, asumimos que el médico debe atenderlo.
             # Sin embargo, el componente render_step_attention suele requerir un paciente seleccionado.
             # Si el componente step_attention maneja la selección automática, bien. 
             # Si no, step_patient_selection debería mostrarlo como "En curso".
             pass
        else:
             if st.session_state.boxes_step > 1: # Si estábamos en atención y terminamos
                 st.session_state.boxes_step = 1
             elif st.session_state.boxes_step == 0: # Si venimos de selección de sala
                 st.session_state.boxes_step = 1

    # Definir pasos
    steps = [
        "Selección de Sala",
        "Selección de Paciente",
        "Atención Clínica"
    ]
    
    col_stepper, col_content = st.columns([1, 4])
    
    with col_stepper:
        render_vertical_stepper(steps, st.session_state.boxes_step)
        
    with col_content:
        # --- PASO 0: SELECCIÓN DE SALA ---
        if st.session_state.boxes_step == 0:
            render_step_sala_selection()
            # La transición a paso 1 ocurre cuando se selecciona sala (rerun provocado por el componente)
            if st.session_state.get('boxes_room_code'):
                 st.session_state.boxes_step = 1
                 st.rerun()

        # --- PASO 1: SELECCIÓN DE PACIENTE ---
        elif st.session_state.boxes_step == 1:
            room_code = st.session_state.get('boxes_room_code')
            
            # Barra superior con info de sala
            col_info, col_change = st.columns([4, 1])
            with col_info:
                st.info(f"📍 Sala Activa: **{room_code}**")
            with col_change:
                if st.button("Cambiar Sala", type="secondary"):
                    st.session_state.boxes_room_code = None
                    st.session_state.boxes_step = 0
                    st.rerun()

            # Verificar si hay paciente activo en la sala (Médico ocupado)
            pacientes_activos = obtener_pacientes_en_sala(room_code)
            medico_ocupado = len(pacientes_activos) > 0
            
            if medico_ocupado:
                # Si ya hay alguien siendo atendido, saltamos directo a atención
                st.session_state.boxes_step = 2
                st.rerun()
            else:
                render_step_patient_selection()
                # La transición a paso 2 ocurre cuando se selecciona un paciente (rerun interno o detección aquí)
                # El componente render_step_patient_selection debería setear 'active_patient_code' o similar
                # Si el componente no maneja el estado global directamente, habría que adaptarlo.
                # Asumimos que render_step_patient_selection actualiza el estado necesario.

        # --- PASO 2: ATENCIÓN CLÍNICA ---
        elif st.session_state.boxes_step == 2:
            room_code = st.session_state.get('boxes_room_code')
            
            # Barra superior simplificada o botón volver
            if st.button("⬅️ Volver a Lista de Pacientes"):
                 # Lógica para cancelar/pausar atención si es necesario
                 st.session_state.boxes_step = 1
                 st.rerun()
            
            render_step_attention()

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/boxes_view.py</div>', unsafe_allow_html=True)
