# path: src/ui/admission_view.py
# Creado: 2025-11-24
# Actualizado: 2025-11-25 - Mejoras flujo admisión (validación y fusión de pasos)
"""
Vista principal del flujo de admisión de pacientes.
Implementa un flujo por pasos (stepper) optimizado.
"""
import streamlit as st
from components.common.stepper import render_vertical_stepper
from components.admission.step_sala_admision import render_step_sala_admision
from components.admission.step_patient_data import render_step_patient_data
from components.admission.step_sala_triaje import render_step_sala_triaje
# Importamos funciones necesarias para la confirmación in-situ
from services.patient_service import calcular_edad, obtener_paciente_por_codigo
from services.flow_manager import obtener_registro_activo, crear_nuevo_flujo, mover_paciente_a_sala, rechazar_paciente as rechazar_flow
from services.permissions_service import get_current_user

def _get_username():
    user = get_current_user()
    return user.get("username", "unknown") if user else "unknown"


from components.common.feedback_button import render_feedback_button

def mostrar_admision():
    """
    Orquesta el flujo completo de admisión con stepper vertical.
    """
    # Inicializar paso actual
    if 'admission_step' not in st.session_state:
        st.session_state.admission_step = 0
    
    # Definir pasos (Fusionados Triaje y Confirmación)
    steps = [
        "Sala de Admisión",
        "Datos del Paciente",
        "Asignación y Confirmación" # Paso 3 fusionado
    ]
    
    # Layout: stepper a la izquierda, contenido a la derecha
    col_stepper, col_content = st.columns([1, 4])
    
    with col_stepper:
        render_vertical_stepper(steps, st.session_state.admission_step)
    
    with col_content:
        # --- PASO 0: SELECCIÓN DE SALA DE ADMISIÓN ---
        if st.session_state.admission_step == 0:
            # Botón de Feedback (alineado a la derecha)
            c_spacer, c_fb = st.columns([10, 1])
            with c_fb:
                render_feedback_button("Admisión")

            sala_selected = render_step_sala_admision()
            
            if sala_selected:
                st.divider()
                if st.button("Continuar a Datos del Paciente →", type="primary", use_container_width=True):
                    st.session_state.admission_step = 1
                    st.rerun()
        
        # --- PASO 1: DATOS DEL PACIENTE ---
        elif st.session_state.admission_step == 1:
            patient_validated = render_step_patient_data()
            
            st.divider()
            col_back, col_next = st.columns([1, 1])
            
            with col_back:
                if st.button("← Volver a Sala de Admisión"):
                    st.session_state.admission_step = 0
                    st.rerun()
            
            with col_next:
                # Botón deshabilitado hasta que se valide el paciente
                if st.button("Asignar Sala de Triaje →", type="primary", disabled=not patient_validated):
                    st.session_state.admission_step = 2
                    # Limpiar selección previa para obligar a seleccionar y que no aparezca el bloque de confirmación automáticamente
                    st.session_state.admission_sala_triaje_code = None
                    st.rerun()
        
        # --- PASO 2: ASIGNACIÓN O RECHAZO (FUSIONADOS) ---
        elif st.session_state.admission_step == 2:
            st.subheader("3. Destino del Paciente")
            
            # Si ya se completó, mostrar solo resumen y botón de reinicio
            if st.session_state.get('admission_complete', False):
                _render_completion_summary()
                return

            # --- ESTADO: SALA SELECCIONADA (Confirmación) ---
            if st.session_state.get('admission_sala_triaje_code'):
                triaje_selected = st.session_state.admission_sala_triaje_code
                
                # Mostrar Confirmación Arriba
                st.info(f"📍 Sala de triaje seleccionada: **{triaje_selected}**")
                
                st.divider()
                st.subheader("✅ Confirmar Asignación")
                
                # Resumen rápido
                patient_code = st.session_state.get('admission_patient_code')
                paciente = obtener_paciente_por_codigo(patient_code)
                nombre = f"{paciente.get('nombre')} {paciente.get('apellido1')}"
                
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Paciente:** {nombre}")
                    with c2:
                        st.markdown(f"**Destino:** {triaje_selected}")
                
                # Acciones Principales
                col_confirm, col_change = st.columns([2, 1])
                with col_confirm:
                    if st.button("📋 Confirmar y Enviar a Triaje", type="primary", use_container_width=True):
                        _execute_assignment(triaje_selected)
                with col_change:
                    if st.button("🔄 Cambiar Sala", use_container_width=True):
                        st.session_state.admission_sala_triaje_code = None
                        st.rerun()
                
                st.divider()
                st.markdown("**Otras Acciones:**")
                col_reject, col_derive = st.columns(2)
                with col_reject:
                    if st.button("🚫 Rechazar Paciente", type="secondary", use_container_width=True):
                        st.session_state.admission_decision_mode = 'reject'
                        st.session_state.admission_sala_triaje_code = None # Limpiar selección
                        st.rerun()
                with col_derive:
                     # Placeholder para derivación a consulta (si existiera lógica específica)
                     # Por ahora, asumimos que derivar a consulta es asignarlo a una sala tipo 'consulta'
                     # Pero el grid actual solo muestra 'triaje'. 
                     # Si el usuario quiere derivar a consulta, deberíamos mostrar salas de consulta?
                     # El usuario dijo: "derivarlo a consultas (mira cómo se hace en otros lados)".
                     # En Triage Step 3 hay derivación.
                     # Aquí, simplificaremos mostrando un mensaje o implementando si es crítico.
                     # Dado que no hay un "Step Consulta", lo trataremos como "Rechazar" o "Asignar a otra sala".
                     # Implementaremos "Derivar a Consulta" como una acción que cambia el grid a salas de consulta?
                     # Mejor: Botón que cambia el modo a 'derive_consulta' y muestra grid de consultas.
                    if st.button("👨‍⚕️ Derivar a Consulta", use_container_width=True):
                        st.session_state.admission_decision_mode = 'derive_consulta'
                        st.session_state.admission_sala_triaje_code = None
                        st.rerun()

            # --- ESTADO: MODO RECHAZO ---
            elif st.session_state.get('admission_decision_mode') == 'reject':
                st.warning("🚫 Rechazo de Paciente")
                from components.common.rejection_form import render_rejection_form
                
                def _handle_cancel():
                    st.session_state.admission_decision_mode = None
                    st.rerun()
                
                render_rejection_form(
                    key_prefix="adm_flow",
                    on_confirm=_execute_rejection,
                    on_cancel=_handle_cancel
                )

            # --- ESTADO: MODO DERIVAR A CONSULTA ---
            elif st.session_state.get('admission_decision_mode') == 'derive_consulta':
                st.info("Seleccione la Consulta de destino:")
                from services.room_service import obtener_salas_por_tipo
                from components.common.room_card import render_room_grid
                
                salas_consulta = obtener_salas_por_tipo("consulta_ingreso")
                # Filtrar activas y subtipo si aplica (asumimos todas las consultas valen)
                
                if not salas_consulta:
                    st.warning("No hay consultas disponibles.")
                    if st.button("Volver"):
                        st.session_state.admission_decision_mode = None
                        st.rerun()
                else:
                    selected_consulta = render_room_grid(salas_consulta, None, "sel_consulta")
                    if selected_consulta:
                        # Reutilizamos lógica de asignación pero cambiando tipo destino
                        _execute_assignment(selected_consulta, tipo_destino="consulta", subtipo_destino="atencion") # Asumimos atencion directa? O espera? Consultas suelen ser directas o espera.
                        # Si es espera de consulta:
                        # _execute_assignment(selected_consulta, tipo_destino="consulta", subtipo_destino="espera")
                    
                    if st.button("← Volver a Selección de Triaje"):
                        st.session_state.admission_decision_mode = None
                        st.rerun()

            # --- ESTADO: SELECCIÓN DE SALA (Default) ---
            else:
                st.info("Seleccione la sala de espera de triaje:")
                
                # Renderizar grid de triaje (el componente ya maneja su estado interno, pero aquí lo controlamos)
                # El componente `render_step_sala_triaje` guarda en `admission_sala_triaje_code` y hace rerun.
                # Así que solo necesitamos llamarlo.
                triaje_selected = render_step_sala_triaje()
                
                # Si el componente retorna (ya seleccionó), el rerun ocurrirá dentro de él o aquí.
                # Pero `render_step_sala_triaje` muestra "Sala seleccionada" al final.
                # Debemos modificar `render_step_sala_triaje` O no usarlo y usar `render_room_grid` directamente aquí
                # para tener control total del layout (ocultar grid).
                # Dado que el usuario pidió "mismo comportamiento que paso 1", y en paso 1 modificamos el componente...
                # Pero en paso 1 el componente MUESTRA la sala seleccionada y OCULTA el grid (return True).
                # Aquí queremos que `render_step_sala_triaje` haga lo mismo.
                # Si `render_step_sala_triaje` retorna True (seleccionado), entramos en el `if` de arriba en el próximo rerun.
                
                # Botones de acción alternativa (antes de seleccionar sala)
                st.divider()
                col_rej, col_cons = st.columns(2)
                with col_rej:
                    if st.button("🚫 Rechazar Paciente", type="secondary", use_container_width=True):
                        st.session_state.admission_decision_mode = 'reject'
                        st.rerun()
                with col_cons:
                    if st.button("👨‍⚕️ Derivar a Consulta Directa", use_container_width=True):
                        st.session_state.admission_decision_mode = 'derive_consulta'
                        st.rerun()
                
                st.divider()
                if st.button("← Volver a Datos del Paciente"):
                    st.session_state.admission_step = 1
                    st.rerun()

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/admission_view.py</div>', unsafe_allow_html=True)


def _render_completion_summary():
    """Muestra el resumen final tras completar la acción."""
    patient_code = st.session_state.get('admission_patient_code')
    paciente = obtener_paciente_por_codigo(patient_code)
    nombre = f"{paciente.get('nombre')} {paciente.get('apellido1')}"
    
    if st.session_state.get('admission_success'):
        st.success("✅ Paciente registrado y enviado a triaje correctamente.")
        with st.expander("📄 Resumen de Admisión", expanded=True):
            st.markdown(f"**Paciente:** {nombre} (`{patient_code}`)")
            st.markdown(f"**Destino:** {st.session_state.get('admission_sala_triaje_code')}")
            st.markdown("**Estado:** EN_ESPERA_TRIAJE")
    
    elif st.session_state.get('admission_rejection_success'):
        st.warning("🚫 Paciente rechazado correctamente.")
        st.markdown(f"**Motivo:** {st.session_state.get('admission_rejection_reason')}")
    
    if st.button("🔄 Nueva Admisión", type="primary", use_container_width=True):
        _reset_admission_flow()
        st.rerun()


def _execute_assignment(sala_triaje, tipo_destino="triaje", subtipo_destino="espera"):
    """Ejecuta la lógica de asignación."""
    try:
        patient_code = st.session_state.get('admission_patient_code')
        sala_admision = st.session_state.get('admission_sala_admision_code')
        
        flujo_activo = obtener_registro_activo(patient_code)
        if flujo_activo:
            st.error(f"❌ Paciente ya activo en: {flujo_activo.get('sala_code')}")
            return

        # 1. Crear flujo en Admisión
        crear_nuevo_flujo(
            patient_code=patient_code,
            sala_admision_code=sala_admision,
            sala_tipo="admision",
            sala_subtipo="atencion",
            notas="Admisión creada",
            usuario=_get_username()
        )
        # 2. Mover a Destino
        mover_paciente_a_sala(
            patient_code=patient_code,
            sala_destino_code=sala_triaje,
            sala_destino_tipo=tipo_destino,
            sala_destino_subtipo=subtipo_destino,
            nuevo_estado="EN_ESPERA_TRIAJE" if tipo_destino == "triaje" else "EN_ESPERA_CONSULTA",
            notas="Asignado desde admisión",
            usuario=_get_username()
        )
        st.session_state.admission_complete = True
        st.session_state.admission_success = True
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")


def _execute_rejection(motivo):
    """Ejecuta la lógica de rechazo."""
    try:
        patient_code = st.session_state.get('admission_patient_code')
        sala_admision = st.session_state.get('admission_sala_admision_code')
        
        # Crear flujo y rechazar
        crear_nuevo_flujo(patient_code, sala_admision, "admision", "atencion", "Inicio (rechazo)", _get_username())
        rechazar_flow(patient_code, motivo, _get_username())
        
        st.session_state.admission_complete = True
        st.session_state.admission_rejection_success = True
        st.session_state.admission_rejection_reason = motivo
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")


def _reset_admission_flow():
    """Limpia todos los estados del flujo de admisión."""
    keys_to_clear = [
        "admission_sala_admision_code", "admission_patient_data", "admission_patient_validated",
        "admission_patient_code", "admission_edit_mode", "admission_patient_not_found",
        "admission_active_flow", "admission_continue_active", "admission_sala_triaje_code",
        "admission_complete", "admission_success", "admission_rejection_success",
        "admission_rejection_mode", "admission_rejection_reason", "adm_nombre",
        "adm_apellido1", "adm_apellido2", "adm_fecha_nac", "adm_num_ss_input",
        "adm_num_id_input", "admission_step"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
