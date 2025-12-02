# path: src/ui/boxes_view.py
# Creado: 2025-11-24
# Refactorizado: 2025-12-02 (Stepper Horizontal)
"""
Vista principal para la Gestión de Boxes y Consultas.
Orquesta el flujo de trabajo del médico:
1. Selección de Sala
2. Selección de Paciente (si está libre)
3. Atención Clínica (si tiene paciente)
"""
import streamlit as st
from components.common.stepper import render_horizontal_stepper
from components.boxes import (
    render_step_sala_selection,
    render_step_patient_selection,
    render_step_attention
)
from services.flow_manager import obtener_pacientes_en_sala
from ui.components.common.tools_panel import render_tools_panel

def render_room_header(room_code, step_name, on_back=None, on_change=None):
    """
    Renderiza una cabecera pegajosa (sticky) para la vista de boxes.
    """
    # CSS para hacer sticky el contenedor
    # Cargar CSS externo
    from utils.ui_utils import load_css
    load_css("src/assets/css/pages/boxes.css")
    
    st.markdown('<div class="room-header-marker"></div>', unsafe_allow_html=True)

    with st.container():
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"### 📍 {room_code} <span style='color:gray; font-weight:normal; font-size:0.8em'>| {step_name}</span>", unsafe_allow_html=True)
        with c2:
            if on_change:
                if st.button("🔄 Cambiar Sala", key="btn_change_room", use_container_width=True):
                    on_change()
            elif on_back:
                if st.button("⬅️ Volver", key="btn_back_list", use_container_width=True):
                    on_back()

def render_boxes_view():
    """
    Renderiza la vista completa de gestión de boxes con stepper.
    """
    # Panel de Herramientas
    render_tools_panel("Atención Box", show_pdf=False)
    
    # --- LÓGICA DE PERSISTENCIA Y AUTO-AVANCE ---
    # Si ya hay sala seleccionada y estamos en paso 0, avanzar automáticamente
    if st.session_state.get('boxes_room_code') and st.session_state.get('boxes_step', 0) == 0:
        st.session_state.boxes_step = 1

    # Inicializar paso actual
    if 'boxes_step' not in st.session_state:
        st.session_state.boxes_step = 0

    # Sincronizar estado lógico con pasos visuales
    # Si no hay sala, forzar paso 0
    if not st.session_state.get('boxes_room_code'):
        st.session_state.boxes_step = 0
    
    # Si hay sala pero estamos en paso 0, avanzar a paso 1
    elif st.session_state.get('boxes_room_code') and st.session_state.boxes_step == 0:
        st.session_state.boxes_step = 1
        st.rerun()

    # Verificar si hay paciente activo en sala (médico ocupado) para saltar a paso 2
    # Esto se hace si estamos en paso 1 (seleccionando paciente) pero resulta que ya hay uno
    if st.session_state.get('boxes_room_code') and st.session_state.boxes_step == 1:
        pacientes_activos = obtener_pacientes_en_sala(st.session_state.boxes_room_code)
        if pacientes_activos:
             st.session_state.boxes_step = 2
             st.rerun()

    # Definir pasos
    steps = [
        "Selección de Sala",
        "Selección de Paciente",
        "Atención Clínica"
    ]
    
    # Renderizar Stepper Horizontal
    render_horizontal_stepper(steps, st.session_state.boxes_step)
    
    st.title("🩺 Atención Clínica en Box")
    
    # --- PASO 0: SELECCIÓN DE SALA ---
    if st.session_state.boxes_step == 0:
        st.markdown("### Seleccione su Box de Atención")
        render_step_sala_selection()
        # La transición a paso 1 ocurre cuando se selecciona sala (rerun provocado por el componente)
        if st.session_state.get('boxes_room_code'):
                st.session_state.boxes_step = 1
                st.rerun()

    # --- PASO 1: SELECCIÓN DE PACIENTE ---
    elif st.session_state.boxes_step == 1:
        room_code = st.session_state.get('boxes_room_code')
        
        def change_room():
            st.session_state.boxes_room_code = None
            st.session_state.boxes_step = 0
            st.rerun()

        render_room_header(room_code, "Lista de Pacientes", on_change=change_room)

        # Verificar si hay paciente activo en la sala (Médico ocupado)
        pacientes_activos = obtener_pacientes_en_sala(room_code)
        medico_ocupado = len(pacientes_activos) > 0
        
        if medico_ocupado:
            # Si ya hay alguien siendo atendido, saltamos directo a atención
            st.session_state.boxes_step = 2
            st.rerun()
        else:
            render_step_patient_selection()

    # --- PASO 2: ATENCIÓN CLÍNICA ---
    elif st.session_state.boxes_step == 2:
        room_code = st.session_state.get('boxes_room_code')
        
        def go_back():
                st.session_state.boxes_step = 1
                st.rerun()
        
        render_room_header(room_code, "En Atención", on_back=go_back)
        
        render_step_attention()

    st.markdown('<div class="debug-footer">src/ui/boxes_view.py</div>', unsafe_allow_html=True)
