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

def render_admission_management_view():
    """
    Renderiza la lista de pacientes o el flujo de consulta activo con stepper.
    """
    st.title("🛏️ Gestión de Ingreso o Consulta")

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
            for p in pacientes_pendientes:
                with st.container(border=True):
                    col_info, col_action = st.columns([4, 1])
                    
                    with col_info:
                        nombre = f"{p.get('nombre')} {p.get('apellido1')} {p.get('apellido2', '')}"
                        st.markdown(f"### 👤 {nombre}")
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.caption(f"🆔 `{p.get('patient_code')}`")
                        with c2:
                            edad = calcular_edad(p.get('fecha_nacimiento'))
                            st.caption(f"🎂 {edad} años")
                        with c3:
                            # Mostrar diagnóstico si viene en las notas
                            notas = p.get('notas', '')
                            if "Dx:" in notas:
                                dx = notas.split("Dx:")[1].strip()
                                st.caption(f"🩺 **Dx:** {dx}")
                            else:
                                st.caption("🩺 Sin diagnóstico previo")

                    with col_action:
                        if st.button("🩺 Atender", key=f"atender_{p.get('patient_code')}", type="primary", use_container_width=True):
                            st.session_state.active_consultation_patient = p
                            st.session_state.consultation_step = 1
                            st.rerun()

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
