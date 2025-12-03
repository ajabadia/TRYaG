# path: src/components/triage/step_patient_selection.py
# Creado: 2025-11-24
# Última modificación: 2025-11-24
"""
Paso 2 del Asistente de Triaje: Selección de Paciente.
"""
import streamlit as st
from services.patient_flow_service import obtener_pacientes_en_espera
from services.patient_service import calcular_edad
from datetime import datetime
from services.permissions_service import get_current_user

def _get_username():
    user = get_current_user()
    return user.get("username", "unknown") if user else "unknown"

def render_step_patient_selection() -> bool:
    """
    Renderiza la lista de pacientes en espera para la sala seleccionada.
    
    Returns:
        bool: True si hay paciente seleccionado, False en caso contrario.
    """
    st.subheader("2️⃣ Selección de Paciente")
    
    room_code = st.session_state.get('triage_room_code')
    if not room_code:
        st.warning("⚠️ No se ha seleccionado sala.")
        return False

    # 1. Obtener configuración de la sala seleccionada
    from services.room_service import obtener_sala_por_codigo
    sala_config = obtener_sala_por_codigo(room_code)
    
    if not sala_config:
        st.error(f"❌ No se encontró configuración para la sala {room_code}")
        return False

    # --- GESTIÓN DE ACCIONES (REASIGNAR / RECHAZAR) ---
    # (Delegado a patient_card.py con acciones estándar)


    # --- RECUPERACIÓN DE PACIENTES ---
    from services.flow_manager import obtener_pacientes_en_sala, mover_paciente_a_sala
    from services.patient_service import obtener_paciente_por_codigo, calcular_edad
    from services.triage_service import create_draft_triage, get_active_draft, discard_draft
    from services.report_service import generate_triage_pdf
    import unicodedata
    import re
    
    lista_pacientes = []
    blocking_patient = None
    
    # 1. Paciente en sala (Prioritario)
    pacientes_en_atencion = obtener_pacientes_en_sala(room_code)
    
    # Mapa de nombres de salas para visualización
    from ui.config.config_loader import load_centro_config
    config = load_centro_config()
    salas_map = {s['codigo']: s.get('nombre', s['codigo']) for s in config.get('salas', [])}

    if pacientes_en_atencion:
        flujo_activo = pacientes_en_atencion[0]
        datos_paciente = obtener_paciente_por_codigo(flujo_activo['patient_code'])
        if datos_paciente:
            p_full = {**datos_paciente, **flujo_activo}
            p_full['is_in_room'] = True
            p_full['sala_espera_origen'] = room_code 
            p_full['sala_nombre'] = salas_map.get(room_code, room_code)
            lista_pacientes.append(p_full)
            blocking_patient = p_full
            
            st.warning(f"⚠️ La sala está ocupada por **{p_full.get('nombre')} {p_full.get('apellido1')}**. Debe finalizar su atención o reasignarlo para atender a otros.")

    # 2. Pacientes en espera
    salas_espera = sala_config.get('salas_espera_asociadas', [])
    if not salas_espera:
        from services.room_service import obtener_salas_por_tipo
        salas_triaje_espera = [s['codigo'] for s in obtener_salas_por_tipo('triaje') if s.get('subtipo') == 'espera']
        salas_espera = salas_triaje_espera if salas_triaje_espera else []

    for sala_esp in salas_espera:
        flujos = obtener_pacientes_en_sala(sala_esp)
        for flujo in flujos:
            datos_paciente = obtener_paciente_por_codigo(flujo['patient_code'])
            if datos_paciente:
                p_full = {**datos_paciente, **flujo}
                p_full['sala_espera_origen'] = sala_esp
                p_full['sala_nombre'] = salas_map.get(sala_esp, sala_esp)
                p_full['is_in_room'] = False
                lista_pacientes.append(p_full)
    
    if not lista_pacientes:
        st.info(f"ℹ️ No hay pacientes en espera ni en atención.")
        if st.button("🔄 Actualizar lista", use_container_width=True):
            st.rerun()
        return False

    st.markdown(f"**Pacientes:** {len(lista_pacientes)}")
    st.divider()
    
    # Inicializar estado seleccionado
    if 'triage_patient' not in st.session_state:
        st.session_state.triage_patient = None
    
    selected_patient = st.session_state.triage_patient
    
    # Renderizar lista
    from ui.components.common.patient_card import render_patient_card
    
    for p in lista_pacientes:
        is_in_room = p.get('is_in_room', False)
        
        # Bloquear "Atender" si hay alguien en sala y NO es este paciente
        disable_attend = (blocking_patient is not None) and (not is_in_room)
        
        is_selected = bool(selected_patient and 
                     selected_patient.get('patient_code') == p.get('patient_code'))
        
        # Definir callbacks
        def on_attend(patient):
            if patient.get('is_in_room', False):
                # Ya está en sala, solo seleccionamos
                st.session_state.triage_patient = patient
            else:
                # Mover a sala
                try:
                    mover_paciente_a_sala(
                        patient_code=patient.get('patient_code'),
                        sala_destino_code=room_code,
                        sala_destino_tipo="triaje",
                        sala_destino_subtipo="atencion",
                        nuevo_estado="EN_TRIAJE",
                        notas=f"Atendido en {room_code}",
                        usuario=_get_username()
                    )
                    st.session_state.triage_patient = patient
                except Exception as e:
                    st.error(f"Error al mover paciente: {e}")
                    return

            # Pre-rellenar edad
            if 'fecha_nacimiento' in patient:
                fn = patient['fecha_nacimiento']
                if isinstance(fn, str):
                    try: fn = datetime.fromisoformat(fn)
                    except: pass
                st.session_state.datos_paciente['edad'] = calcular_edad(fn)
            
            # --- GESTIÓN DE BORRADORES (DRAFTS) ---
            # (Imports movidos arriba)
            
            patient_code = patient.get('patient_code')
            user_id = _get_username()
            
            # 1. Buscar borrador existente
            draft = get_active_draft(patient_code)
            
            if draft:
                st.toast(f"📂 Recuperando triaje en curso para {patient.get('nombre')}...")
                # Cargar datos del borrador en sesión
                st.session_state.triage_record_id = str(draft['_id'])
                # Restaurar datos si existen en el borrador (pendiente implementar mapeo completo)
                # Por ahora, confiamos en que el usuario rellene, o mapeamos lo básico si guardamos partials
                # Restaurar datos si existen en el borrador
                # Preservar imágenes si ya hubiera en sesión (raro en resume, pero por seguridad)
                saved_images = st.session_state.datos_paciente.get('imagenes', [])
                
                # Definir claves de metadatos a excluir de datos_paciente
                metadata_keys = ['_id', 'patient_id', 'evaluator_id', 'status', 'timestamp', 'audit_id', 'gi_responses']
                
                # Restaurar dinámicamente todo lo que no sea metadata
                for k, v in draft.items():
                    if k not in metadata_keys:
                        st.session_state.datos_paciente[k] = v
                
                # Restaurar imágenes
                st.session_state.datos_paciente['imagenes'] = saved_images

                # Mapeo de compatibilidad inversa (si falta texto_medico pero hay motivo_consulta)
                if 'motivo_consulta' in draft and not st.session_state.datos_paciente.get('texto_medico'):
                    st.session_state.datos_paciente['texto_medico'] = draft['motivo_consulta']

                if 'gi_responses' in draft:
                    st.session_state.gi_responses = draft['gi_responses']
                
                # Restaurar estado de edición para que el usuario vea lo que tenía
                st.session_state.is_editing_text = True
            else:
                # 2. Crear nuevo borrador
                draft_id = create_draft_triage(patient_code, user_id)
                st.session_state.triage_record_id = draft_id

            # --- AUTO-ADVANCE ---
            # En lugar de solo seleccionar, avanzamos directamente al paso 2
            st.session_state.triage_step = 2
            
            # Inicializar estado de triaje limpio (si no es resume)
            if not draft:
                st.session_state.datos_paciente = {
                    "texto_medico": "",
                    "edad": st.session_state.triage_patient.get('edad', 40) if st.session_state.triage_patient else 40,
                    "gender": st.session_state.triage_patient.get('gender'),
                    "dolor": 5,
                    "imagenes": [],
                    "imagenes_confirmadas_ia": [],
                    "vital_signs": {},
                    # Propagar datos de seguro
                    "insurance_info": st.session_state.triage_patient.get('insurance_info', {}),
                    "seguro": st.session_state.triage_patient.get('seguro', '')
                }
                st.session_state.resultado = None
                st.session_state.calificacion_humana = None
                st.session_state.validation_complete = False
                st.session_state.analysis_complete = False
                st.session_state.is_editing_text = True
                st.session_state.show_text_error = False
                st.session_state.modal_image_selection = {}
            
            st.rerun()

        def on_reject(patient):
            st.session_state.triage_action_target = patient
            st.session_state.triage_action_type = 'reject'
            st.rerun()

        def on_reassign(patient):
            st.session_state.triage_action_target = patient
            st.session_state.triage_action_type = 'reassign'
            st.rerun()

        def on_reset(patient):
            """Reiniciar triaje: descartar borrador y limpiar sesión."""
            discard_draft(patient.get('patient_code'))
            st.toast(f"🗑️ Borrador descartado para {patient.get('nombre')}")
            # Limpiar datos en sesión si es el paciente actual
            if st.session_state.triage_patient and st.session_state.triage_patient.get('patient_code') == patient.get('patient_code'):
                 st.session_state.datos_paciente = {
                    "texto_medico": "",
                    "edad": 40, # Se recalculará
                    "dolor": 5,
                    "imagenes": [],
                    "vital_signs": {}
                }
            st.rerun()

        # Verificar si hay borrador activo para este paciente
        active_draft = get_active_draft(p.get('patient_code'))

        # Construir acciones
        actions = []
        
        # Botón Principal (Atender/Continuar)
        # Ahora es "Triar Ahora" o "Retomar Triaje"
        btn_label = "Retomar Triaje" if (is_in_room or active_draft) else "Triar Ahora"
        btn_type = "primary"
        
        # Solo mostrar botón de atender si no está bloqueado o si es el paciente en sala
        # O si queremos mostrarlo deshabilitado, pasamos disabled=True
        
        actions.append({
            "label": btn_label,
            "key": "attend",
            "type": btn_type,
            "on_click": on_attend,
            "disabled": disable_attend and not is_in_room
        })

        # Botón de Reiniciar (Solo si hay borrador)
        if active_draft:
            actions.append({
                "label": "Reiniciar", # Icono se pone en patient_card si se soporta, o texto
                "key": "reset",
                "type": "secondary",
                "on_click": on_reset,
                "help": "Descartar borrador y empezar de cero"
            })

        render_patient_card(
            patient=p,
            actions=actions,
            show_triage_level=False, # En selección de triaje aún no tienen nivel
            show_wait_time=True,
            show_location=True,
            is_in_room=is_in_room,
            key_prefix="triage_sel",
            allow_rejection=True,
            allow_reassignment=True
        )

        # Botón de descarga de borrador (si existe)
        if active_draft:
            try:
                # Preparar datos para el PDF (mezcla de paciente y borrador)
                # El borrador tiene los datos clínicos parciales
                draft_record = {**p, **active_draft}
                draft_record["destination"] = "BORRADOR - EN PROCESO"
                
                pdf_bytes = generate_triage_pdf(draft_record)
                
                raw_name = f"{p.get('nombre', 'Paciente')}_{p.get('apellido1', '')}"
                normalized = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('ASCII')
                safe_name = re.sub(r'[^\w\-_]', '_', normalized)
                file_name = f"Borrador_{safe_name}_{datetime.now().strftime('%H%M')}.pdf"
                
                st.download_button(
                    label="📄 Descargar Borrador PDF",
                    data=pdf_bytes,
                    file_name=file_name,
                    mime="application/pdf",
                    key=f"btn_dl_draft_{p.get('patient_code')}",
                    help="Descargar informe preliminar con los datos capturados hasta ahora"
                )
            except Exception as e:
                st.error(f"Error generando PDF borrador: {e}")

    # Mostrar paciente seleccionado y permitir avanzar
    # (Ya no es necesario porque el botón avanza directo, pero por si acaso queda algo residual)
    if selected_patient:
        # Si llegamos aquí es porque hubo un rerun pero no se cambió el step (raro con la nueva lógica)
        # O si se seleccionó desde otro lado.
        pass
        
    st.markdown('<div class="debug-footer">src/components/triage/step_patient_selection.py</div>', unsafe_allow_html=True)
    return False
