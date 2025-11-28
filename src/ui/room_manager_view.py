# path: src/ui/room_manager_view.py
# Creado: 2025-11-24
# Actualizado: 2025-11-25 - Añadido loading indicator y corrección de keys duplicadas
# Actualizado: 2025-11-25 - Integrada detección de pacientes en salas inválidas
"""
Vista de Gestión de Salas (Control Tower).
Permite visualizar y gestionar pacientes en todas las salas.
Detecta y muestra alertas de pacientes asignados a salas inexistentes o inactivas.
"""

import streamlit as st
from datetime import datetime
from services.patient_flow_service import (
    obtener_vista_global_salas,
    reassign_patient_flow,
    rechazar_paciente,
    detectar_errores_salas,
)
from ui.config_panel import load_centro_config
from components.common.room_card import render_room_card

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def calculate_wait_time(start_time):
    """Devuelve los minutos transcurridos desde *start_time*.
    Si *start_time* es None o falsy, devuelve 0.
    """
    if not start_time:
        return 0
    delta = datetime.now() - start_time
    return int(delta.total_seconds() / 60)

def render_patient_card(patient, room_code, key_suffix=""):
    """Tarjeta de paciente con botón de gestión.
    Se muestra el nombre, ID y tiempo de espera.
    """
    wait_minutes = calculate_wait_time(patient.get('wait_start'))
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{patient.get('nombre_completo')}**")
            st.caption(f"ID: {patient.get('patient_code')}")
        with c2:
            st.markdown(f"⏱️ **{wait_minutes}** min")
        st.markdown(f"Estado: `{patient.get('estado_flujo')}`")
        # Añadimos key_suffix para evitar duplicados si la misma sala se renderiza en múltiples tabs
        if st.button("⚙️ Gestionar", key=f"manage_{patient['patient_code']}_{room_code}_{key_suffix}"):
            st.session_state.managing_patient = patient
            st.session_state.managing_origin_room = room_code
            st.rerun()

def render_error_alerts():
    """Muestra alertas de pacientes en salas inexistentes o inactivas."""
    errores = detectar_errores_salas()
    
    if not errores:
        return  # No mostrar nada si no hay errores
    
    # Registrar errores nuevos y generar notificaciones
    from services.room_metrics_service import registrar_error_detectado
    from services.notification_service import notify_room_error_detected, NotificationPriority
    
    # Verificar si hay errores nuevos que no están registrados
    if 'last_errors_check' not in st.session_state:
        st.session_state.last_errors_check = set()
    
    current_errors = {(e['patient_code'], e['sala_erronea']) for e in errores}
    new_errors = current_errors - st.session_state.last_errors_check
    
    # Registrar y notificar errores nuevos
    for patient_code, sala_erronea in new_errors:
        error_data = next((e for e in errores if e['patient_code'] == patient_code and e['sala_erronea'] == sala_erronea), None)
        if error_data:
            # Registrar en métricas
            registrar_error_detectado(
                patient_code=error_data['patient_code'],
                sala_erronea=error_data['sala_erronea'],
                motivo_error=error_data['motivo_error'],
                estado=error_data['estado'],
                nombre_completo=error_data['nombre_completo']
            )
            
            # Crear notificación
            priority = NotificationPriority.CRITICAL if error_data['motivo_error'] == "Sala inexistente" else NotificationPriority.HIGH
            notify_room_error_detected(
                patient_code=error_data['patient_code'],
                patient_name=error_data['nombre_completo'],
                sala_erronea=error_data['sala_erronea'],
                motivo=error_data['motivo_error'],
                priority=priority
            )
    
    # Actualizar caché de errores
    st.session_state.last_errors_check = current_errors
    
    st.warning(f"⚠️ **Se detectaron {len(errores)} paciente(s) con asignaciones erróneas**", icon="⚠️")
    
    with st.expander(f"📋 Ver {len(errores)} Incidencia(s) Detectada(s)", expanded=True):
        for i, error in enumerate(errores):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**{error['nombre_completo']}**")
                    st.caption(f"ID: {error['patient_code']}")
                    
                with col2:
                    if error['motivo_error'] == "Sala inexistente":
                        st.error(f"🚫 Sala **{error['sala_erronea']}** no existe")
                    else:
                        st.warning(f"⚠️ Sala **{error['sala_erronea']}** está inactiva")
                    st.caption(f"Estado: {error['estado']}")
                
                with col3:
                    # Tiempo desde entrada
                    wait_time = calculate_wait_time(error.get('entrada'))
                    st.metric("Tiempo", f"{wait_time} min")
                
                # Botón para gestionar este paciente
                if st.button(
                    "⚙️ Corregir Asignación", 
                    key=f"fix_error_{error['patient_code']}_{i}",
                    type="primary",
                    use_container_width=True
                ):
                    # Convertir error a formato de paciente para el panel de gestión
                    st.session_state.managing_patient = {
                        'patient_code': error['patient_code'],
                        'nombre_completo': error['nombre_completo'],
                        'estado_flujo': error['estado'],
                        'created_at': error.get('entrada'),
                        'wait_start': error.get('entrada'),
                    }
                    st.session_state.managing_origin_room = error['sala_erronea']
                    st.rerun()

def render_management_panel():
    """Panel lateral para gestionar el paciente seleccionado."""
    if 'managing_patient' not in st.session_state or not st.session_state.managing_patient:
        return
    p = st.session_state.managing_patient
    origin = st.session_state.managing_origin_room
    st.markdown("---")
    st.subheader(f"🛠️ Gestión de Incidencia: {p.get('nombre_completo')}")
    col_info, col_actions = st.columns([1, 2])
    with col_info:
        st.info(
            f"""
            **ID:** {p.get('patient_code')}
            **Sala Actual:** {origin}
            **Estado:** {p.get('estado_flujo')}
            **Tiempo Total:** {calculate_wait_time(p.get('created_at'))} min
            """
        )
        if st.button("Cerrar Panel", type="secondary"):
            st.session_state.managing_patient = None
            st.rerun()
    with col_actions:
        tab_move, tab_kick = st.tabs(["🔄 Reasignar Sala", "🚫 Alta / Rechazo Forzoso"])
        with tab_move:
            st.write("Mover paciente a otra sala (corrige errores de flujo).")
            
            # Auto-sugerencia de salas
            from services.room_suggestion_service import get_top_suggestions, format_suggestion_display
            
            suggestions = get_top_suggestions(origin, top_n=3)
            
            if suggestions:
                st.markdown("**💡 Salas Sugeridas:** (basadas en tipo, disponibilidad y ocupación)")
                
                # Mostrar top 3 sugerencias
                for i, sug in enumerate(suggestions, 1):
                    sala_sug = sug['sala']
                    with st.container(border=True):
                        col_sug_info, col_sug_btn = st.columns([4, 1])
                        with col_sug_info:
                            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else "•"
                            st.markdown(f"{medal} **{sala_sug['nombre']}** `{sala_sug['codigo']}`")
                            reasons_text = " | ".join(sug['reasons'])
                            st.caption(f"Score: {sug['score']} - {reasons_text}")
                        with col_sug_btn:
                            if st.button("Seleccionar", key=f"sug_{sala_sug['codigo']}", type="secondary"):
                                st.session_state['suggested_room'] = sala_sug['codigo']
                                st.rerun()
                
                st.markdown("---")
            
            # Selector manual
            config = load_centro_config()
            all_rooms = config.get('salas', [])
            target_rooms = [r for r in all_rooms if r['codigo'] != origin and r.get('activa', True)]
            
            # Pre-seleccionar si hay sugerencia
            default_index = 0
            if 'suggested_room' in st.session_state and st.session_state.suggested_room:
                try:
                    default_index = [r['codigo'] for r in target_rooms].index(st.session_state.suggested_room)
                    del st.session_state['suggested_room']  # Limpiar después de usar
                except (ValueError, IndexError):
                    pass
            
            target_room_code = st.selectbox(
                "Sala de Destino (Manual)",
                options=[r['codigo'] for r in target_rooms],
                index=default_index,
                format_func=lambda x: next(
                    f"{r['nombre']} ({r['tipo']}) - {r.get('plazas_disponibles', '?')} plazas" for r in target_rooms if r['codigo'] == x
                ),
            )
            
            if st.button("Confirmar Reasignación", type="primary"):
                target_type = next((r['tipo'] for r in target_rooms if r['codigo'] == target_room_code), None)
                success = False
                if target_type == 'triaje':
                    success = reassign_patient_flow(p['patient_code'], new_sala_triaje_code=target_room_code)
                elif target_type == 'admision':
                    success = reassign_patient_flow(p['patient_code'], new_sala_admision_code=target_room_code)
                elif target_type == 'espera':
                    success = reassign_patient_flow(p['patient_code'], new_sala_espera_code=target_room_code)
                elif target_type in ['box', 'consulta_ingreso']:
                    success = reassign_patient_flow(p['patient_code'], new_sala_atencion_code=target_room_code)
                else:
                    st.warning(f"Reasignación a salas de tipo '{target_type}' no soportada.")
                
                if success:
                    # Notificar resolución
                    from services.notification_service import notify_room_error_resolved
                    notify_room_error_resolved(
                        patient_code=p['patient_code'],
                        patient_name=p.get('nombre_completo', 'N/A'),
                        sala_antigua=origin,
                        sala_nueva=target_room_code
                    )
                    
                    # Marcar error como resuelto en métricas
                    from services.room_metrics_service import marcar_error_resuelto
                    marcar_error_resuelto(
                        patient_code=p['patient_code'],
                        sala_erronea=origin,
                        resolution_type="reasignado",
                        new_sala=target_room_code
                    )
                    
                    st.success(f"Paciente movido a {target_room_code}")
                    st.session_state.managing_patient = None
                    st.rerun()
                else:
                    st.error("Error al reasignar.")
        with tab_kick:
            st.write("Finalizar flujo del paciente inmediatamente.")
            reason = st.text_input("Motivo (Obligatorio)", placeholder="Ej: Error administrativo, Paciente se marchó")
            if st.button("Forzar Salida", type="primary", disabled=not reason):
                if rechazar_paciente(p['patient_code'], f"ADMIN_FORCE: {reason}"):
                    st.success("Paciente eliminado del flujo activo.")
                    st.session_state.managing_patient = None
                    st.rerun()
                else:
                    st.error("Error al finalizar flujo.")

def mostrar_gestor_salas():
    """Renderiza la vista principal del gestor de salas."""
    # Header con botón de refresco
    col_title, col_refresh = st.columns([4, 1])
    with col_title:
        st.header(":material/dashboard: Tablero de Control de Salas")
    with col_refresh:
        if st.button("🔄 Actualizar Datos", type="primary", use_container_width=True):
            st.rerun()
    
    st.markdown("Visión global del estado del centro y herramientas de corrección.")

    # Cargar datos primero
    vista_global = obtener_vista_global_salas()
    config = load_centro_config()
    all_rooms = config.get('salas', [])
    errores = detectar_errores_salas()
    
    # Métricas rápidas
    total_pacientes = sum(len(pacientes) for pacientes in vista_global.values())
    salas_activas = len([s for s in all_rooms if s.get('activa', True)])
    total_errores = len(errores)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("👥 Pacientes Activos", total_pacientes)
    with metric_col2:
        st.metric("🏥 Salas Activas", salas_activas)
    with metric_col3:
        if total_errores > 0:
            st.metric("⚠️ Errores Detectados", total_errores, delta=None, delta_color="inverse")
        else:
            st.metric("✅ Estado", "Sin errores")
    with metric_col4:
        from datetime import datetime
        st.metric("🕐 Última actualización", datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")

    # 1. Alertas de errores (pacientes en salas inexistentes/inactivas)
    if errores:
        render_error_alerts()

    # 2. Panel de gestión (si hay paciente seleccionado)
    render_management_panel()

    # 3. Pestañas por zona
    tab_adm, tab_tri, tab_box, tab_ing = st.tabs([
        "Admisión",
        "Triaje",
        "Boxes/Consultas",
        "Ingreso/Consulta",
    ])

    def render_zone(zone_type, container):
        """Filtra y muestra las salas de *zone_type*.
        Para el tipo "consulta_ingreso" también se incluyen las salas cuyo
        subtipo es "espera" (salas de espera).
        """
        with container:
            zone_rooms = [
                r for r in all_rooms
                if r.get('activa', True) and r.get('tipo') == zone_type
            ]
            if not zone_rooms:
                st.info(f"No hay salas de {zone_type} configuradas.")
                return
            
            # Calcular columnas dinámicamente (máximo 4 por fila)
            num_rooms = len(zone_rooms)
            cols_per_row = min(4, num_rooms) if num_rooms > 0 else 1
            
            # Iterar sobre las salas y mostrarlas en grid
            for i, room in enumerate(zone_rooms):
                # Iniciar nueva fila si es necesario
                if i % cols_per_row == 0:
                    cols = st.columns(cols_per_row)
                
                col_idx = i % cols_per_row
                code = room['codigo']
                patients = vista_global.get(code, [])
                
                with cols[col_idx]:
                    render_room_card(
                        sala=room,
                        is_selected=False,
                        button_key=f"room_view_{code}_{zone_type}",
                        show_select_button=False,
                        pacientes=patients,
                        # Pasamos key_suffix para evitar duplicados
                        render_patient_func=lambda p, c: render_patient_card(p, c, key_suffix=zone_type),
                    )

    render_zone("admision", tab_adm)
    render_zone("triaje", tab_tri)
    render_zone("box", tab_box)
    render_zone("consulta_ingreso", tab_ing)
