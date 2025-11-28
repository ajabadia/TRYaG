# path: src/components/admission/step_patient_data.py
# Creado: 2025-11-24
"""
Paso 2 del flujo de admisión: Búsqueda y datos del paciente.
"""
import streamlit as st
from datetime import datetime, date
from services.patient_service import (
    buscar_paciente_existente,
    crear_paciente,
    actualizar_paciente_con_auditoria,
    validar_documento,
    calcular_edad,
)
from services.patient_flow_service import obtener_flujo_activo, rechazar_paciente
from src.db.repositories.people import get_people_repository
from ui.config.people_manager import person_dialog
from utils.icons import render_icon


def render_step_patient_data() -> bool:
    """
    Renderiza la búsqueda y captura de datos del paciente.
    
    Returns:
        bool: True si los datos están validados, False en caso contrario.
    """
    st.subheader("2️⃣ Datos del Paciente")
    
    # Inicializar estados
    if 'admission_patient_data' not in st.session_state:
        st.session_state.admission_patient_data = None
    if 'admission_patient_validated' not in st.session_state:
        st.session_state.admission_patient_validated = False
    if 'admission_patient_code' not in st.session_state:
        st.session_state.admission_patient_code = None
    if 'admission_edit_mode' not in st.session_state:
        st.session_state.admission_edit_mode = False
    
    # Inicializar inputs
    if 'adm_nombre' not in st.session_state:
        st.session_state.adm_nombre = ""
    if 'adm_apellido1' not in st.session_state:
        st.session_state.adm_apellido1 = ""
    if 'adm_apellido2' not in st.session_state:
        st.session_state.adm_apellido2 = ""
    if 'adm_fecha_nac' not in st.session_state:
        st.session_state.adm_fecha_nac = date(1990, 1, 1)
    if 'admission_contact_info' not in st.session_state:
        st.session_state.admission_contact_info = []
    
    # Inicializar estado de confirmación de nuevo paciente
    if 'admission_patient_not_found' not in st.session_state:
        st.session_state.admission_patient_not_found = False
    
    # --- Callback para modal ---
    def on_person_save(pid):
        repo = get_people_repository()
        person = repo.get_by_id(pid)
        if person:
            st.session_state.admission_patient_data = person
            st.session_state.admission_patient_validated = True # Asumimos validado al venir de modal/db
            st.session_state.admission_patient_code = person['patient_code']
            
            # Verificar flujo activo
            flujo_activo = obtener_flujo_activo(person['patient_code'])
            st.session_state.admission_active_flow = flujo_activo
            
            st.rerun()

    # --- Búsqueda Automática ---
    patient_loaded = st.session_state.admission_patient_data is not None
    
    if not patient_loaded:
        with st.container(border=True):
            col_title, col_create = st.columns([3, 1])
            with col_title:
                st.markdown("**🔍 Búsqueda de Paciente**")
            with col_create:
                if st.button("➕ Crear Nuevo", type="primary", use_container_width=True):
                    person_dialog(None, on_save=on_person_save)
            
            search_term = st.text_input("Buscar por Nombre, DNI, SS...", placeholder="Escriba al menos 3 caracteres", key="adm_search_term")
            
            if search_term and len(search_term) >= 3:
                repo = get_people_repository()
                results = repo.search_by_name(search_term)
                
                if results:
                    st.caption(f"Encontrados {len(results)} resultados:")
                    for p in results:
                        with st.container(border=True):
                            c1, c2, c3 = st.columns([4, 1, 1])
                            with c1:
                                nombre_completo = f"{p.get('nombre')} {p.get('apellido1')} {p.get('apellido2') or ''}".strip()
                                st.markdown(f"**{nombre_completo}**")
                                
                                ids = []
                                if p.get('num_ss'): ids.append(f"SS: {p.get('num_ss')}")
                                for i in p.get('identificaciones', []):
                                    ids.append(f"{i['type']}: {i['value']}")
                                if not ids and p.get('identification_number'): ids.append(f"ID: {p.get('identification_number')}")
                                
                                st.caption(f"Código: `{p.get('patient_code')}` | {' | '.join(ids)}")
                                
                            with c2:
                                if st.button("Seleccionar", key=f"sel_{p['_id']}", use_container_width=True):
                                    on_person_save(str(p['_id']))
                                    
                            with c3:
                                if st.button("✏️", key=f"edit_{p['_id']}", help="Editar Persona"):
                                    person_dialog(str(p['_id']), on_save=on_person_save)
                else:
                    st.info("No se encontraron resultados.")
            elif search_term:
                st.caption("Escriba al menos 3 caracteres para buscar.")

    else:
        # Estado: Paciente cargado
        paciente = st.session_state.admission_patient_data
        
        # --- Diálogo de gestión de flujo activo ---
        if 'admission_active_flow' not in st.session_state:
            st.session_state.admission_active_flow = None
        
        if st.session_state.admission_active_flow:
            st.divider()
            from components.common.active_flow_manager import render_active_flow_manager
            
            def _on_continue():
                st.session_state.admission_continue_active = True
                pass # El flujo continuará en la vista principal si es necesario

            def _on_cancel_search():
                st.session_state.admission_patient_data = None
                st.session_state.admission_active_flow = None
                st.session_state.admission_patient_validated = False
                st.rerun()

            def _on_reassign_success():
                st.session_state.admission_active_flow = None
                st.session_state.admission_patient_validated = True
                st.success("✅ Proceso anterior cerrado. Puede continuar.")
                st.rerun()

            render_active_flow_manager(
                paciente=paciente,
                flujo=st.session_state.admission_active_flow,
                key_prefix="adm_active_flow",
                on_continue=_on_continue,
                on_cancel=_on_cancel_search,
                on_reassign_success=_on_reassign_success,
                reassign_mode_label="Reasignar Sala",
                reassign_help="Cierra el flujo actual y permite asignar una nueva sala"
            )
            return False

        # --- Vista de Paciente Seleccionado (Read Only) ---
        with st.container(border=True):
            c_info, c_actions = st.columns([4, 1])
            with c_info:
                nombre_completo = f"{paciente.get('nombre')} {paciente.get('apellido1')} {paciente.get('apellido2') or ''}".strip()
                st.markdown(f"### 👤 {nombre_completo}")
                
                ids = []
                if paciente.get('num_ss'): ids.append(f"**SS:** {paciente.get('num_ss')}")
                for i in paciente.get('identificaciones', []):
                    ids.append(f"**{i['type']}:** {i['value']}")
                
                st.markdown(" | ".join(ids))
                
                fnac = paciente.get('fecha_nacimiento')
                if isinstance(fnac, datetime): fnac = fnac.date()
                edad = calcular_edad(datetime.combine(fnac, datetime.min.time())) if fnac else "?"
                st.caption(f"Fecha Nacimiento: {fnac} ({edad} años)")
                
            with c_actions:
                if st.button("✏️ Editar", key="adm_edit_selected", use_container_width=True):
                    person_dialog(str(paciente['_id']), on_save=on_person_save)
                
                if st.button("🔄 Cambiar", key="adm_change_patient", use_container_width=True):
                    st.session_state.admission_patient_data = None
                    st.session_state.admission_patient_validated = False
                    st.session_state.admission_active_flow = None
                    st.rerun()
        
        st.success("✅ Paciente seleccionado y validado.")
        st.session_state.admission_patient_validated = True

    return st.session_state.admission_patient_validated
