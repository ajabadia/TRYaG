# path: src/ui/components/common/patient_card.py
import streamlit as st
from datetime import datetime
from utils.ui_utils import get_room_color

from services.patient_service import calcular_edad, obtener_paciente_por_codigo

def render_patient_card(
    patient: dict,
    actions: list = None,
    show_triage_level: bool = True,
    show_wait_time: bool = True,
    show_location: bool = False,
    highlight_alert: bool = True,
    is_in_room: bool = False,
    flow_status: dict = None,
    key_prefix: str = ""
):
    """
    Renderiza una tarjeta de paciente unificada y flexible.
    Si faltan datos en el dict 'patient', intenta completarlos desde BD usando 'patient_code'.
    
    Args:
        patient (dict): Datos del paciente (puede ser parcial).
        actions (list): Lista de dicts con configuración de botones.
        show_triage_level (bool): Mostrar badge de nivel de triaje.
        show_wait_time (bool): Mostrar tiempo de espera.
        show_location (bool): Mostrar sala actual/origen.
        highlight_alert (bool): Cambiar borde/color según alertas de espera.
        is_in_room (bool): Destacar si el paciente está en sala (estilo azul).
        key_prefix (str): Prefijo para keys de Streamlit.
    """
    # 0. Enriquecer datos si es necesario
    # Si faltan datos básicos (nombre, edad) y tenemos código, consultamos BD
    pid = patient.get('patient_code')
    if pid and (not patient.get('nombre') or patient.get('edad') is None):
        full_data = obtener_paciente_por_codigo(pid)
        if full_data:
            # Mezclar: priorizar datos de flujo (patient) sobre estáticos (full_data) para cosas como ubicación,
            # pero usar estáticos para demografía si faltan.
            # Estrategia: Copiar full_data y actualizar con patient (para mantener estado actual de flujo)
            merged = full_data.copy()
            merged.update(patient)
            patient = merged

    # 1. Preparar Datos Visuales
    nombre = patient.get('nombre_completo')
    if not nombre:
        nombre = f"{patient.get('nombre', '')} {patient.get('apellido1', '')} {patient.get('apellido2', '')}".strip()
    
    # Calcular edad si falta
    edad = patient.get('edad')
    if edad is None or edad == 'N/A':
        fnac = patient.get('fecha_nacimiento')
        if fnac:
            if isinstance(fnac, str):
                try: fnac = datetime.fromisoformat(fnac)
                except: pass
            if isinstance(fnac, datetime):
                edad = calcular_edad(fnac)
                patient['edad'] = edad # Guardar para uso posterior
    
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
    # Usar siempre container para consistencia, el estilo visual se maneja dentro
    context = st.container(border=True)
    
    # Estilo CSS para destacar si está en sala (opcional, o usar st.info dentro)
    if is_in_room:
        st.markdown("""
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            border-color: #2196F3 !important;
            border-width: 2px !important;
        }
        </style>
        """, unsafe_allow_html=True)

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
            
            edad_str = f"{patient.get('edad')} años" if patient.get('edad') is not None else ""
            gender_str = patient.get('gender', '')
            if gender_str and gender_str != 'No Especificado':
                 edad_str += f" • {gender_str}"
            
            st.caption(f"ID: `{pid}` {('• ' + edad_str) if edad_str else ''}")
            
            if show_location:
                # Prioridad: sala_nombre > sala_code > sala_actual > sala_espera_origen
                loc_name = patient.get('sala_nombre')
                loc_code = patient.get('sala_code') or patient.get('sala_actual')
                
                if loc_name and loc_code:
                    loc_display = f"{loc_name} ({loc_code})"
                elif loc_name:
                    loc_display = loc_name
                elif loc_code:
                    loc_display = loc_code
                else:
                    loc_display = patient.get('sala_espera_origen') or "N/A"
                
                # Obtener color según tipo de sala (si está disponible)
                sala_tipo = patient.get('sala_tipo')
                color = get_room_color(sala_tipo)
                
                st.markdown(f"📍 <span style='color:{color}; font-weight:bold;'>{loc_display}</span>", unsafe_allow_html=True)

            # Mostrar estado de flujo si se proporciona
            if flow_status:
                estado = flow_status.get('estado', 'N/A')
                sala_actual = flow_status.get('sala_actual', 'N/A')
                st.markdown(f"🔄 **Estado:** {estado}")
                if sala_actual and sala_actual != 'N/A':
                     st.markdown(f"🏥 **Sala Actual:** {sala_actual}")

        with c_meta:
            # --- INFO DE SEGURO ---
            insurance_info = patient.get('insurance_info', {})
            if insurance_info and insurance_info.get('has_insurance'):
                insurer_name = insurance_info.get('insurer_name', 'Aseguradora')
                logo_url = insurance_info.get('logo_url')
                
                if logo_url:
                    st.image(logo_url, width=60, caption=insurer_name)
                else:
                    st.markdown(f"🏥 **{insurer_name}**")
            elif insurance_info and not insurance_info.get('has_insurance') and insurance_info.get('type') == 'Privado':
                st.markdown("💶 **Privado**")

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
            
            # Botón de Informe (Modal)
            if pid != 'N/A':
                col_pdf, _ = st.columns([1, 3])
                with col_pdf:
                    if st.button("📄 Informe", key=f"btn_pdf_{pid}_{key_prefix}", help="Ver y descargar informe", use_container_width=True):
                        from ui.components.reports.report_viewer import render_report_viewer
                        from utils.triage_utils import get_triage_record_for_pdf
                        
                        record = get_triage_record_for_pdf(pid)
                        if record:
                            render_report_viewer(record, patient)
                        else:
                            st.toast("⚠️ No hay datos de triaje disponibles para este paciente.", icon="⚠️")
        
        # Etiqueta de componente
        st.markdown('<div style="color: #ccc; font-size: 0.6em; text-align: right;">src/ui/components/common/patient_card.py</div>', unsafe_allow_html=True)

from services.patient_service import calcular_edad

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
                edad = patient.get('edad')
                if edad is None or edad == 'N/A':
                    fnac = patient.get('fecha_nacimiento')
                    if fnac:
                        if isinstance(fnac, str):
                            try:
                                fnac = datetime.fromisoformat(fnac)
                            except:
                                pass
                        if isinstance(fnac, datetime):
                            edad = calcular_edad(fnac)
                        else:
                            edad = 'N/A'
                    else:
                        edad = 'N/A'
                
                st.caption(f"**Edad:** {edad} años")
                gender = patient.get('gender')
                if gender and gender != 'No Especificado':
                    st.caption(f"**Sexo:** {gender}")
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
