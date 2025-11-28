# path: src/components/triage/step_patient_selection.py
# Creado: 2025-11-24
# Última modificación: 2025-11-24
"""
Paso 2 del Asistente de Triaje: Selección de Paciente.
"""
import streamlit as st
from services.patient_flow_service import obtener_pacientes_en_espera
from services.patient_service import calcular_edad
from datetime import datetime
from services.permissions_service import get_current_user

def _get_username():
    user = get_current_user()
    return user.get("username", "unknown") if user else "unknown"

def render_step_patient_selection() -> bool:
    """
    Renderiza la lista de pacientes en espera para la sala seleccionada.
    
    Returns:
        bool: True si hay paciente seleccionado, False en caso contrario.
    """
    st.subheader("2️⃣ Selección de Paciente")
    
    room_code = st.session_state.get('triage_room_code')
    if not room_code:
        st.warning("⚠️ No se ha seleccionado sala.")
        return False

    # 1. Obtener configuración de la sala seleccionada
    from services.room_service import obtener_sala_por_codigo
    sala_config = obtener_sala_por_codigo(room_code)
    
    if not sala_config:
        st.error(f"❌ No se encontró configuración para la sala {room_code}")
        return False

    # --- GESTIÓN DE ACCIONES (REASIGNAR / RECHAZAR) ---
    if 'triage_action_target' not in st.session_state:
        st.session_state.triage_action_target = None
    if 'triage_action_type' not in st.session_state:
        st.session_state.triage_action_type = None

    # Si hay una acción en curso, mostramos su UI y ocultamos la lista
    if st.session_state.triage_action_target:
        target_p = st.session_state.triage_action_target
        action_type = st.session_state.triage_action_type
        
        st.divider()
        st.markdown(f"### Gestionar Paciente: {target_p.get('nombre')} {target_p.get('apellido1')}")
        
        if action_type == 'reassign':
            st.info("Seleccione la sala de espera de destino:")
            from services.room_service import obtener_salas_por_tipo
            from components.common.room_card import render_room_grid
            from services.flow_manager import mover_paciente_a_sala
            
            # Obtener salas de espera de triaje
            salas_espera = [s for s in obtener_salas_por_tipo('triaje') if s.get('subtipo') == 'espera']
            
            selected_code = render_room_grid(
                salas=salas_espera,
                selected_code=None,
                button_key_prefix="reassign_triage_grid",
                cols_per_row=3
            )
            
            if selected_code:
                try:
                    mover_paciente_a_sala(
                        patient_code=target_p['patient_code'],
                        sala_destino_code=selected_code,
                        sala_destino_tipo="triaje",
                        sala_destino_subtipo="espera",
                        nuevo_estado="EN_ESPERA_TRIAJE",
                        notas=f"Reasignado desde triaje {room_code}",
                        usuario=_get_username()
                    )
                    st.success(f"✅ Paciente reasignado a {selected_code}")
                    st.session_state.triage_action_target = None
                    st.session_state.triage_action_type = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al mover: {e}")
            
            if st.button("🔙 Cancelar"):
                st.session_state.triage_action_target = None
                st.session_state.triage_action_type = None
                st.rerun()

        elif action_type == 'reject':
            st.warning("¿Está seguro de que desea rechazar a este paciente? Se cerrará su flujo actual.")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("🗑️ Sí, Rechazar", type="primary", use_container_width=True):
                    from services.flow_manager import rechazar_paciente
                    try:
                        success, msg = rechazar_paciente(
                            patient_code=target_p['patient_code'],
                            motivo="Rechazado en triaje",
                            usuario=_get_username()
                        )
                        if success:
                            st.success("✅ Paciente rechazado correctamente")
                            st.session_state.triage_action_target = None
                            st.session_state.triage_action_type = None
                            st.rerun()
                        else:
                            st.error(f"Error al rechazar: {msg}")
                    except Exception as e:
                        st.error(f"Error al rechazar: {e}")
            with col_cancel:
                if st.button("Cancelar", use_container_width=True):
                    st.session_state.triage_action_target = None
                    st.session_state.triage_action_type = None
                    st.rerun()
        
        return False

    # --- RECUPERACIÓN DE PACIENTES ---
    from services.flow_manager import obtener_pacientes_en_sala, mover_paciente_a_sala
    from services.patient_service import obtener_paciente_por_codigo, calcular_edad
    
    lista_pacientes = []
    blocking_patient = None
    
    # 1. Paciente en sala (Prioritario)
    pacientes_en_atencion = obtener_pacientes_en_sala(room_code)
    if pacientes_en_atencion:
        flujo_activo = pacientes_en_atencion[0]
        datos_paciente = obtener_paciente_por_codigo(flujo_activo['patient_code'])
        if datos_paciente:
            p_full = {**datos_paciente, **flujo_activo}
            p_full['is_in_room'] = True
            p_full['sala_espera_origen'] = room_code 
            lista_pacientes.append(p_full)
            blocking_patient = p_full
            
            st.warning(f"⚠️ La sala está ocupada por **{p_full.get('nombre')} {p_full.get('apellido1')}**. Debe finalizar su atención o reasignarlo para atender a otros.")

    # 2. Pacientes en espera
    salas_espera = sala_config.get('salas_espera_asociadas', [])
    if not salas_espera:
        from services.room_service import obtener_salas_por_tipo
        salas_triaje_espera = [s['codigo'] for s in obtener_salas_por_tipo('triaje') if s.get('subtipo') == 'espera']
        salas_espera = salas_triaje_espera if salas_triaje_espera else []

    for sala_esp in salas_espera:
        flujos = obtener_pacientes_en_sala(sala_esp)
        for flujo in flujos:
            datos_paciente = obtener_paciente_por_codigo(flujo['patient_code'])
            if datos_paciente:
                p_full = {**datos_paciente, **flujo}
                p_full['sala_espera_origen'] = sala_esp
                p_full['is_in_room'] = False
                lista_pacientes.append(p_full)
    
    if not lista_pacientes:
        st.info(f"ℹ️ No hay pacientes en espera ni en atención.")
        if st.button("🔄 Actualizar lista", use_container_width=True):
            st.rerun()
        return False

    st.markdown(f"**Pacientes:** {len(lista_pacientes)}")
    st.divider()
    
    # Inicializar estado seleccionado
    if 'triage_patient' not in st.session_state:
        st.session_state.triage_patient = None
    
    selected_patient = st.session_state.triage_patient
    
    # Renderizar lista
    from components.common.patient_selection_card import render_patient_selection_card
    
    for p in lista_pacientes:
        is_in_room = p.get('is_in_room', False)
        
        # Bloquear "Atender" si hay alguien en sala y NO es este paciente
        disable_attend = (blocking_patient is not None) and (not is_in_room)
        
        is_selected = bool(selected_patient and 
                     selected_patient.get('patient_code') == p.get('patient_code'))
        
        action = render_patient_selection_card(
            p, 
            is_selected=is_selected, 
            key_prefix="triage",
            is_in_room=is_in_room,
            disable_attend=disable_attend,
            show_actions=True
        )
        
        if action == 'attend':
            if is_in_room:
                # Ya está en sala, solo seleccionamos
                st.session_state.triage_patient = p
            else:
                # Mover a sala
                try:
                    mover_paciente_a_sala(
                        patient_code=p.get('patient_code'),
                        sala_destino_code=room_code,
                        sala_destino_tipo="triaje",
                        sala_destino_subtipo="atencion",
                        nuevo_estado="EN_TRIAJE",
                        notas=f"Atendido en {room_code}",
                        usuario=_get_username()
                    )
                    st.session_state.triage_patient = p
                except Exception as e:
                    st.error(f"Error al mover paciente: {e}")
                    continue

            # Pre-rellenar edad
            if 'fecha_nacimiento' in p:
                fn = p['fecha_nacimiento']
                if isinstance(fn, str):
                    try: fn = datetime.fromisoformat(fn)
                    except: pass
                st.session_state.datos_paciente['edad'] = calcular_edad(fn)
            
            st.rerun()
            
        elif action == 'reject':
            st.session_state.triage_action_target = p
            st.session_state.triage_action_type = 'reject'
            st.rerun()
            
        elif action == 'reassign':
            st.session_state.triage_action_target = p
            st.session_state.triage_action_type = 'reassign'
            st.rerun()

    # Mostrar paciente seleccionado y permitir avanzar
    if selected_patient:
        st.divider()
        st.info(f"👤 Atendiendo a: **{selected_patient.get('nombre')} {selected_patient.get('apellido1')}** (ID: {selected_patient.get('patient_code')})")
        return True
        
    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/step_patient_selection.py</div>', unsafe_allow_html=True)
    return False
