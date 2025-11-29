# path: src/ui/components/common/patient_card.py
import streamlit as st
from datetime import datetime

def render_patient_card(
    patient: dict,
    actions: list = None,
    show_triage_level: bool = True,
    show_wait_time: bool = True,
    show_location: bool = False,
    highlight_alert: bool = True,
    key_prefix: str = ""
):
    """
    Renderiza una tarjeta de paciente unificada y flexible.
    
    Args:
        patient (dict): Datos del paciente.
        actions (list): Lista de dicts con configuración de botones:
                        [{'label': 'Llamar', 'key': 'call', 'on_click': func, 'type': 'primary'}]
        show_triage_level (bool): Mostrar badge de nivel de triaje.
        show_wait_time (bool): Mostrar tiempo de espera.
        show_location (bool): Mostrar sala actual/origen.
        highlight_alert (bool): Cambiar borde/color según alertas de espera.
        key_prefix (str): Prefijo para keys de Streamlit.
    """
    # 1. Preparar Datos Visuales
    nombre = patient.get('nombre_completo', f"{patient.get('nombre', '')} {patient.get('apellido1', '')}")
    pid = patient.get('patient_code', 'N/A')
    
    # Nivel Triaje
    nivel_str = str(patient.get('nivel_triaje', 'N/A'))
    badge_color = "grey"
    if "Rojo" in nivel_str or "Nivel I" in nivel_str: badge_color = "red"
    elif "Naranja" in nivel_str or "Nivel II" in nivel_str: badge_color = "orange"
    elif "Amarillo" in nivel_str or "Nivel III" in nivel_str: badge_color = "orange" # Gold/Yellow
    elif "Verde" in nivel_str or "Nivel IV" in nivel_str: badge_color = "green"
    elif "Azul" in nivel_str or "Nivel V" in nivel_str: badge_color = "blue"

    # Tiempo de Espera
    wait_str = "0 min"
    alert_level = "normal"
    if show_wait_time:
        wait_start = patient.get('wait_start') or patient.get('entrada') or patient.get('created_at')
        if wait_start:
            if isinstance(wait_start, str):
                try: wait_start = datetime.fromisoformat(wait_start.replace('Z', '+00:00'))
                except: pass
            if isinstance(wait_start, datetime):
                # Ensure timezone awareness compatibility if needed, usually naive works if consistent
                if wait_start.tzinfo and not datetime.now().tzinfo:
                     wait_start = wait_start.replace(tzinfo=None)
                
                mins = int((datetime.now() - wait_start).total_seconds() / 60)
                if mins < 60: wait_str = f"{mins} min"
                else: wait_str = f"{mins // 60}h {mins % 60}m"
                
                # Simple alert logic (can be replaced by queue_manager logic if passed)
                # This is a fallback if 'alert_level' is not in patient dict
                if 'alert_level' in patient:
                    alert_level = patient['alert_level']
                else:
                    # Default thresholds
                    if mins > 120: alert_level = 'critical'
                    elif mins > 60: alert_level = 'warning'

    # 2. Renderizar
    # Borde coloreado si es crítico/warning
    border_color = None # Default streamlit gray
    if highlight_alert:
        if alert_level == 'critical': 
            # Streamlit no permite color de borde en container nativo directamente, 
            # pero podemos usar markdown o emoji.
            pass 

    with st.container(border=True):
        c_info, c_meta = st.columns([3, 1])
        
        with c_info:
            # Header: Badge + Nombre
            if show_triage_level and nivel_str != 'N/A':
                st.markdown(f":{badge_color}[**{nivel_str}**] **{nombre}**")
            else:
                st.markdown(f"**{nombre}**")
            
            st.caption(f"ID: `{pid}`")
            
            if show_location:
                loc = patient.get('sala_actual') or patient.get('sala_espera_origen') or "N/A"
                st.caption(f"📍 {loc}")

        with c_meta:
            if show_wait_time:
                st.markdown(f"⏱️ **{wait_str}**")
                if highlight_alert:
                    if alert_level == 'critical':
                        st.markdown(":red[**CRITICAL**]")
                    elif alert_level == 'warning':
                        st.markdown(":orange[**WARNING**]")

        # Acciones
        if actions:
            cols = st.columns(len(actions))
            for i, action in enumerate(actions):
                with cols[i]:
                    if st.button(
                        action['label'],
                        key=f"{key_prefix}_{action['key']}_{pid}",
                        type=action.get('type', 'secondary'),
                        use_container_width=True,
                        help=action.get('help')
                    ):
                        if action.get('on_click'):
                            action['on_click'](patient)
