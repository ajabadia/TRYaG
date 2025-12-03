# path: src/components/triage/step_final_disposition.py
# Creado: 2025-12-01
"""
Paso 5 del Asistente de Triaje: Destino Final.
Permite asignar sala de espera, rechazar o devolver a admisión.
"""
import streamlit as st
from datetime import datetime
from services.patient_flow_service import completar_triaje, rechazar_paciente, reassign_patient_flow, save_triage_data
from services.room_service import obtener_salas_por_tipo

def render_step_final_disposition():
    """Renderiza las opciones de destino final post-triaje."""
    st.markdown("### 5. Destino y Derivación")
    
    p = st.session_state.get('triage_patient')
    if not p:
        st.error("No hay paciente activo.")
        return False
        
    st.info(f"Paciente: **{p.get('nombre')} {p.get('apellido1')}** | Triaje Completado")
    
    # --- Generación de Informe ---
    from services.report_service import generate_triage_pdf
    
    col_print, col_space = st.columns([1, 4])
    with col_print:
        # Construir registro para el reporte usando helper
        from utils.triage_utils import get_current_triage_record
        record = get_current_triage_record()
        
        # Determinar destino provisional para el PDF si ya hay selección
        dest = "Pendiente de asignación"
        if st.session_state.get('selected_espera_code'):
            dest = f"Box: {st.session_state.get('selected_espera_code')}"
        elif st.session_state.get('selected_consulta_code'):
            dest = f"Consulta: {st.session_state.get('selected_consulta_code')}"
        record["destination"] = dest
        
        pdf_bytes = generate_triage_pdf(record)
        
        # Nombre del archivo (Sanitizado ASCII)
        import re
        import unicodedata
        raw_name = f"{p.get('nombre')}_{p.get('apellido1')}"
        normalized = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('ASCII')
        safe_name = re.sub(r'[^\w\-_]', '_', normalized)
        
        file_name = f"Triaje_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        st.download_button(
            label="🖨️ Descargar Hoja de Triaje",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/octet-stream",
            type="primary",
            icon="📄",
            use_container_width=True
        )
    
    st.divider()
    
    tab_espera, tab_consulta, tab_rechazo, tab_admision = st.tabs([
        "🏥 Boxes (Urgencias)", 
        "👨‍⚕️ Consulta / Ingreso",
        "🚫 Alta / Rechazo", 
        "🔙 Devolver a Admisión"
    ])
    
    # --- Opción 1: Boxes (Urgencias) ---
    with tab_espera:
        st.markdown("Asignar a una sala de espera de Boxes.")
        from components.common.room_card import render_room_list
        
        current_selection = st.session_state.get('selected_espera_code')
        
        # Si hay selección, mostrar confirmación arriba
        if current_selection:
            col_info, col_change = st.columns([3, 1])
            with col_info:
                st.info(f"📍 Destino seleccionado: **{current_selection}**")
            with col_change:
                if st.button("🔄 Cambiar Sala", key="change_box_dest"):
                    st.session_state.selected_espera_code = None
                    st.rerun()
            
            if st.button("Confirmar Derivación a Box", type="primary", use_container_width=True):
                # Guardar datos completos antes de derivar
                full_data = {
                    "datos_paciente": st.session_state.datos_paciente,
                    "resultado": st.session_state.resultado,
                    "evaluator_id": "system", # TODO: Usar usuario real
                    "contingency_mode": st.session_state.get('contingency_mode', False),
                    "is_training": st.session_state.get('training_mode', False)
                }
                save_triage_data(p['patient_code'], full_data)
                
                if completar_triaje(p['patient_code'], current_selection):
                    st.success(f"Paciente derivado a {current_selection}")
                    st.session_state.triage_step = 1 # Volver a lista
                    st.session_state.triage_patient = None
                    st.session_state.selected_espera_code = None
                    st.session_state.validation_complete = False
                    st.session_state.analysis_complete = False
                    st.session_state.resultado = None
                    st.rerun()
                else:
                    st.error("Error al derivar paciente.")
        else:
            # Mostrar List
            # Obtener salas de espera de boxes (tipo box, subtipo espera)
            salas_box = obtener_salas_por_tipo("box")
            salas_espera = [s for s in salas_box if s.get('subtipo') == 'espera']
            
            if not salas_espera:
                st.warning("No hay salas de espera de boxes configuradas.")
            else:
                selected_espera = render_room_list(
                    salas=salas_espera,
                    selected_code=st.session_state.get('selected_espera_code'),
                    button_key_prefix="disp_espera"
                )
                
                if selected_espera:
                    st.session_state.selected_espera_code = selected_espera
                    st.rerun()

    # --- Opción 2: Consulta / Ingreso ---
    with tab_consulta:
        st.markdown("Derivar a Consulta Externa o Ingreso.")
        from components.common.room_card import render_room_list
        
        current_cons = st.session_state.get('selected_consulta_code')
        
        if current_cons:
            col_info, col_change = st.columns([3, 1])
            with col_info:
                st.info(f"📍 Destino seleccionado: **{current_cons}**")
            with col_change:
                if st.button("🔄 Cambiar Sala", key="change_cons_dest"):
                    st.session_state.selected_consulta_code = None
                    st.rerun()
            
            if st.button("Confirmar Derivación a Consulta", type="primary", use_container_width=True):
                # Guardar datos completos
                full_data = {
                    "datos_paciente": st.session_state.datos_paciente,
                    "resultado": st.session_state.resultado,
                    "evaluator_id": "system",
                    "contingency_mode": st.session_state.get('contingency_mode', False),
                    "is_training": st.session_state.get('training_mode', False)
                }
                save_triage_data(p['patient_code'], full_data)
                
                if completar_triaje(p['patient_code'], current_cons):
                    st.success(f"Paciente derivado a {current_cons}")
                    st.session_state.triage_step = 1
                    st.session_state.triage_patient = None
                    st.session_state.selected_consulta_code = None
                    st.session_state.validation_complete = False
                    st.session_state.analysis_complete = False
                    st.session_state.resultado = None
                    st.rerun()
                else:
                    st.error("Error al derivar paciente.")
        else:
            # Obtener salas de consulta/ingreso
            salas_consulta = obtener_salas_por_tipo("consulta_ingreso")
            # Filtrar por espera si existe, sino mostrar todas (o atención directa)
            salas_consulta_espera = [s for s in salas_consulta if s.get('subtipo') == 'espera']
            if not salas_consulta_espera:
                 # Si no hay espera específica, mostrar las de atención (derivación directa)
                 salas_consulta_espera = [s for s in salas_consulta if s.get('subtipo') == 'atencion']
    
            if not salas_consulta_espera:
                st.warning("No hay salas de consulta/ingreso configuradas.")
            else:
                selected_consulta = render_room_list(
                    salas=salas_consulta_espera,
                    selected_code=st.session_state.get('selected_consulta_code'),
                    button_key_prefix="disp_consulta"
                )
                
                if selected_consulta:
                    st.session_state.selected_consulta_code = selected_consulta
                    st.rerun()

    # --- Opción 3: Rechazar / Alta ---
    with tab_rechazo:
        motivo = st.text_area("Motivo de rechazo o alta directa", placeholder="Ej: No requiere atención urgente, derivado a AP.")
        if st.button("Confirmar Rechazo/Alta", type="primary", disabled=not motivo):
            if rechazar_paciente(p['patient_code'], motivo):
                st.success("Paciente rechazado/dado de alta.")
                st.session_state.triage_step = 1
                st.session_state.triage_patient = None
                st.rerun()
            else:
                st.error("Error al rechazar paciente.")

    # --- Opción 4: Devolver a Admisión ---
    with tab_admision:
        st.warning("Devolver paciente a la cola de admisión (ej. datos incorrectos).")
        salas_adm = obtener_salas_por_tipo("admision")
        sala_adm_code = st.selectbox("Sala de Admisión Destino", [s['codigo'] for s in salas_adm], format_func=lambda x: next((s['nombre'] for s in salas_adm if s['codigo'] == x), x))
        
        if st.button("Devolver a Admisión"):
            if reassign_patient_flow(p['patient_code'], new_sala_admision_code=sala_adm_code):
                st.success(f"Paciente devuelto a admisión {sala_adm_code}")
                st.session_state.triage_step = 1
                st.session_state.triage_patient = None
                st.rerun()
            else:
                st.error("Error al reasignar.")

    return True

    st.markdown('<div class="debug-footer">src/components/triage/step_final_disposition.py</div>', unsafe_allow_html=True)
