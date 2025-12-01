# path: src/components/boxes/step_attention.py
# Creado: 2025-11-24
# Refactorizado: 2025-11-26 (Stepper Clínico)
"""
Paso 3 de Gestión de Boxes: Atención Clínica y Resolución.
Implementa un flujo clínico paso a paso (Anamnesis -> Pruebas -> Resolución).
"""
import streamlit as st
from datetime import datetime
from services.flow_manager import (
    obtener_pacientes_en_sala, 
    finalizar_flujo, 
    mover_paciente_a_sala
)
from services.patient_service import obtener_paciente_por_codigo, calcular_edad
from services.room_service import obtener_salas_por_tipo
from services.permissions_service import get_current_user

def _get_username():
    user = get_current_user()
    return user.get("username", "unknown") if user else "unknown"

def render_step_attention() -> bool:
    """
    Gestiona la atención del paciente activo en la sala mediante un flujo clínico.
    
    Returns:
        bool: True si hay un paciente siendo atendido.
    """
    room_code = st.session_state.get('boxes_room_code')
    if not room_code:
        return False

    # 1. Buscar si hay un paciente activo en esta sala
    pacientes_activos = obtener_pacientes_en_sala(room_code)
    
    if not pacientes_activos:
        return False # No hay paciente, volver a selección
    
    # Tomamos el primero
    flujo_paciente = pacientes_activos[0]
    patient_code = flujo_paciente.get('patient_code')
    
    # Obtener datos demográficos
    paciente = obtener_paciente_por_codigo(patient_code)
    if not paciente:
        st.error("Error al cargar datos del paciente.")
        return True

    # --- Inicializar Estado Clínico ---
    session_key = f"clinical_session_{patient_code}"
    if session_key not in st.session_state:
        st.session_state[session_key] = {
            "anamnesis": "",
            "exploracion": "",
            "pruebas": "",
            "tratamiento": "",
            "diagnostico": "",
            "step": 1
        }
    
    clinical_data = st.session_state[session_key]

    # --- Header del Paciente ---
    st.subheader("3️⃣ Acto Clínico")
    
    from ui.components.common.patient_card import render_patient_header
    
    # Adaptar datos para el header
    # El header espera un objeto triage_result opcional para el nivel.
    # Podemos pasar el estado del flujo como "nivel" para que se vea destacado si queremos,
    # o simplemente dejar que el header muestre lo básico.
    # El header actual muestra: Nombre, ID, Edad, Origen, y Nivel (Badge).
    
    # En boxes, el "nivel" podría ser el nivel de triaje si existe.
    # El objeto `flujo_paciente` tiene info del flujo. `paciente` tiene info demográfica.
    # Si queremos mostrar el nivel de triaje, deberíamos tenerlo.
    # Por ahora, usamos el header estándar.
    
    render_patient_header(paciente)

    # --- Stepper Navigation ---
    steps = {
        1: "Anamnesis y Exploración",
        2: "Pruebas y Tratamiento",
        3: "Diagnóstico y Resolución"
    }
    
    # Visualización del progreso
    cols = st.columns(len(steps))
    for i, (step_num, step_name) in enumerate(steps.items()):
        with cols[i]:
            if step_num == clinical_data["step"]:
                st.markdown(f"#### 🔵 {step_name}")
            elif step_num < clinical_data["step"]:
                st.markdown(f"✅ {step_name}")
            else:
                st.markdown(f"⚪ {step_name}")
    
    st.divider()

    # --- Renderizado del Paso Actual ---
    current_step = clinical_data["step"]

    if current_step == 1:
        _render_step_anamnesis(clinical_data)
    elif current_step == 2:
        _render_step_pruebas(clinical_data)
    elif current_step == 3:
        _render_step_resolucion(clinical_data, patient_code, session_key)

    return True



def _render_step_anamnesis(data):
    st.markdown("#### 📝 Anamnesis y Exploración Física")
    
    col1, col2 = st.columns(2)
    with col1:
        data["anamnesis"] = st.text_area(
            "Anamnesis / Motivo de Consulta", 
            value=data["anamnesis"],
            height=200,
            placeholder="Describa el motivo de consulta y antecedentes..."
        )
    with col2:
        data["exploracion"] = st.text_area(
            "Exploración Física", 
            value=data["exploracion"],
            height=200,
            placeholder="Constantes, auscultación, inspección..."
        )

    col_next = st.columns([4, 1])[1]
    with col_next:
        if st.button("Siguiente ➡️", type="primary", use_container_width=True):
            data["step"] = 2
            st.rerun()

def _render_step_pruebas(data):
    st.markdown("#### 🧪 Pruebas Complementarias y Tratamiento")
    
    col1, col2 = st.columns(2)
    with col1:
        data["pruebas"] = st.text_area(
            "Solicitud de Pruebas", 
            value=data["pruebas"],
            height=150,
            placeholder="Analíticas, Radiografías, etc..."
        )
        st.info("ℹ️ La integración con LIS/RIS está pendiente.")
        
    with col2:
        data["tratamiento"] = st.text_area(
            "Tratamiento en Box / Pauta", 
            value=data["tratamiento"],
            height=150,
            placeholder="Medicación administrada, curas..."
        )

    c_prev, c_next = st.columns([1, 4, 1])[0::2]
    with c_prev:
        if st.button("⬅️ Anterior", use_container_width=True):
            data["step"] = 1
            st.rerun()
    with c_next:
        if st.button("Siguiente ➡️", type="primary", use_container_width=True):
            data["step"] = 3
            st.rerun()

def _render_step_resolucion(data, patient_code, session_key):
    st.markdown("#### 🏁 Diagnóstico y Resolución")
    
    data["diagnostico"] = st.text_area(
        "Diagnóstico Principal", 
        value=data["diagnostico"],
        height=100,
        placeholder="Juicio clínico final..."
    )
    
    st.divider()
    
    col_alta, col_ingreso = st.columns(2)
    
    # --- Columna Alta ---
    with col_alta:
        with st.container(border=True):
            st.markdown("##### 🏠 Dar de Alta")
            tipo_alta = st.selectbox(
                "Tipo de Alta", 
                ["ALTA_CURADO", "ALTA_DERIVADO_AP", "ALTA_VOLUNTARIA", "ABANDONO"],
                key=f"tipo_alta_{patient_code}"
            )
            
            if st.button("✅ Finalizar (Alta)", type="primary", use_container_width=True):
                if not data["diagnostico"]:
                    st.error("⚠️ Debe indicar un diagnóstico.")
                else:
                    _finalizar_visita(patient_code, tipo_alta, data, session_key)

    # --- Columna Ingreso ---
    with col_ingreso:
        with st.container(border=True):
            st.markdown("##### 🏥 Solicitar Ingreso")
            
            salas_ingreso = [s for s in obtener_salas_por_tipo("consulta_ingreso") if s.get('subtipo') == 'espera']
            opciones_ingreso = {f"{s['nombre']} ({s['codigo']})": s['codigo'] for s in salas_ingreso}
            
            sala_ingreso_sel = st.selectbox(
                "Enviar a Espera de Ingreso", 
                options=list(opciones_ingreso.keys()),
                key=f"sala_ingreso_{patient_code}",
                disabled=len(salas_ingreso) == 0
            )
            
            if st.button("Solicitar Ingreso ➡️", type="secondary", use_container_width=True, disabled=len(salas_ingreso) == 0):
                 if not data["diagnostico"]:
                    st.error("⚠️ Debe indicar un diagnóstico.")
                 elif not sala_ingreso_sel:
                    st.error("⚠️ No hay salas disponibles.")
                 else:
                    codigo_sala_destino = opciones_ingreso[sala_ingreso_sel]
                    _solicitar_ingreso(patient_code, codigo_sala_destino, data, session_key)

    c_prev = st.columns([1, 5])[0]
    with c_prev:
        if st.button("⬅️ Anterior", use_container_width=True):
            data["step"] = 2
            st.rerun()

def _finalizar_visita(patient_code, tipo_alta, data, session_key):
    try:
        notas_finales = (
            f"Anamnesis: {data['anamnesis']} | "
            f"Exploración: {data['exploracion']} | "
            f"Pruebas: {data['pruebas']} | "
            f"Dx: {data['diagnostico']} | "
            f"Tx: {data['tratamiento']}"
        )
        finalizar_flujo(
            patient_code=patient_code,
            tipo_finalizacion=tipo_alta,
            notas=notas_finales,
            usuario=_get_username()
        )
        # Limpiar sesión
        if session_key in st.session_state:
            del st.session_state[session_key]
            
        st.success(f"Visita finalizada: {tipo_alta}")
        st.rerun()
    except Exception as e:
        st.error(f"Error al finalizar: {e}")

def _solicitar_ingreso(patient_code, sala_destino, data, session_key):
    try:
        notas_ingreso = f"Solicitud Ingreso. Dx: {data['diagnostico']}. Tx: {data['tratamiento']}"
        mover_paciente_a_sala(
            patient_code=patient_code,
            sala_destino_code=sala_destino,
            sala_destino_tipo="consulta_ingreso",
            sala_destino_subtipo="espera",
            nuevo_estado="PENDIENTE_INGRESO",
            notas=notas_ingreso,
            usuario=_get_username()
        )
        # Limpiar sesión
        if session_key in st.session_state:
            del st.session_state[session_key]

        st.success("Solicitud de ingreso enviada correctamente.")
        st.rerun()
    except Exception as e:
        st.error(f"Error al solicitar ingreso: {e}")
