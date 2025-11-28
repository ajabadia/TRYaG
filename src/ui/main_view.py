# path: src/ui/main_view.py
# Creado: 2025-11-21
# Última modificación: 2025-11-24
"""
Módulo orquestador que construye la vista principal del "Asistente de Triaje".
Implementa un flujo por pasos (stepper) para selección de sala, paciente y triaje.
"""
import streamlit as st
from components.common.stepper import render_vertical_stepper
from components.triage.step_sala_selection import render_step_sala_selection
from components.triage.step_patient_selection import render_step_patient_selection
from components.triage.step_triage_process import render_step_triage_process
from components.triage.step_disposition import render_step_disposition

def mostrar_asistente_triaje():
    """
    Dibuja y gestiona la lógica de la pestaña "Asistente de Triaje" con stepper.
    """
    st.title("🏥 Asistente de Triaje")

    # Inicializar paso actual
    if 'triage_step' not in st.session_state:
        st.session_state.triage_step = 0

    # Definir pasos
    steps = [
        "Selección de Sala",
        "Selección de Paciente",
        "Realizar Triaje",
        "Derivación"
    ]
    
    # Layout: stepper a la izquierda, contenido a la derecha
    col_stepper, col_content = st.columns([1, 4])
    
    with col_stepper:
        render_vertical_stepper(steps, st.session_state.triage_step)
        
    with col_content:
        # --- PASO 0: SELECCIÓN DE SALA ---
        if st.session_state.triage_step == 0:
            sala_selected = render_step_sala_selection()
            
            if sala_selected:
                st.divider()
                if st.button("Continuar a Pacientes →", type="primary", use_container_width=True):
                    st.session_state.triage_step = 1
                    st.rerun()
        
        # --- PASO 1: SELECCIÓN DE PACIENTE ---
        elif st.session_state.triage_step == 1:
            patient_selected = render_step_patient_selection()
            
            st.divider()
            col_back, col_next = st.columns([1, 1])
            
            with col_back:
                if st.button("← Cambiar Sala"):
                    st.session_state.triage_step = 0
                    st.session_state.triage_room_code = None
                    st.session_state.triage_patient = None
                    st.rerun()
            
            with col_next:
                if patient_selected:
                    if st.button("Iniciar Triaje →", type="primary"):
                        st.session_state.triage_step = 2
                        st.rerun()

        # --- PASO 2: REALIZAR TRIAJE ---
        elif st.session_state.triage_step == 2:
            validation_complete = render_step_triage_process()
            
            # Botón para continuar a derivación si validación completa
            if validation_complete:
                st.divider()
                if st.button("Continuar a Derivación →", type="primary", use_container_width=True):
                    st.session_state.triage_step = 3
                    st.rerun()
            
            st.divider()
            if st.button("← Volver a Lista de Pacientes"):
                st.session_state.triage_step = 1
                st.session_state.triage_patient = None
                # Limpiar datos del triaje
                st.session_state.resultado = None
                st.session_state.datos_paciente = {
                    "texto_medico": "",
                    "edad": 40,
                    "dolor": 5,
                    "imagenes": [],
                    "imagenes_confirmadas_ia": []
                }
                st.session_state.calificacion_humana = None
                st.session_state.validation_complete = False
                st.rerun()

        # --- PASO 3: DERIVACIÓN ---
        elif st.session_state.triage_step == 3:
            render_step_disposition()

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/main_view.py</div>', unsafe_allow_html=True)