# path: src/components/boxes/step_patient_selection.py
# Creado: 2025-11-24
"""
Paso 2 de Gestión de Boxes: Selección de Paciente en Espera.
"""
import streamlit as st
from datetime import datetime
from services.room_service import obtener_sala_por_codigo, obtener_salas_por_tipo
from services.flow_manager import obtener_pacientes_en_sala, mover_paciente_a_sala
from services.patient_service import obtener_paciente_por_codigo, calcular_edad
from services.permissions_service import get_current_user

def _get_username():
    user = get_current_user()
    return user.get("username", "unknown") if user else "unknown"

def render_step_patient_selection() -> bool:
    """
    Muestra pacientes en las salas de espera asociadas y permite llamarlos.
    
    Returns:
        bool: True si se ha seleccionado un paciente (pasa al siguiente paso), False si no.
    """
    st.subheader("2️⃣ Pacientes en Espera")
    
    room_code = st.session_state.get('boxes_room_code')
    if not room_code:
        st.warning("⚠️ No se ha seleccionado sala.")
        return False

    # 1. Obtener configuración de la sala actual
    sala_config = obtener_sala_por_codigo(room_code)
    if not sala_config:
        st.error(f"❌ Error de configuración: Sala {room_code} no encontrada.")
        return False
        
    # 2. Obtener salas de espera asociadas
    salas_espera = sala_config.get('salas_espera_asociadas', [])
    
    if not salas_espera:
        # Fallback: Buscar todas las salas de espera de boxes
        salas_boxes_espera = [s['codigo'] for s in obtener_salas_por_tipo('box') if s.get('subtipo') == 'espera']
        if salas_boxes_espera:
            salas_espera = salas_boxes_espera
        else:
            st.warning("⚠️ Esta consulta no tiene salas de espera asociadas.")
            return False

    # 3. Obtener pacientes de todas las salas de espera Y de la propia sala (derivados directos)
    pacientes_en_espera = []
    
    # Mapa de nombres de salas
    from ui.config.config_loader import load_centro_config
    config = load_centro_config()
    salas_map = {s['codigo']: s.get('nombre', s['codigo']) for s in config.get('salas', [])}
    
    # Lista de salas a consultar: Espera + Propia Sala
    salas_a_consultar = list(salas_espera)
    if room_code not in salas_a_consultar:
        salas_a_consultar.append(room_code)

    for sala_code_iter in salas_a_consultar:
        flujos = obtener_pacientes_en_sala(sala_code_iter)
        for flujo in flujos:
            # Filtrar: Si es la propia sala, excluir los que ya están en atención
            # (Solo queremos ver los que están esperando o derivados)
            if sala_code_iter == room_code and flujo.get('estado') == 'EN_ATENCION_BOX':
                continue
                
            datos_paciente = obtener_paciente_por_codigo(flujo['patient_code'])
            if datos_paciente:
                paciente_completo = {**datos_paciente, **flujo}
                paciente_completo['sala_espera_origen'] = sala_code_iter
                paciente_completo['sala_nombre'] = salas_map.get(sala_code_iter, sala_code_iter)
                pacientes_en_espera.append(paciente_completo)
    
    if not pacientes_en_espera:
        st.info(f"ℹ️ No hay pacientes pendientes en: {', '.join(salas_a_consultar)}")
        if st.button("🔄 Actualizar lista", use_container_width=True, key="btn_refresh_patient_list"):
            st.rerun()
        return False

    st.markdown(f"**Pacientes pendientes:** {len(pacientes_en_espera)}")
    
    # Mostrar lista de pacientes
    from ui.components.common.patient_card import render_patient_card
    
    for p in pacientes_en_espera:
        # Definir callback para llamar al paciente
        def on_call(patient):
            _llamar_paciente(patient, room_code)

        actions = [{
            "label": "Llamar",
            "key": "call",
            "type": "primary",
            "on_click": on_call
        }]

        render_patient_card(
            patient=p,
            actions=actions,
            show_triage_level=True,
            show_wait_time=True,
            show_location=True,
            key_prefix="boxes_sel"
        )
            
    return False


def _llamar_paciente(paciente, room_code):
    """Mueve al paciente a la sala de atención."""
    try:
        mover_paciente_a_sala(
            patient_code=paciente.get('patient_code'),
            sala_destino_code=room_code,
            sala_destino_tipo="box",
            sala_destino_subtipo="atencion",
            nuevo_estado="EN_ATENCION_BOX",
            notas=f"Llamado a consulta {room_code}",
            usuario=_get_username()
        )
        st.success(f"Llamando a {paciente.get('nombre')}...")
        st.rerun()
    except Exception as e:
        st.error(f"Error al llamar paciente: {e}")
