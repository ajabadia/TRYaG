# path: src/components/admission/step_confirmation.py
# Creado: 2025-11-24
"""
Paso 4 del flujo de admisión: Confirmación y registro final.
"""
import streamlit as st
from services.patient_flow_service import (
    crear_flujo_paciente,
    rechazar_paciente,
    obtener_flujo_activo,
)
from services.patient_service import calcular_edad, obtener_paciente_por_codigo
from datetime import datetime
from services.permissions_service import get_current_user

def _get_username():
    user = get_current_user()
    return user.get("username", "unknown") if user else "unknown"

def render_step_confirmation():
    """
    Renderiza la confirmación final y registro del paciente.
    """
    st.subheader("4️⃣ Confirmación de Admisión")
    
    # Inicializar estados
    if 'admission_complete' not in st.session_state:
        st.session_state.admission_complete = False
    if 'admission_rejection_mode' not in st.session_state:
        st.session_state.admission_rejection_mode = False
    
    # Obtener datos para el resumen
    patient_code = st.session_state.get('admission_patient_code')
    sala_admision = st.session_state.get('admission_sala_admision_code')
    sala_triaje = st.session_state.get('admission_sala_triaje_code')
    
    if not patient_code:
        st.error("❌ No hay paciente validado.")
        return
    
    # Obtener datos completos del paciente
    paciente = obtener_paciente_por_codigo(patient_code)
    if not paciente:
        st.error("❌ No se pudo cargar la información del paciente.")
        return
    
    edad = calcular_edad(paciente['fecha_nacimiento'])
    nombre_completo = f"{paciente['nombre']} {paciente['apellido1']} {paciente.get('apellido2', '')}"
    
    # --- Si ya se completó la admisión ---
    if st.session_state.admission_complete:
        if st.session_state.get('admission_success'):
            st.success("✅ Paciente registrado y enviado a triaje correctamente.")
            
            with st.expander("📄 Resumen de Admisión", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Paciente:** {nombre_completo}")
                    st.markdown(f"**Código:** `{patient_code}`")
                    st.markdown(f"**Edad:** {edad} años")
                with col2:
                    st.markdown(f"**Sala Admisión:** {sala_admision}")
                    st.markdown(f"**Sala Triaje:** {sala_triaje}")
                    st.markdown("**Estado:** EN_ESPERA_TRIAJE")
        
        elif st.session_state.get('admission_rejection_success'):
            st.warning("🚫 Paciente rechazado correctamente.")
            st.markdown(f"**Motivo:** {st.session_state.get('admission_rejection_reason', 'No especificado')}")
        
        st.divider()
        if st.button("🔄 Nueva Admisión", type="primary", use_container_width=True):
            _reset_admission_flow()
            st.rerun()
        
        return
    
    # --- Modo rechazo ---
    if st.session_state.admission_rejection_mode:
        st.warning("⚠️ Proceso de rechazo de paciente")
        
        motivo = st.text_input("Motivo del rechazo *", key="adm_motivo_rechazo")
        
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("🚨 Confirmar Rechazo", type="primary", use_container_width=True):
                if not motivo:
                    st.error("❌ Debe especificar un motivo.")
                else:
                    try:
                        from services.flow_manager import crear_nuevo_flujo, rechazar_paciente as rechazar_flow
                        
                        # Crear flujo inicial para registrar la visita
                        crear_nuevo_flujo(
                            patient_code=patient_code,
                            sala_admision_code=sala_admision,
                            sala_tipo="admision",
                            sala_subtipo="atencion",
                            notas="Inicio de admisión (rechazada)",
                            usuario=_get_username()
                        )
                        
                        # Rechazar inmediatamente
                        rechazar_flow(
                            patient_code=patient_code,
                            motivo=motivo,
                            usuario=_get_username()
                        )
                        st.session_state.admission_complete = True
                        st.session_state.admission_rejection_success = True
                        st.session_state.admission_rejection_reason = motivo
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al rechazar: {str(e)}")
        
        with col_cancel:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.admission_rejection_mode = False
                st.rerun()
        
        return
    
    # --- Resumen previo a confirmación ---
    with st.container(border=True):
        st.markdown("### 📋 Resumen de Admisión")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Paciente:** {nombre_completo}")
            st.markdown(f"**Código:** `{patient_code}`")
            st.markdown(f"**Edad:** {edad} años")
            st.markdown(f"**SS:** {paciente.get('num_ss', 'No especificado')}")
        
        with col2:
            st.markdown(f"**Sala Admisión:** {sala_admision}")
            st.markdown(f"**Sala Triaje:** {sala_triaje}")
            st.markdown(f"**ID ({paciente.get('tipo_identificacion')}):** {paciente.get('num_identificacion')}")
    
    st.divider()
    
    # --- Botones de acción ---
    col_confirm, col_reject = st.columns([1, 1])
    
    with col_confirm:
        if st.button("📋 Registrar y Enviar a Triaje", type="primary", use_container_width=True):
            # Verificar si ya tiene flujo activo
            from services.flow_manager import obtener_registro_activo, crear_nuevo_flujo, mover_paciente_a_sala
            
            flujo_activo = obtener_registro_activo(patient_code)
            
            if flujo_activo:
                st.error(f"❌ El paciente ya tiene un proceso activo en sala: {flujo_activo.get('sala_code')}")
                st.info("💡 Debe finalizar el proceso anterior antes de crear uno nuevo.")
            else:
                try:
                    # 1. Crear flujo inicial en Admisión
                    flow_id = crear_nuevo_flujo(
                        patient_code=patient_code,
                        sala_admision_code=sala_admision,
                        sala_tipo="admision",
                        sala_subtipo="atencion",
                        notas="Admisión creada",
                        usuario=_get_username()
                    )
                    
                    # 2. Mover a Sala de Espera de Triaje seleccionada
                    mover_paciente_a_sala(
                        patient_code=patient_code,
                        sala_destino_code=sala_triaje,
                        sala_destino_tipo="triaje",
                        sala_destino_subtipo="espera",
                        nuevo_estado="EN_ESPERA_TRIAJE",
                        notas="Asignado desde admisión",
                        usuario=_get_username()
                    )
                    
                    st.session_state.admission_complete = True
                    st.session_state.admission_success = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al registrar: {str(e)}")
    
    with col_reject:
        if st.button("🚫 Rechazar Paciente", type="secondary", use_container_width=True):
            st.session_state.admission_rejection_mode = True
            st.rerun()


def _reset_admission_flow():
    """Limpia todos los estados del flujo de admisión."""
    keys_to_clear = [
        "admission_sala_admision_code",
        "admission_patient_data",
        "admission_patient_validated",
        "admission_patient_code",
        "admission_edit_mode",
        "admission_patient_not_found",
        "admission_active_flow",
        "admission_continue_active",
        "admission_sala_triaje_code",
        "admission_complete",
        "admission_success",
        "admission_rejection_success",
        "admission_rejection_mode",
        "admission_rejection_reason",
        "adm_nombre",
        "adm_apellido1",
        "adm_apellido2",
        "adm_fecha_nac",
        "adm_num_ss_input",
        "adm_num_id_input",
        "admission_step",
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

            st.markdown('<div class="debug-footer">src/components/admission/step_confirmation.py</div>', unsafe_allow_html=True)
