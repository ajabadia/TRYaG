# path: src/ui/components/common/patient_card.py
import streamlit as st
from datetime import datetime
from utils.ui_utils import get_room_color

from services.patient_service import calcular_edad, obtener_paciente_por_codigo
from services.report_service import generate_triage_pdf
import unicodedata
import re

# --- MODALES GLOBALES (Evitar definición en bucle) ---

@st.dialog("⛔ Rechazar Paciente")
def _dialog_reject(pid, nombre):
    st.markdown(f"**Paciente:** {nombre}")
    st.warning("Esta acción finalizará el flujo del paciente y liberará la sala.")
    motivo = st.text_area("Motivo del rechazo", key=f"reason_reject_{pid}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", key=f"cancel_reject_{pid}"):
            st.session_state[f"show_reject_modal_{pid}"] = False
            st.rerun()
    with c2:
        if st.button("Confirmar Rechazo", key=f"confirm_reject_{pid}", type="primary", disabled=not motivo):
            from services.patient_flow_service import rechazar_paciente
            if rechazar_paciente(pid, motivo):
                st.success("Paciente rechazado correctamente.")
                st.session_state[f"show_reject_modal_{pid}"] = False
                st.rerun()
            else:
                st.error("Error al rechazar paciente.")

@st.dialog("🔄 Cambiar Sala")
def _dialog_reassign(pid, nombre):
    st.markdown(f"**Paciente:** {nombre}")
    from db.repositories.salas import get_all_salas
    rooms = get_all_salas()
    # Filtrar salas activas
    active_rooms = [r for r in rooms if r.get('activa', True)]
    
    # Helper para formatear etiqueta con ocupación
    def format_room_label(r):
        return f"{r['nombre']} ({r['codigo']})"

    room_options = {format_room_label(r): r['codigo'] for r in active_rooms}
    
    selected_label = st.selectbox("Seleccione Nueva Sala", list(room_options.keys()), key=f"sel_reassign_{pid}")
    target_code = room_options[selected_label]
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", key=f"cancel_reassign_{pid}"):
            st.session_state[f"show_reassign_modal_{pid}"] = False
            st.rerun()
    with c2:
        if st.button("Confirmar Cambio", key=f"confirm_reassign_{pid}", type="primary"):
            from services.patient_flow_service import reassign_patient_flow
            if reassign_patient_flow(pid, new_sala_atencion_code=target_code): 
                    st.success("Paciente reasignado correctamente.")
                    st.session_state[f"show_reassign_modal_{pid}"] = False
                    st.rerun()
            else:
                    st.error("Error al reasignar paciente.")

@st.dialog("✅ Finalizar Atención")
def _dialog_finish(pid, nombre):
    st.markdown(f"**Paciente:** {nombre}")
    st.info("Finalizar la atención clínica y liberar el box/consulta.")
    notas = st.text_area("Notas de cierre (opcional)", key=f"notes_finish_{pid}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", key=f"cancel_finish_{pid}"):
            st.session_state[f"show_finish_modal_{pid}"] = False
            st.rerun()
    with c2:
        if st.button("Confirmar Finalización", key=f"confirm_finish_{pid}", type="primary"):
            from services.patient_flow_service import finalizar_flujo
            if finalizar_flujo(pid, motivo="Atención Completada", notas=notas):
                st.success("Atención finalizada.")
                st.session_state[f"show_finish_modal_{pid}"] = False
                st.rerun()
            else:
                st.error("Error al finalizar atención.")

@st.dialog("🖨️ Ticket de Admisión")
def _dialog_print(patient, pid):
    # Pasamos callback para cerrar
    def on_close():
            st.session_state[f"show_print_modal_{pid}"] = False
            st.rerun()
    
    from components.admission.patient_ticket import render_ticket_modal
    render_ticket_modal(patient)
    
    # Botón explicito de cerrar
    if st.button("Cerrar", key=f"close_print_{pid}"):
        on_close()


def render_patient_card(
    patient: dict,
    actions: list = None,
    show_triage_level: bool = True,
    show_wait_time: bool = True,
    show_location: bool = False,
    highlight_alert: bool = True,
    is_in_room: bool = False,
    flow_status: dict = None,
    key_prefix: str = "",
    **kwargs
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
        
        # --- Estimación Inteligente ---
        estimated_min_total = patient.get('estimated_wait_minutes')
        remaining_str = ""
        if estimated_min_total is not None:
             elapsed = int((datetime.now() - wait_start).total_seconds() / 60) if wait_start else 0
             remaining = max(0, estimated_min_total - elapsed)
             
             if remaining == 0:
                 remaining_str = " (Inminente)"
                 badge_color_est = "green"
             else:
                 remaining_str = f" (Est. {remaining} min)"
                 badge_color_est = "grey"
             
             wait_str += remaining_str

    # 2. Renderizar
    # Usar siempre container para consistencia, el estilo visual se maneja dentro
    context = st.container(border=True)
    
    # Estilo CSS para destacar si está en sala (opcional, o usar st.info dentro)
    if is_in_room:
        from utils.ui_utils import load_css
        load_css("src/assets/css/components/cards.css")

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

        # Acciones Personalizadas
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
        
        # Acciones Estándar (Rechazar, Reasignar, Finalizar, Imprimir)
        # Se muestran en una fila separada o integradas si no hay acciones personalizadas
        
        # Definir qué acciones estándar mostrar
        std_actions = []
        if kwargs.get('allow_rejection', False):
            std_actions.append('reject')
        if kwargs.get('allow_reassignment', False):
            std_actions.append('reassign')
        # Nuevo: Imprimir siempre disponible por defecto si no se deshabilita explícitamente
        if kwargs.get('allow_print_ticket', True):
            std_actions.append('print')
        if kwargs.get('allow_finish', False):
            std_actions.append('finish')
            
        if std_actions:
            st.divider()
            c_std = st.columns(len(std_actions))
            
            for i, action_type in enumerate(std_actions):
                with c_std[i]:
                    if action_type == 'reject':
                        if st.button("⛔ Rechazar", key=f"btn_reject_{pid}_{key_prefix}", type="secondary", use_container_width=True):
                            st.session_state[f"show_reject_modal_{pid}"] = True
                            st.rerun()
                            
                    elif action_type == 'reassign':
                        if st.button("🔄 Cambiar Sala", key=f"btn_reassign_{pid}_{key_prefix}", type="secondary", use_container_width=True):
                            st.session_state[f"show_reassign_modal_{pid}"] = True
                            st.rerun()
                    
                    elif action_type == 'print':    
                         if st.button("🖨️ Pulsera", key=f"btn_print_{pid}_{key_prefix}", type="secondary", use_container_width=True):
                            st.session_state[f"show_print_modal_{pid}"] = True
                            st.rerun()

                    elif action_type == 'finish':
                        if st.button("✅ Finalizar", key=f"btn_finish_{pid}_{key_prefix}", type="primary", use_container_width=True):
                            st.session_state[f"show_finish_modal_{pid}"] = True
                            st.rerun()

        # Botón de Informe (Modal/Descarga)
        if pid != 'N/A' and kwargs.get('show_report', True):
            # Keys para estado de este PDF específico
            pdf_state_key = f"pdf_bytes_{pid}_{key_prefix}"
            pdf_name_key = f"pdf_name_{pid}_{key_prefix}"
            
            # Si ya está generado, mostrar botón de descarga
            if st.session_state.get(pdf_state_key):
                import base64
                
                pdf_data = st.session_state[pdf_state_key]
                file_name = st.session_state.get(pdf_name_key)
                if not file_name:
                    file_name = f"Informe_Triaje_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                
                # Guardar en disco temporal para servir vía Tornado (Fix Chrome)
                import os
                temp_dir = 'temp'
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, file_name)
                
                try:
                    with open(temp_path, "wb") as f:
                        f.write(pdf_data)
                        
                    download_url = f"/download_file_v7?filename={file_name}"
                    
                    c_down, c_clear = st.columns([3, 1])
                    with c_down:
                        st.markdown(f'''
                            <a href="{download_url}" target="_blank" style="text-decoration:none;">
                                <div style="
                                    display: inline-flex;
                                    align-items: center;
                                    justify-content: center;
                                    padding: 0.25rem 0.75rem;
                                    border-radius: 0.5rem;
                                    min-height: 38.4px;
                                    margin: 0px;
                                    line-height: 1.6;
                                    color: white;
                                    width: 100%;
                                    background-color: #ff4b4b;
                                    border: 1px solid rgba(49, 51, 63, 0.2);
                                    cursor: pointer;
                                    font-weight: 400;
                                    text-align: center;
                                ">
                                    ⬇️ Descargar PDF (Server)
                                </div>
                            </a>
                        ''', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Error saving temp PDF: {e}")
                    with st.spinner("Generando..."):
                        try:
                            # Construir registro wrapper (Flattener para report_service)
                            # El servicio espera que 'nombre', 'hda', etc estén en la raíz o en patient_snapshot
                            # Al ser is_draft=True, busca en la raíz.
                            record_wrapper = patient.copy()
                            record_wrapper.update({
                                "patient_snapshot": patient, # Fallback doble
                                "timestamp": datetime.now(),
                                "audit_id": pid,
                                "evaluator_id": "Sistema",
                                "status": "BORRADOR"
                            })
                            
                            # Generar
                            from services.report_service import get_report_filename
                            pdf_bytes = generate_triage_pdf(record_wrapper)
                            file_name = get_report_filename(patient, prefix="Informe")
                            
                            # Guardar en sesión
                            st.session_state[pdf_state_key] = pdf_bytes
                            st.session_state[pdf_name_key] = file_name
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # --- MODALES: INVOCACIÓN (Ya no definición) ---
    
    # 1. Modal Rechazo
    if st.session_state.get(f"show_reject_modal_{pid}", False):
        _dialog_reject(pid, nombre)

    # 2. Modal Reasignación
    if st.session_state.get(f"show_reassign_modal_{pid}", False):
        _dialog_reassign(pid, nombre)

    # 3. Modal Finalizar
    if st.session_state.get(f"show_finish_modal_{pid}", False):
        _dialog_finish(pid, nombre)
        
    # 4. Modal Impresión
    if st.session_state.get(f"show_print_modal_{pid}", False):
        _dialog_print(patient, pid)

    # Etiqueta de componente
    st.markdown('<div class="debug-footer">src/ui/components/common/patient_card.py</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="debug-footer">src/ui/components/common/patient_card.py</div>', unsafe_allow_html=True)
