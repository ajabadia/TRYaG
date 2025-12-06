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
from db.repositories.people import get_people_repository
from ui.config.people_manager import person_dialog
from utils.icons import render_icon

def _update_patient_insurance(paciente, insurance_info):
    """Actualiza la información de seguro del paciente en BD y sesión."""
    from services.patient_service import actualizar_paciente_con_auditoria
    
    # Preparamos datos para actualizar (manteniendo lo demás igual)
    # Nota: actualizar_paciente_con_auditoria requiere pasar todos los campos.
    # Esto es un poco pesado, idealmente tendríamos un patch, pero usaremos lo que hay.
    
    # Extraer identificación principal
    main_id = paciente['identificaciones'][0]
    
    try:
        new_person_data, warning = actualizar_paciente_con_auditoria(
            patient_code_anterior=paciente['patient_code'],
            nombre=paciente['nombre'],
            apellido1=paciente['apellido1'],
            apellido2=paciente.get('apellido2'),
            fecha_nacimiento=paciente['fecha_nacimiento'],
            num_ss=paciente.get('num_ss'),
            num_identificacion=main_id['value'],
            tipo_identificacion=main_id['type'],
            contact_info=paciente.get('contact_info'),
            insurance_info=insurance_info,
            gender=paciente.get('gender'),
            usuario="admission_step",
            force_update=True # Forzamos porque solo actualizamos seguro
        )
        
        if new_person_data:
            # Actualizar sesión con el NUEVO objeto (que tiene nuevo _id y está activo)
            st.session_state.admission_patient_data = new_person_data
            st.session_state.admission_patient_code = new_person_data['patient_code']
            st.success("Información de aseguradora actualizada.")
            if warning:
                st.warning(warning)
        else:
            st.error(f"Error al actualizar: {warning}")

    except ValueError as e:
        st.error(f"Error de validación: {e}")
    except Exception as e:
        st.error(f"Error inesperado: {e}")

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

            elif search_term:
                st.caption("Escriba al menos 3 caracteres para buscar.")

    else:
        # Estado: Paciente cargado
        paciente = st.session_state.admission_patient_data
        
        # --- GESTIÓN DE ASEGURADORA (NUEVO) ---
        # Verificamos si ya tiene info de seguro
        insurance_info = paciente.get('insurance_info', {})
        has_insurance = insurance_info.get('has_insurance', False)
        
        # Container para gestión de seguro
        with st.container(border=True):
            st.markdown("#### 🏥 Cobertura Sanitaria")
            
            # 1. ¿Tiene seguro?
            tiene_seguro = st.radio(
                "¿El paciente tiene Aseguradora o Mutua?",
                ["No (Privado)", "Sí"],
                index=1 if has_insurance else 0,
                horizontal=True,
                key="adm_has_insurance_radio"
            )
            
            if tiene_seguro == "Sí":
                from db.repositories.insurers import get_insurers_repository
                repo_insurers = get_insurers_repository()
                insurers_list = repo_insurers.get_all(active_only=True)
                
                # Preparar opciones
                options = ["Seleccionar..."] + [i['name'] for i in insurers_list]
                
                # Pre-selección
                current_insurer_name = insurance_info.get('insurer_name')
                index_sel = 0
                if current_insurer_name in options:
                    index_sel = options.index(current_insurer_name)
                
                selected_insurer_name = st.selectbox("Seleccione la Compañía", options, index=index_sel, key="adm_insurer_select")
                
                if selected_insurer_name != "Seleccionar...":
                    # Buscar objeto completo
                    insurer_obj = next((i for i in insurers_list if i['name'] == selected_insurer_name), None)
                    
                    if insurer_obj:
                        # Mostrar Logo si existe
                        if insurer_obj.get('logo_url'):
                            st.image(insurer_obj['logo_url'], width=100)
                            
                        # Verificar si está admitida
                        if not insurer_obj.get('is_admitted', True):
                            st.error(f"⚠️ La compañía **{selected_insurer_name}** NO está concertada con este centro.")
                            
                            c_priv, c_rej = st.columns(2)
                            with c_priv:
                                if st.button("💶 Pasar a Privado", use_container_width=True):
                                    # Guardar como privado
                                    _update_patient_insurance(paciente, {"has_insurance": False, "type": "Privado"})
                                    st.rerun()
                            with c_rej:
                                if st.button("🚫 Rechazar Admisión", type="primary", use_container_width=True):
                                    st.session_state.admission_decision_mode = 'reject'
                                    st.rerun()
                            
                            # Bloquear continuación normal
                            return False
                        else:
                            # Si es válida y cambió, guardar
                            if selected_insurer_name != current_insurer_name:
                                new_info = {
                                    "has_insurance": True,
                                    "insurer_id": str(insurer_obj['_id']),
                                    "insurer_name": insurer_obj['name'],
                                    "logo_url": insurer_obj.get('logo_url'),
                                    "type": "Aseguradora" if insurer_obj.get('is_insurer') else "Mutua"
                                }
                                _update_patient_insurance(paciente, new_info)
                                st.rerun()
            
            else:
                # Si seleccionó "No (Privado)" y antes tenía seguro, actualizar
                if has_insurance:
                    _update_patient_insurance(paciente, {"has_insurance": False, "type": "Privado"})
                    st.rerun()

        # --- Diálogo de gestión de flujo activo ---
        if 'admission_active_flow' not in st.session_state:
            st.session_state.admission_active_flow = None
        
        # Solo mostrar gestor si hay flujo activo Y NO hemos decidido continuar
        if st.session_state.admission_active_flow and not st.session_state.get('admission_continue_active'):
            st.divider()
            from components.common.active_flow_manager import render_active_flow_manager
            
            def _on_continue():
                st.session_state.admission_continue_active = True
                st.rerun()

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

        # --- Vista de Paciente Seleccionado (Standard Card) ---
        from ui.components.common.patient_card import render_patient_card
        
        def _on_edit(p):
            person_dialog(str(p['_id']), on_save=on_person_save)
            
        def _on_change(p):
            st.session_state.admission_patient_data = None
            st.session_state.admission_patient_validated = False
            st.session_state.admission_active_flow = None
            st.session_state.admission_continue_active = False # Reset
            st.rerun()

        
        # --- Lógica de Impresión de Ticket ---
        if hasattr(st, "dialog"):
            @st.dialog("🖨️ Ticket de Admisión")
            def _open_print_dialog(p):
                from components.admission.patient_ticket import render_ticket_modal
                render_ticket_modal(p)
        else:
            # Fallback para versiones antiguas
            def _open_print_dialog(p):
                st.error("Su versión de Streamlit no soporta diálogos modales.")

        def _on_print(p):
            _open_print_dialog(p)

        actions = [
            {"label": "✏️ Editar", "key": "edit", "on_click": _on_edit},
            {"label": "🔄 Cambiar", "key": "change", "on_click": _on_change},
            {"label": "🖨️ Pulsera", "key": "print", "on_click": _on_print}
        ]
        
        # Si decidimos continuar, mostramos el estado del flujo en la card
        flow_status = None
        if st.session_state.get('admission_continue_active') and st.session_state.admission_active_flow:
            f = st.session_state.admission_active_flow
            sala = f.get('sala_atencion_code') or f.get('sala_destino_code') or f.get('sala_triaje_code') or f.get('sala_admision_code')
            flow_status = {
                "estado": f.get('estado'),
                "sala_actual": sala
            }

        render_patient_card(
            patient=paciente,
            actions=actions,
            show_triage_level=False, # En admisión aún no hay triaje
            show_wait_time=False,
            show_location=False,
            flow_status=flow_status,
            key_prefix="adm_step2"
        )
        
        st.success("✅ Paciente seleccionado y validado.")
        st.session_state.admission_patient_validated = True

    return st.session_state.admission_patient_validated

    st.markdown('<div class="debug-footer">src/components/admission/step_patient_data.py</div>', unsafe_allow_html=True)
