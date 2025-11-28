# path: src/components/common/patient_selection_card.py
# Creado: 2025-11-25
"""
Componente reutilizable para mostrar una tarjeta de selección de paciente.
Se usa en listas de espera (Triaje, Admisión, etc.).
"""
import streamlit as st
from services.room_service import obtener_sala_por_codigo

def render_patient_selection_card(
    patient, 
    is_selected=False, 
    key_prefix="", 
    is_in_room=False, 
    disable_attend=False,
    show_actions=False
):
    """
    Renderiza una tarjeta de paciente con información clave y botones de acción.
    
    Args:
        patient (dict): Datos del paciente.
        is_selected (bool): Si está seleccionado.
        key_prefix (str): Prefijo para claves.
        is_in_room (bool): Si el paciente ya está en la sala (destacado).
        disable_attend (bool): Si se debe deshabilitar el botón de atender.
        show_actions (bool): Si mostrar botones extra (Rechazar/Reasignar).
        
    Returns:
        str: Acción realizada ('attend', 'reject', 'reassign') o None.
    """
    # Obtener nombre legible de la sala
    sala_codigo = patient.get('sala_espera_origen')
    sala_texto = sala_codigo or "Desconocida"
    
    if sala_codigo:
        sala_info = obtener_sala_por_codigo(sala_codigo)
        if sala_info:
            sala_texto = f"{sala_info.get('nombre', '')} ({sala_codigo})"

    # Contenedor con estilo diferente si está en sala
    if is_in_room:
        context = st.info("🔵 Paciente en Sala de Triaje")
    else:
        context = st.container(border=True)
    
    with context:
        col_info, col_action = st.columns([4, 1])
        
        with col_info:
            # Nombre y estado
            nombre_completo = f"{patient.get('nombre', '')} {patient.get('apellido1', '')}".strip()
            
            if is_in_room:
                st.markdown(f"🔵 **{nombre_completo}** (En Sala)")
            elif is_selected:
                st.success(f"✓ **{nombre_completo}**")
            else:
                st.markdown(f"**{nombre_completo}**")
            
            # Detalles
            col_id, col_sala = st.columns(2)
            with col_id:
                st.caption(f"**ID:** {patient.get('patient_code')}")
            with col_sala:
                st.caption(f"**Sala:** {sala_texto}")
            
            # Hora
            if 'entrada' in patient:
                try:
                    entrada = patient.get('entrada')
                    if isinstance(entrada, str):
                        from datetime import datetime
                        entrada = datetime.fromisoformat(entrada.replace('Z', '+00:00'))
                    
                    if entrada:
                        from datetime import datetime
                        hora = entrada.strftime('%H:%M')
                        delta = datetime.now() - entrada
                        minutos = int(delta.total_seconds() / 60)
                        
                        if minutos < 60:
                            espera_str = f"{minutos} min"
                        else:
                            h = minutos // 60
                            m = minutos % 60
                            espera_str = f"{h}h {m}m"
                            
                        st.caption(f"**Llegada:** {hora} (⏱️ {espera_str})")
                except Exception:
                    pass
        
        with col_action:
            action = None
            
            # Botón Principal
            btn_label = "Continuar" if is_in_room else ("Atendiendo" if is_selected else "Atender")
            btn_type = "primary" if (is_selected or is_in_room) else "secondary"
            
            if st.button(
                btn_label, 
                key=f"{key_prefix}_attend_{patient.get('patient_code')}", 
                type=btn_type, 
                disabled=disable_attend and not is_in_room, # Permitir continuar si es el paciente en sala
                use_container_width=True
            ):
                action = "attend"
            
            # Botones Extra
            if show_actions:
                col_rej, col_reas = st.columns(2)
                with col_rej:
                    if st.button("❌", key=f"{key_prefix}_reject_{patient.get('patient_code')}", help="Rechazar", use_container_width=True):
                        action = "reject"
                with col_reas:
                    if st.button("➡️", key=f"{key_prefix}_reassign_{patient.get('patient_code')}", help="Reasignar", use_container_width=True):
                        action = "reassign"
                        
            return action

def render_patient_header(patient, triage_result=None):
    """
    Renderiza una cabecera con estilo de tarjeta para el paciente en proceso.
    Incluye datos del triaje si están disponibles.
    """
    with st.container(border=True):
        col_info, col_extra = st.columns([3, 1])
        
        with col_info:
            nombre_completo = f"{patient.get('nombre', '')} {patient.get('apellido1', '')}".strip()
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
