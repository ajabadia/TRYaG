# path: src/ui/components/waiting_list.py
import streamlit as st
from datetime import datetime
from services.queue_manager import sort_queue, get_wait_time_alert
from services.patient_flow_service import iniciar_atencion_box

def render_waiting_list_component(patients: list, context: str = "dashboard", box_code: str = None):
    """
    Renderiza una lista de pacientes en espera.
    
    Args:
        patients: Lista de diccionarios de pacientes.
        context: 'dashboard' (vista general) o 'attention' (para llamar a box).
        box_code: Código del box si el contexto es 'attention'.
    """
    if not patients:
        st.info("✅ No hay pacientes en espera.")
        return

    # Ordenar por prioridad
    sorted_patients = sort_queue(patients)
    
    # Renderizar lista usando el componente unificado
    from ui.components.common.patient_card import render_patient_card

    for p in sorted_patients:
        # Definir acciones según contexto
        actions = []
        
        if context == "attention" and box_code:
            def on_call(pat):
                if iniciar_atencion_box(pat['patient_code'], box_code):
                    st.toast(f"Llamando a {pat['nombre_completo']}...", icon="📢")
                    st.session_state.active_patient_code = pat['patient_code']
                    st.rerun()
                else:
                    st.error("Error al asignar.")
            
            actions.append({
                'label': '📢 LLAMAR',
                'key': 'call',
                'type': 'primary',
                'on_click': on_call
            })
            
        elif context == "dashboard":
            def on_reeval(pat):
                # Lógica de reevaluación
                st.session_state.triage_patient = pat
                st.session_state.is_reevaluation = True
                st.session_state.triage_step = 1
                st.toast(f"Paciente {pat['patient_code']} cargado para re-evaluación. Vaya a la pestaña 'Triaje'.", icon="✅")
                # No podemos cambiar de tab programáticamente con st.tabs, así que avisamos al usuario
            
            actions.append({
                'label': '🔄 Re-evaluar',
                'key': 'reeval',
                'type': 'secondary',
                'on_click': on_reeval
            })

        render_patient_card(
            patient=p,
            actions=actions,
            show_triage_level=True,
            show_wait_time=True,
            highlight_alert=True,
            key_prefix=f"wl_{context}"
        )

    st.caption("src/ui/components/waiting_list.py")
