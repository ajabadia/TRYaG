# path: src/ui/admission_management_view.py
# Creado: 2025-11-24
# Refactorizado: 2025-11-28 (Stepper)
"""
Vista para la Gestión de Ingresos y Consultas.
Permite seleccionar pacientes pendientes y realizar el flujo clínico completo.
"""
import streamlit as st
from components.common.stepper import render_vertical_stepper
from services.room_service import obtener_salas_por_tipo
from services.flow_manager import obtener_pacientes_en_sala
from services.patient_service import obtener_paciente_por_codigo, calcular_edad
from components.consultation import render_consultation_flow

from ui.components.common.tools_panel import render_tools_panel

def render_admission_management_view():
    """
    Renderiza la lista de pacientes o el flujo de consulta activo con stepper.
    """
    st.title("🛏️ Gestión de Ingreso o Consulta")
    
    # Panel de Herramientas
    render_tools_panel("Consulta", show_pdf=False)

    # Inicializar paso
    if 'consultation_step' not in st.session_state:
        st.session_state.consultation_step = 0

    # Sincronizar estado
    if st.session_state.get('active_consultation_patient'):
        st.session_state.consultation_step = 1
    else:
        st.session_state.consultation_step = 0

    steps = [
        "Lista de Pacientes",
        "Consulta Médica"
    ]

    col_stepper, col_content = st.columns([1, 4])

    with col_stepper:
        render_vertical_stepper(steps, st.session_state.consultation_step)

    with col_content:
        # --- PASO 0: LISTA DE PACIENTES ---
        if st.session_state.consultation_step == 0:
            st.info("💡 Seleccione un paciente para iniciar la consulta o gestionar el ingreso.")

            # 1. Obtener salas de espera de ingreso/consulta
            salas_ingreso = [s for s in obtener_salas_por_tipo("consulta_ingreso") if s.get('subtipo') == 'espera']
            
            if not salas_ingreso:
                st.warning("⚠️ No hay salas de espera de ingreso o consulta configuradas.")
                return

            # 2. Buscar pacientes en esas salas
            pacientes_pendientes = []
            for sala in salas_ingreso:
                flujos = obtener_pacientes_en_sala(sala['codigo'])
                for f in flujos:
                    paciente = obtener_paciente_por_codigo(f['patient_code'])
                    if paciente:
                        item = {**paciente, **f}
                        item['sala_origen'] = sala['codigo']
                        pacientes_pendientes.append(item)

            if not pacientes_pendientes:
                st.success("✅ No hay pacientes pendientes.")
                if st.button("🔄 Actualizar"):
                    st.rerun()
                return

            st.markdown(f"**Pendientes:** {len(pacientes_pendientes)}")
            
            # 3. Listar y gestionar
            st.markdown(f"**Pendientes:** {len(pacientes_pendientes)}")
            
            # 3. Listar y gestionar
            from ui.components.common.patient_card import render_patient_card
            
            for p in pacientes_pendientes:
                def _on_atender(patient):
                    st.session_state.active_consultation_patient = patient
                    st.session_state.consultation_step = 1
                    st.rerun()

                actions = [{
                    "label": "🩺 Atender",
                    "key": "atender",
                    "type": "primary",
                    "on_click": _on_atender
                }]
                
                # Mostrar diagnóstico en la card si existe
                # Podemos inyectarlo en el nombre o usar un campo custom si la card lo soportara,
                # pero por ahora lo dejamos como parte de la info que la card ya muestra (si lo pasamos en el dict)
                # La card muestra 'sala_espera_origen' si show_location=True.
                
                render_patient_card(
                    patient=p,
                    actions=actions,
                    show_triage_level=False,
                    show_wait_time=True,
                    show_location=True,
                    key_prefix="adm_mgmt_list"
                )

        # --- PASO 1: CONSULTA MÉDICA ---
        elif st.session_state.consultation_step == 1:
            active_patient = st.session_state.active_consultation_patient
            
            col_back, col_title = st.columns([1, 5])
            with col_back:
                if st.button("⬅️ Volver", use_container_width=True):
                    st.session_state.active_consultation_patient = None
                    st.session_state.consultation_step = 0
                    st.rerun()
            
            if active_patient:
                render_consultation_flow(
                    active_patient, 
                    active_patient, # El objeto tiene datos de paciente y flujo mergeados
                    on_finish=_on_consultation_finish
                )

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/admission_management_view.py</div>', unsafe_allow_html=True)

def _on_consultation_finish():
    """Callback al finalizar la consulta."""
    st.session_state.active_consultation_patient = None
    st.session_state.consultation_step = 0
    st.rerun()
