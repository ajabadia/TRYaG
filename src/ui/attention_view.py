# path: src/ui/attention_view.py
# Creado: 2025-11-24
"""
Vista de Atención en Box (Consulta Médica).
Permite seleccionar pacientes de la sala de espera, atenderlos y finalizar su flujo.
"""
import streamlit as st
from datetime import datetime
from services.patient_flow_service import (
    obtener_vista_global_salas, 
    iniciar_atencion_box, 
    finalizar_atencion,
    obtener_flujo_activo
)
from services.room_service import obtener_salas_por_tipo
from ui.config.config_loader import load_centro_config

from ui.components.waiting_list import render_waiting_list_component

def render_waiting_list(selected_box_code):
    """Muestra la lista de pacientes en salas de espera para ser llamados."""
    st.markdown("### 📋 Pacientes en Espera")
    
    # Obtener todos los pacientes
    vista_global = obtener_vista_global_salas()
    
    # Filtrar solo los que están en salas de espera (DERIVADO)
    # Buscar salas de tipo box con subtipo espera
    salas_box = obtener_salas_por_tipo('box')
    salas_espera = [s for s in salas_box if s.get('subtipo') == 'espera']
    codigos_espera = [s['codigo'] for s in salas_espera]
    
    pacientes_espera = []
    for codigo in codigos_espera:
        pacientes_espera.extend(vista_global.get(codigo, []))
        
    if not pacientes_espera:
        st.info("No hay pacientes en salas de espera.")
        return

    # Usar componente reutilizable
    render_waiting_list_component(pacientes_espera, context="attention", box_code=selected_box_code)

def render_active_patient(patient_code, box_code):
    """Muestra la ficha del paciente que está siendo atendido."""
    st.markdown(f"### 🩺 En Atención (Box {box_code})")
    
    # Recuperar datos completos
    flujo = obtener_flujo_activo(patient_code)
    if not flujo or flujo.get('estado') != 'EN_ATENCION':
        st.warning("El paciente ya no está en estado de atención activa.")
        st.session_state.active_patient_code = None
        st.rerun()
        return

    # Recuperar datos personales (esto debería venir de un servicio mejor, pero usamos lo que tenemos)
    # En una app real, haríamos una query a 'patients'
    # Aquí usamos el truco de obtener_vista_global para sacar datos enriquecidos si es necesario,
    # o hacemos query directa. Haremos query directa simulada o reusamos vista global.
    # Por eficiencia, mejor query directa, pero no tengo el servicio importado aquí.
    # Usaremos vista global filtrada por el box actual.
    vista = obtener_vista_global_salas()
    pacientes_box = vista.get(box_code, [])
    paciente_data = next((p for p in pacientes_box if p['patient_code'] == patient_code), None)
    
    if not paciente_data:
        st.error("Error cargando datos del paciente.")
        return

    # --- Ficha del Paciente ---
    with st.container(border=True):
        c_img, c_dat = st.columns([1, 4])
        with c_img:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80) # Placeholder
        with c_dat:
            st.markdown(f"## {paciente_data['nombre_completo']}")
            st.markdown(f"**Edad:** {paciente_data.get('edad', '?')} años | **ID:** {patient_code}")
            st.info(f"**Motivo Consulta:** {paciente_data.get('motivo_consulta', 'No especificado')}")

    # --- Acciones de Finalización ---
    st.divider()
    st.markdown("#### 📝 Resolución")
    
    detalles = st.text_area("Notas de evolución / Tratamiento", height=100)
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        if st.button("🏠 Alta / Domicilio", type="primary", use_container_width=True):
            if finalizar_atencion(patient_code, "DOMICILIO", detalles):
                st.success("Paciente dado de alta.")
                st.session_state.active_patient_code = None
                st.rerun()
                
    with c2:
        if st.button("🏥 Ingreso Hospital", use_container_width=True):
            if finalizar_atencion(patient_code, "INGRESO", detalles):
                st.success("Paciente enviado a ingreso.")
                st.session_state.active_patient_code = None
                st.rerun()

    with c3:
        if st.button("🔙 Devolver a Espera", use_container_width=True):
            if finalizar_atencion(patient_code, "ESPERA", detalles):
                st.success("Paciente devuelto a sala de espera.")
                st.session_state.active_patient_code = None
                st.rerun()
                
    with c4:
        if st.button("🚫 Rechazar / Error", type="secondary", use_container_width=True):
             if finalizar_atencion(patient_code, "RECHAZADO", detalles):
                st.warning("Atención rechazada/cancelada.")
                st.session_state.active_patient_code = None
                st.rerun()

def mostrar_atencion_box():
    """Vista principal de Atención en Box."""
    st.header(":material/stethoscope: Atención en Box")
    
    # 1. Selección de Box (Simulando login de médico en un box)
    salas_box = obtener_salas_por_tipo('box') # Tipo 'box' con subtipo 'atencion'
    salas_box_atencion = [s for s in salas_box if s.get('subtipo') == 'atencion']
    
    if not salas_box_atencion:
        st.warning("No hay salas de tipo 'box' con subtipo 'atencion' configuradas. Por favor añádalas en Configuración.")
        return

    box_options = [s['codigo'] for s in salas_box_atencion]
    selected_box = st.selectbox("📍 Seleccione su Box / Consulta", box_options, format_func=lambda x: next((s['nombre'] for s in salas_box_atencion if s['codigo'] == x), x))
    
    st.divider()
    
    # 2. Verificar si ya tengo un paciente activo en este box
    # Buscamos en la vista global si hay alguien en este box con estado EN_ATENCION
    vista = obtener_vista_global_salas()
    pacientes_en_mi_box = vista.get(selected_box, [])
    paciente_activo = next((p for p in pacientes_en_mi_box if p['estado_flujo'] == 'EN_ATENCION'), None)
    
    if paciente_activo:
        # Si hay paciente activo, mostramos su ficha directamente
        st.session_state.active_patient_code = paciente_activo['patient_code']
        render_active_patient(paciente_activo['patient_code'], selected_box)
    else:
        # Si no, mostramos la lista de espera para llamar a alguien
        st.session_state.active_patient_code = None
        render_waiting_list(selected_box)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/attention_view.py</div>', unsafe_allow_html=True)
