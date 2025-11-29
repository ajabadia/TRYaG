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
    is_in_room: bool = False,
    key_prefix: str = ""
):
    """
    Renderiza una tarjeta de paciente unificada y flexible.
    
    Args:
        patient (dict): Datos del paciente.
        actions (list): Lista de dicts con configuración de botones:
                        [{'label': 'Llamar', 'key': 'call', 'on_click': func, 'type': 'primary', 'disabled': bool}]
        show_triage_level (bool): Mostrar badge de nivel de triaje.
        show_wait_time (bool): Mostrar tiempo de espera.
        show_location (bool): Mostrar sala actual/origen.
        highlight_alert (bool): Cambiar borde/color según alertas de espera.
        is_in_room (bool): Destacar si el paciente está en sala (estilo azul).
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
    # Contenedor con estilo diferente si está en sala
    if is_in_room:
        context = st.info("🔵 Paciente en Sala")
    else:
        context = st.container(border=True)

    with context:
        c_info, c_meta = st.columns([3, 1])
        
        with c_info:
            # Header: Badge + Nombre
            if is_in_room:
                 st.markdown(f"**{nombre}**")
            elif show_triage_level and nivel_str != 'N/A':
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
                if highlight_alert and not is_in_room:
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
                        help=action.get('help'),
                        disabled=action.get('disabled', False)
                    ):
                        if action.get('on_click'):
                            action['on_click'](patient)

def render_patient_header(patient, triage_result=None):
    """
    Renderiza una cabecera con estilo de tarjeta para el paciente en proceso.
    Incluye datos del triaje si están disponibles.
    """
    with st.container(border=True):
        col_info, col_extra = st.columns([3, 1])
        
        with col_info:
            nombre_completo = patient.get('nombre_completo', f"{patient.get('nombre', '')} {patient.get('apellido1', '')}").strip()
            st.markdown(f"### 👤 {nombre_completo}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption(f"**ID:** {patient.get('patient_code')}")
            with c2:
                edad = patient.get('edad', 'N/A')
                st.caption(f"**Edad:** {edad} años")
            with c3:
                # Mostrar sala de origen si existe
                sala = patient.get('sala_espera_origen')
                if sala:
                    st.caption(f"**Origen:** {sala}")

        with col_extra:
            if triage_result and triage_result.get('nivel'):
                nivel = triage_result.get('nivel')
                # Si es un dict (color, text), extraer
                if isinstance(nivel, dict):
                    color = nivel.get('color', 'grey')
                    text = nivel.get('text', 'N/A')
                    st.markdown(f"<div style='background-color:{color}; color:white; padding:10px; border-radius:5px; text-align:center;'><b>{text}</b></div>", unsafe_allow_html=True)
                else:
                    st.info(f"Nivel: {nivel}")
            else:
                st.caption("Triaje en curso...")
    # Nota: Este componente es pequeño y se usa repetidamente, quizás no queramos el footer en cada tarjeta individual
    # pero si el usuario lo pide explícitamente en "todos los archivos", lo ponemos.
    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/components/common/patient_card.py</div>', unsafe_allow_html=True)
