# path: src/components/common/active_flow_manager.py
# Creado: 2025-11-25
"""
Componente reutilizable para gestionar pacientes con flujo activo (conflictos).
Permite: Continuar, Reasignar, Rechazar o Cancelar.
"""
import streamlit as st
from components.common.rejection_form import render_rejection_form
from services.patient_flow_service import rechazar_paciente

def render_active_flow_manager(
    paciente: dict,
    flujo: dict,
    key_prefix: str,
    on_continue: callable,
    on_cancel: callable,
    on_reassign_success: callable,
    render_reassign_ui: callable = None,
    reassign_mode_label: str = "Reasignar Sala",
    reassign_help: str = "Cierra el flujo actual y permite asignar una nueva sala"
):
    """
    Renderiza el gestor de conflictos de flujo activo.
    
    Args:
        paciente: Datos del paciente.
        flujo: Datos del flujo activo.
        key_prefix: Prefijo para claves de Streamlit.
        on_continue: Callback al pulsar Continuar.
        on_cancel: Callback al pulsar Cancelar.
        on_reassign_success: Callback al completar la reasignación (si usa UI default) o para notificar éxito.
        render_reassign_ui: Función opcional para renderizar UI personalizada de reasignación.
                            Si es None, muestra confirmación simple de cierre de flujo.
        reassign_mode_label: Etiqueta del botón de reasignar.
        reassign_help: Ayuda del botón de reasignar.
    """
    
    # Estado local para la acción seleccionada
    action_key = f"{key_prefix}_action"
    if action_key not in st.session_state:
        st.session_state[action_key] = None # 'continue', 'reassign', 'reject', None

    # --- INFORMACIÓN DEL CONFLICTO ---
    st.warning("⚠️ Este paciente ya tiene un proceso activo en el sistema")
    
    with st.container(border=True):
        st.markdown("### 📋 Información del Proceso Activo")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Paciente:** {paciente.get('nombre')} {paciente.get('apellido1')}")
            st.markdown(f"**Código:** `{paciente.get('patient_code')}`")
            st.markdown(f"**Estado:** {flujo.get('estado', 'N/A')}")
        
        with col2:
            sala_actual = (flujo.get('sala_atencion_code') or 
                         flujo.get('sala_destino_code') or 
                         flujo.get('sala_triaje_code') or 
                         flujo.get('sala_admision_code'))
            st.markdown(f"**Sala Actual:** {sala_actual}")
            if 'created_at_flow' in flujo:
                # Manejar fecha si es string o datetime
                fecha = flujo['created_at_flow']
                if hasattr(fecha, 'strftime'):
                    fecha_str = fecha.strftime('%d/%m/%Y %H:%M')
                else:
                    fecha_str = str(fecha)
                st.markdown(f"**Inicio:** {fecha_str}")

    # --- SELECTOR DE ACCIÓN ---
    if st.session_state[action_key] is None:
        st.markdown("**¿Qué desea hacer?**")
        
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            if st.button("✅ Continuar Proceso", key=f"{key_prefix}_btn_cont", type="secondary", use_container_width=True, help="Mantiene el flujo actual sin cambios"):
                st.session_state[action_key] = 'continue'
                st.rerun()
        
        with c2:
            if st.button(f"🔄 {reassign_mode_label}", key=f"{key_prefix}_btn_reassign", type="primary", use_container_width=True, help=reassign_help):
                st.session_state[action_key] = 'reassign'
                st.rerun()

        with c3:
            if st.button("🚫 Rechazar", key=f"{key_prefix}_btn_reject", type="secondary", use_container_width=True, help="Cierra el flujo actual y marca como rechazado"):
                st.session_state[action_key] = 'reject'
                st.rerun()
        
        with c4:
            if st.button("❌ Cancelar", key=f"{key_prefix}_btn_cancel", use_container_width=True, help="Cancela la operación actual"):
                on_cancel()

    # --- ACCIONES EXTRA (Impresión) ---
    c_print, _ = st.columns([1, 3])
    with c_print:
        if st.button("🖨️ Imprimir Ticket", key=f"{key_prefix}_btn_print_ticket", use_container_width=True):
            st.session_state[f"{key_prefix}_show_ticket"] = True
            st.rerun()

    # Modal Impresión local en Active Flow Manager
    if st.session_state.get(f"{key_prefix}_show_ticket", False):
        @st.dialog("🖨️ Ticket de Admisión")
        def print_ticket_dialog_afm():
            from components.admission.patient_ticket import render_ticket_modal
            render_ticket_modal(paciente)
            if st.button("Cerrar", key=f"{key_prefix}_close_ticket"):
                st.session_state[f"{key_prefix}_show_ticket"] = False
                st.rerun()

        try:
            print_ticket_dialog_afm()
        except:
            # Si hay conflicto de diálogos, ignorar silenciosamente o intentar mostrar advertencia
            # En Streamlit 1.34+ no se permiten multiples dialogs.
            # Si falla, simplemente no lo abre en este ciclo.
            st.warning("⚠️ No se puede abrir la ventana de impresión porque hay otro diálogo activo.")
            if st.button("Reintentar impresión", key=f"{key_prefix}_retry_print"):
                st.rerun()
        
    # --- LÓGICA DE ACCIONES ---
    
    # 1. CONTINUAR
    if st.session_state[action_key] == 'continue':
        st.divider()
        st.info("ℹ️ Ha decidido continuar con el proceso actual.")
        
        # Ejecutar callback de continuación
        # Nota: A veces queremos mostrar algo antes de ejecutar, pero por simplicidad ejecutamos directo o mostramos botón de volver
        on_continue()
        
        if st.button("🔙 Volver a Selección", key=f"{key_prefix}_back_cont", use_container_width=True):
            st.session_state[action_key] = None
            st.rerun()

    # 2. REASIGNAR
    elif st.session_state[action_key] == 'reassign':
        st.divider()
        
        if render_reassign_ui:
            # UI Personalizada (ej: Grid de salas en Triaje)
            render_reassign_ui()
            
            if st.button("Cancelar Reasignación", key=f"{key_prefix}_cancel_reassign_custom"):
                st.session_state[action_key] = None
                st.rerun()
        else:
            # UI Por defecto (Confirmación simple - Admisión)
            st.info("ℹ️ Se cerrará el flujo actual para permitir una nueva asignación.")
            
            col_conf, col_canc = st.columns(2)
            with col_conf:
                if st.button("Confirmar Reasignación", key=f"{key_prefix}_conf_reassign", type="primary", use_container_width=True):
                    try:
                        rechazar_paciente(paciente['patient_code'], "Reasignación administrativa")
                        st.session_state[action_key] = None
                        on_reassign_success()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            with col_canc:
                if st.button("Cancelar", key=f"{key_prefix}_cancel_reassign", use_container_width=True):
                    st.session_state[action_key] = None
                    st.rerun()

    # 3. RECHAZAR
    elif st.session_state[action_key] == 'reject':
        st.divider()
        
        def _on_reject_confirm(motivo):
            try:
                rechazar_paciente(paciente['patient_code'], motivo)
                st.session_state[action_key] = None
                st.success("✅ Paciente rechazado y flujo cerrado correctamente.")
                # Callback de éxito de rechazo (usualmente implica limpiar estado padre)
                on_cancel() # En muchos casos es volver al inicio, o podemos pasar otro callback
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

        def _on_reject_cancel():
            st.session_state[action_key] = None
            st.rerun()

        render_rejection_form(
            key_prefix=f"{key_prefix}_reject_form",
            on_confirm=_on_reject_confirm,
            on_cancel=_on_reject_cancel
        )

        st.markdown('<div class="debug-footer">src/components/common/active_flow_manager.py</div>', unsafe_allow_html=True)
