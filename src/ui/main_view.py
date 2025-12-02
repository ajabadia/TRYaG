# path: src/ui/main_view.py
# Creado: 2025-11-21
# Última modificación: 2025-12-02
"""
Módulo orquestador que construye la vista principal del "Asistente de Triaje".
Implementa un flujo por pasos (stepper) para selección de sala, paciente y triaje.
"""
import streamlit as st
from components.common.stepper import render_horizontal_stepper
from components.triage.step_sala_selection import render_step_sala_selection
from components.triage.step_patient_selection import render_step_patient_selection
from components.triage.step_triage_process import render_step_triage_process
from components.triage.step_disposition import render_step_disposition
from components.triage.nursing_form import render_nursing_assessment_form
from components.triage.step_final_disposition import render_step_final_disposition
from ui.components.common.tools_panel import render_tools_panel
from datetime import datetime
from services.patient_flow_service import save_triage_data

def mostrar_asistente_triaje():
    """
    Dibuja y gestiona la lógica de la pestaña "Asistente de Triaje" con stepper.
    """
    st.title("🏥 Asistente de Triaje")

    # Banner Modo Formación
    if st.session_state.get('training_mode', False):
        st.warning("🎓 MODO FORMACIÓN ACTIVO: Los registros se marcarán como entrenamiento y no afectarán a las estadísticas reales.", icon="🎓")

    is_training = st.session_state.get('training_mode', False)

    # --- LÓGICA DE PERSISTENCIA Y AUTO-AVANCE ---
    # Si ya hay sala seleccionada y estamos en paso 0, avanzar automáticamente (Solo modo normal)
    if not is_training and st.session_state.get('triage_room_code') and st.session_state.get('triage_step', 0) == 0:
        st.session_state.triage_step = 1

    # Inicializar paso actual
    if 'triage_step' not in st.session_state:
        st.session_state.triage_step = 0

    # Definir pasos según modo
    if is_training:
        steps = [
            "Datos del Caso",
            "Realizar Triaje",
            "Valoración Enfermería",
            "Órdenes y Planificación",
            "Finalizar Entrenamiento"
        ]
        # Mapeo de pasos visuales a lógicos para training si fuera necesario, 
        # pero aquí parece que coinciden 1:1 con la lógica de abajo.
    else:
        steps = [
            "Selección de Sala",
            "Selección de Paciente",
            "Realizar Triaje",
            "Derivación"
        ]
    
    # Renderizar Stepper Horizontal
    # Ajustamos el índice visual si es necesario. 
    # En modo normal: Paso 0 (Sala) -> index 0. Paso 1 (Paciente) -> index 1.
    current_step_index = st.session_state.triage_step
    render_horizontal_stepper(steps, current_step_index)
    
    # --- PASO 0: SELECCIÓN DE SALA (Solo Normal) ---
    if st.session_state.triage_step == 0 and not is_training:
        # Panel de Herramientas (Global en paso 0)
        render_tools_panel("Triaje", show_pdf=False)
        
        sala_selected = render_step_sala_selection()
        
        # Si se selecciona sala, el componente hace rerun.
        # Al recargar, la lógica de arriba (auto-avance) nos moverá al paso 1.
    
    # --- PASO 1: SELECCIÓN DE PACIENTE / DATOS CASO ---
    elif st.session_state.triage_step == 1:
        if is_training:
            st.markdown("### 🎓 Configuración del Caso de Entrenamiento")
            st.info("Configure los datos básicos del paciente simulado.")
            
            with st.container(border=True):
                c1, c2 = st.columns(2)
                with c1:
                    age_input = st.number_input("Edad del Paciente", min_value=0, max_value=120, value=40)
                with c2:
                    sex_input = st.selectbox("Sexo", ["Hombre", "Mujer", "Otro"])
                
                if st.button("🚀 Iniciar Caso de Prueba", type="primary", use_container_width=True):
                    # Configurar entorno de prueba
                    st.session_state.triage_room_code = "SALATEST"
                    
                    # Crear paciente dummy
                    dummy_code = f"TEST-{datetime.now().strftime('%H%M%S')}"
                    st.session_state.triage_patient = {
                        "patient_code": dummy_code,
                        "nombre": "Usuario",
                        "apellido1": "De Pruebas",
                        "apellido2": f"({dummy_code})",
                        "edad": age_input,
                        "gender": sex_input,
                        "motivo_consulta": "Simulación de entrenamiento"
                    }
                    
                    # Resetear datos del triaje
                    st.session_state.datos_paciente = {
                        "texto_medico": "",
                        "edad": age_input,
                        "gender": sex_input,
                        "dolor": 5,
                        "imagenes": [],
                        "imagenes_confirmadas_ia": [],
                        "vital_signs": {}
                    }
                    st.session_state.resultado = None
                    st.session_state.calificacion_humana = None
                    st.session_state.validation_complete = False
                    st.session_state.analysis_complete = False
                    st.session_state.is_editing_text = True
                    st.session_state.show_text_error = False
                    st.session_state.modal_image_selection = {}
                    
                    # Avanzar
                    st.session_state.triage_step = 2
                    st.rerun()
            
        else:
            # Cabecera compacta de contexto
            with st.container(border=True):
                c_info, c_actions = st.columns([4, 1])
                with c_info:
                    st.markdown(f"📍 **{st.session_state.get('triage_room_code')}** | Seleccione paciente para iniciar triaje")
                with c_actions:
                    if st.button("Cambiar Sala", key="btn_change_room_header", use_container_width=True):
                        st.session_state.triage_step = 0
                        st.session_state.triage_room_code = None
                        st.rerun()

            patient_selected = render_step_patient_selection()
            
            # El componente step_patient_selection ahora debe manejar el avance
            # Si retorna True (paciente seleccionado), avanzamos
            if patient_selected:
                    # La lógica de avance ya debería estar en el botón "Atender" del componente
                    # Pero por seguridad, si detectamos paciente seleccionado aquí:
                    if st.session_state.get('triage_patient'):
                        st.session_state.triage_step = 2
                        # Resetear datos del paciente para asegurar un formulario limpio
                        st.session_state.datos_paciente = {
                        "texto_medico": "",
                        "edad": st.session_state.triage_patient.get('edad', 40) if st.session_state.triage_patient else 40,
                        "dolor": 5,
                        "imagenes": [],
                        "imagenes_confirmadas_ia": [],
                        "vital_signs": {}
                        }
                        st.session_state.resultado = None
                        st.session_state.calificacion_humana = None
                        st.session_state.validation_complete = False
                        st.session_state.analysis_complete = False
                        st.session_state.is_editing_text = True
                        st.session_state.show_text_error = False
                        st.session_state.modal_image_selection = {}
                        st.rerun()

    # --- PASO 2: REALIZAR TRIAJE ---
    elif st.session_state.triage_step == 2:
        # Botón Volver
        if st.button("← Volver", use_container_width=True):
            st.session_state.triage_step = 1
            if not is_training:
                st.session_state.triage_patient = None
            # Limpiar datos del triaje
            st.session_state.resultado = None
            st.session_state.datos_paciente = {
                "texto_medico": "",
                "edad": 40,
                "dolor": 5,
                "imagenes": [],
                "imagenes_confirmadas_ia": [],
                "vital_signs": {}
            }
            st.session_state.calificacion_humana = None
            st.session_state.validation_complete = False
            st.session_state.analysis_complete = False
            st.rerun()
        
        # Panel de Herramientas (Feedback + PDF)
        render_tools_panel("Triaje", st.session_state.get('triage_patient'))
        
        validation_complete = render_step_triage_process()
        
        # Botón para continuar a derivación si validación completa
        if validation_complete:
            st.divider()
            if st.button("Continuar a Valoración Enfermería →", type="primary", use_container_width=True):
                st.session_state.triage_step = 3
                st.rerun()

    # --- PASO 3: VALORACIÓN ENFERMERÍA ---
    elif st.session_state.triage_step == 3:
        # Botón Volver
        if st.button("← Volver a Triaje", use_container_width=True):
            st.session_state.triage_step = 2
            st.rerun()
            
        render_nursing_assessment_form()
        
        st.divider()
        if st.button("Continuar a Órdenes →", type="primary", use_container_width=True):
            st.session_state.triage_step = 4
            st.rerun()

    # --- PASO 4: ÓRDENES Y PLANIFICACIÓN ---
    elif st.session_state.triage_step == 4:
        # Botón Volver
        if st.button("← Volver a Enfermería", use_container_width=True):
            st.session_state.triage_step = 3
            st.rerun()
            
        render_step_disposition() # Ahora solo renderiza Órdenes
        
        # El botón "Continuar" está dentro de render_step_disposition

    # --- PASO 5: DESTINO / FINALIZACIÓN ---
    elif st.session_state.triage_step == 5:
        # Botón Volver
        if st.button("← Volver a Órdenes", use_container_width=True):
            st.session_state.triage_step = 4
            st.rerun()
        
        if is_training:
            st.markdown("### ✅ Finalizar Entrenamiento")
            st.success("Ha completado el flujo de triaje y enfermería en modo formación.")
            
            st.info("Al finalizar, el registro se guardará marcado como 'Entrenamiento' y volverá a la pantalla de configuración del caso.")
            
            if st.button("💾 Guardar y Finalizar Caso", type="primary", use_container_width=True):
                # Guardar datos
                full_data = {
                    "datos_paciente": st.session_state.datos_paciente,
                    "resultado": st.session_state.resultado,
                    "evaluator_id": "trainee",
                    "contingency_mode": st.session_state.get('contingency_mode', False),
                    "is_training": True
                }
                save_triage_data(st.session_state.triage_patient['patient_code'], full_data)
                
                st.success("Caso guardado correctamente.")
                import time
                time.sleep(1)
                
                # Reiniciar a paso 1
                st.session_state.triage_step = 1
                st.session_state.triage_patient = None
                st.rerun()
        else:
            render_step_final_disposition()

    st.markdown('<div class="debug-footer">src/ui/main_view.py</div>', unsafe_allow_html=True)