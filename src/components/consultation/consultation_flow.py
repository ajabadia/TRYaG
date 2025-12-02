# path: src/components/consultation/consultation_flow.py
# Creado: 2025-11-26
"""
Flujo clínico para Consultas e Ingresos.
Implementa el stepper: Revisión Historia -> Evolución -> Plan/Alta.
"""
import streamlit as st
from services.flow_manager import finalizar_flujo
from services.patient_service import calcular_edad
from services.permissions_service import get_current_user

def _get_username():
    user = get_current_user()
    return user.get("username", "unknown") if user else "unknown"

def render_consultation_flow(paciente: dict, flujo: dict, on_finish: callable = None):
    """
    Renderiza el flujo de atención de consulta.
    
    Args:
        paciente: Datos del paciente.
        flujo: Datos del flujo actual.
        on_finish: Callback al finalizar.
    """
    patient_code = paciente.get('patient_code')
    
    # --- Inicializar Estado ---
    session_key = f"consultation_session_{patient_code}"
    if session_key not in st.session_state:
        st.session_state[session_key] = {
            "historia": "",
            "evolucion": "",
            "plan": "",
            "step": 1
        }
    
    data = st.session_state[session_key]

    # --- Header con Tarjeta de Paciente ---
    from ui.components.common.patient_card import render_patient_card
    
    render_patient_card(
        patient=paciente,
        show_triage_level=True,
        show_wait_time=True,
        show_location=True,
        allow_rejection=True,
        allow_reassignment=True,
        allow_finish=True,
        key_prefix="consultation_flow"
    )
    
    # --- Stepper ---
    steps = {
        1: "Revisión Historia",
        2: "Evolución",
        3: "Plan y Alta"
    }
    
    cols = st.columns(len(steps))
    for i, (step_num, step_name) in enumerate(steps.items()):
        with cols[i]:
            if step_num == data["step"]:
                st.markdown(f"#### 🔵 {step_name}")
            elif step_num < data["step"]:
                st.markdown(f"✅ {step_name}")
            else:
                st.markdown(f"⚪ {step_name}")
    
    st.divider()

    # --- Pasos ---
    if data["step"] == 1:
        _step_historia(data)
    elif data["step"] == 2:
        _step_evolucion(data)
    elif data["step"] == 3:
        _step_plan(data, patient_code, session_key, on_finish)

def _step_historia(data):
    st.markdown("#### 📖 Revisión de Historia")
    st.info("Aquí se mostrarían antecedentes, alergias y visitas previas.")
    
    data["historia"] = st.text_area(
        "Notas de revisión",
        value=data["historia"],
        placeholder="Apuntes sobre la historia clínica...",
        height=150
    )
    
    if st.button("Siguiente ➡️", type="primary", use_container_width=True):
        data["step"] = 2
        st.rerun()

def _step_evolucion(data):
    st.markdown("#### 📝 Evolución Clínica")
    
    data["evolucion"] = st.text_area(
        "Evolución / Curso Clínico",
        value=data["evolucion"],
        placeholder="Describa la evolución del paciente...",
        height=200
    )
    
    c_prev, c_next = st.columns([1, 4])
    with c_prev:
        if st.button("⬅️ Atrás"):
            data["step"] = 1
            st.rerun()
    with c_next:
        if st.button("Siguiente ➡️", type="primary", use_container_width=True):
            data["step"] = 3
            st.rerun()

def _step_plan(data, patient_code, session_key, on_finish):
    st.markdown("#### 🏁 Plan y Alta")
    
    data["plan"] = st.text_area(
        "Plan Terapéutico / Recomendaciones",
        value=data["plan"],
        placeholder="Plan a seguir...",
        height=150
    )
    
    st.divider()
    
    tipo_resolucion = st.selectbox(
        "Resolución",
        ["INGRESO_CONFIRMADO", "ALTA_DOMICILIO", "DERIVACION_ESPECIALISTA"],
        key=f"res_{patient_code}"
    )
    
    c_prev, c_finish = st.columns([1, 4])
    with c_prev:
        if st.button("⬅️ Atrás"):
            data["step"] = 2
            st.rerun()
    with c_finish:
        if st.button("✅ Finalizar Consulta", type="primary", use_container_width=True):
            if not data["plan"]:
                st.error("⚠️ Debe indicar un plan.")
            else:
                _finalizar_consulta(patient_code, tipo_resolucion, data, session_key, on_finish)

def _finalizar_consulta(patient_code, tipo, data, session_key, on_finish):
    try:
        notas = f"Historia: {data['historia']} | Evolución: {data['evolucion']} | Plan: {data['plan']}"
        finalizar_flujo(
            patient_code=patient_code,
            tipo_finalizacion=tipo,
            notas=notas,
            usuario=_get_username()
        )
        
        if session_key in st.session_state:
            del st.session_state[session_key]
            
        st.success("Consulta finalizada correctamente.")
        if on_finish:
            on_finish()
        else:
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
