# path: src/components/triage/input_form.py
# Creado: 2025-11-21
# Última modificación: 2025-11-28
import io
import os
import streamlit as st
from PIL import Image
from datetime import datetime
from utils.icons import render_icon
from core.config import get_min_chars_motivo
from components.common.audio_recorder import render_audio_recorder
from components.common.webcam_manager import render_webcam_manager
from components.common.video_recorder import render_video_recorder
from components.common.file_importer import render_file_importer
from components.triage.media_cards import render_media_card
from utils.file_handler import TempFileWrapper, calculate_md5
from core.transcription_handler import get_transcription
from components.triage.patient_background_form import render_patient_background_form
from components.triage.vital_signs import render_vital_signs_form
from utils.ui_utils import load_css
from utils.ui_utils import load_css
from services.simulated_ia import simulacion_ia
from services.triage_service import llamar_modelo_gemini
from components.common.speech_to_text import speech_to_text # Corrección de import


def procesar_respuesta_ia(resultado_ia, algo_result=None):
    """
    Procesa la respuesta de la IA y la guarda en el estado de la sesión.
    Combina con el resultado algorítmico si está disponible.
    """
    final_result = {}
    
    # 1. Base: Algoritmo (si existe)
    if algo_result:
        final_result.update(algo_result)
        
    # 2. IA: Sobrescribe o enriquece
    if resultado_ia and "nivel_sugerido" in resultado_ia:
        niveles_info = {
            1: {"color": "red", "text": "NIVEL I - RESUCITACIÓN"},
            2: {"color": "orange", "text": "NIVEL II - EMERGENCIA"},
            3: {"color": "#FFD700", "text": "NIVEL III - URGENCIA"},
            4: {"color": "green", "text": "NIVEL IV - MENOS URGENTE"},
            5: {"color": "blue", "text": "NIVEL V - NO URGENTE"}
        }
        nivel_num = resultado_ia['nivel_sugerido']
        
        # Actualizar campos clave para compatibilidad con PDF y UI
        final_result["status"] = "SUCCESS"
        final_result["final_priority"] = nivel_num
        final_result["final_color"] = niveles_info.get(nivel_num, {}).get("color", "gray")
        final_result["nivel"] = niveles_info.get(nivel_num, niveles_info[4]) # Estructura legacy para UI
        final_result["razones"] = resultado_ia.get("razonamiento", ["No se proporcionó razonamiento."])
        
        # Preservar wait_time del algoritmo si la IA no lo da (la IA no suele darlo en este prompt)
        if "wait_time" not in final_result:
             final_result["wait_time"] = "N/A"
             
        # Preservar warnings si existen (para UI destacada)
        if "warnings" in resultado_ia:
            final_result["warnings"] = resultado_ia["warnings"]

    else:
        # Si no tiene nivel_sugerido, verificar si tiene la estructura correcta
        if isinstance(resultado_ia, dict) and "nivel" in resultado_ia:
            # Ya tiene la estructura correcta
            final_result.update(resultado_ia)
        else:
            # Error o formato inesperado - crear estructura por defecto
            final_result = {
                "status": resultado_ia.get("status", "ERROR") if isinstance(resultado_ia, dict) else "ERROR",
                "msg": resultado_ia.get("msg", "Error procesando respuesta de IA") if isinstance(resultado_ia, dict) else str(resultado_ia)
            }
            
    # --- GESTIÓN DE HISTORIAL (PHASE 8.7) ---
    if "_ai_response_object" in resultado_ia:
        new_response_obj = resultado_ia["_ai_response_object"]
        
        # Inicializar historial en session_state si no existe
        if "ai_responses_history" not in st.session_state:
            st.session_state.ai_responses_history = []
        
        # Marcar anteriores como 'discarded'
        for resp in st.session_state.ai_responses_history:
            if resp.get("status") == "accepted":
                resp["status"] = "discarded"
        
        # Añadir nueva respuesta
        st.session_state.ai_responses_history.append(new_response_obj)
        
        # Limpiar el objeto temporal del resultado final para no ensuciar la UI
        if "_ai_response_object" in final_result:
            del final_result["_ai_response_object"]

    st.session_state.resultado = final_result

def render_input_form():
    """
    Renderiza el formulario de entrada de datos del paciente.
    """
    reset_count = st.session_state.get('reset_count', 0)

# --- CALLBACKS DE INTEGRACIÓN (MOVIDOS A NIVEL DE MÓDULO) ---

def on_audio_confirmed(audio_wrappers):
    if audio_wrappers:
        if 'imagenes' not in st.session_state.datos_paciente:
            st.session_state.datos_paciente['imagenes'] = []
        
        # Manejar tanto lista como item único por compatibilidad
        if isinstance(audio_wrappers, list):
            st.session_state.datos_paciente['imagenes'].extend(audio_wrappers)
        else:
            st.session_state.datos_paciente['imagenes'].append(audio_wrappers)
            
    st.session_state.triage_input_type = "" # Resetear selector

def on_webcam_close(photos):
    if photos:
        if 'imagenes' not in st.session_state.datos_paciente:
            st.session_state.datos_paciente['imagenes'] = []
        st.session_state.datos_paciente['imagenes'].extend(photos)
    st.session_state.triage_input_type = "" # Resetear selector

def on_video_confirmed(video_wrappers):
    if video_wrappers:
        if 'imagenes' not in st.session_state.datos_paciente:
            st.session_state.datos_paciente['imagenes'] = []
        st.session_state.datos_paciente['imagenes'].extend(video_wrappers)
    st.session_state.triage_input_type = "" # Resetear selector

def on_files_confirmed(files_list):
    if files_list:
        if 'imagenes' not in st.session_state.datos_paciente:
            st.session_state.datos_paciente['imagenes'] = []
        
        # Evitar duplicados por nombre
        current_names = {f.name for f in st.session_state.datos_paciente['imagenes']}
        for f in files_list:
            if f.name not in current_names:
                st.session_state.datos_paciente['imagenes'].append(f)
        
        st.session_state.triage_input_type = "" # Resetear selector

def import_callback():
    import time
    time.sleep(1.5)
    st.session_state.datos_paciente['texto_medico'] += "\n\n[IMPORTADO HCE]: Paciente con antecedentes de hipertensión. Última visita por dolor lumbar crónico."
    st.session_state.triage_input_type = "" # Resetear selector

# --- DEFINICIÓN DE DIÁLOGOS (NIVEL DE MÓDULO) ---
# NOTA: dismissible=False evita que se cierre al hacer click fuera (requiere Streamlit reciente)

@st.dialog("🎤 Grabar Audio", width="large")
def dialog_audio():
    render_audio_recorder(key_prefix="triage_audio", on_audio_ready=on_audio_confirmed)
    
@st.dialog("📷 Tomar Foto", width="large")
def dialog_photo():
    render_webcam_manager(key_prefix="triage_cam", on_close=on_webcam_close)
    
@st.dialog("🎥 Grabar Video", width="large")
def dialog_video():
    render_video_recorder(key_prefix="triage_video", on_video_ready=on_video_confirmed)
    
@st.dialog("📁 Subir Archivo", width="large")
def dialog_file():
    render_file_importer(key_prefix="triage_files", on_files_ready=on_files_confirmed)
    
@st.dialog("🏥 Importar Historial", width="large")
def dialog_history():
    st.markdown("##### 🏥 Importación de Historia Clínica")
    st.info("Simulación de conexión con HCE (Historia Clínica Electrónica).")
    
    c_imp, c_cls = st.columns(2)
    with c_imp:
        if st.button("⬇️ Importar Últimos Informes", key="sim_import_btn", use_container_width=True):
            import_callback()
            st.rerun()
    with c_cls:
        if st.button("❌ Cerrar", key="hist_close_btn", use_container_width=True):
            st.rerun()
    
    st.markdown('<div class="debug-footer">src/components/triage/input_form.py</div>', unsafe_allow_html=True)


def render_input_form():
    """
    Renderiza el formulario de entrada de datos del paciente.
    """
    reset_count = st.session_state.get('reset_count', 0)

    with st.container(border=True):
        # Cabecera de sección con icono
        c_head_icon, c_head_text = st.columns([1, 20])
        with c_head_icon:
             render_icon("user", size=24) 
        with c_head_text:
            st.header("1. Datos del Paciente")

        # --- SELECTOR DE MODO DE TRIAJE (Phase 11.4) ---
        triage_mode = st.radio(
            "Modo de Interacción:",
            ["Estándar (Formulario)", "Conversacional (Chat IA)"],
            horizontal=True,
            key="triage_interaction_mode"
        )
        st.divider()

        is_step1_disabled = st.session_state.analysis_complete
        is_editing = st.session_state.is_editing_text
        
        # --- 🔮 MAGIC CASES (LIQUID UI - DYNAMIC) ---
        # Evaluar el estado del paciente en tiempo real para adaptar la interfaz
        from services.dynamic_ui_rules_engine import DynamicRulesEngine
        
        # Solo ejecutar si hay datos mínimos para evitar ruido
        if st.session_state.datos_paciente.get('texto_medico') or st.session_state.datos_paciente.get('vital_signs'):
            # Instanciar singleton (migra DB si es necesario la primera vez)
            engine = DynamicRulesEngine() 
            ui_adaptations = engine.evaluate(st.session_state.datos_paciente)
            
            # 1. Alertas Clínicas (Top Banner)
            for alert in ui_adaptations.get('alerts', []):
                if alert['type'] == 'critical':
                    st.error(alert['message'], icon="🚨")
                elif alert['type'] == 'warning':
                    st.warning(alert['message'], icon="⚠️")
                else:
                    st.info(alert['message'], icon="ℹ️")
            
            # 2. Sugerencias de Acción (Badges)
            if ui_adaptations.get('suggestions'):
                cols_sug = st.columns(len(ui_adaptations['suggestions']) + 1)
                cols_sug[0].caption("📢 **Protocolos Sugeridos:**")
                for i, sug in enumerate(ui_adaptations['suggestions']):
                    cols_sug[i+1].markdown(f":sparkles: `{sug}`")
        
        # ----------------------------------
        
        # --- LÓGICA DE VISUALIZACIÓN ---
        if triage_mode == "Conversacional (Chat IA)":
             from components.triage.conversational_chat import render_conversational_chat
             render_conversational_chat()
             
             # Sincronización inversa (para que funcione el botón Analizar de abajo)
             # El chat ya actualizará 'texto_medico', asi que no hay nada extra que hacer
             # salvo mostrar los datos administrativos minimos.
             st.divider()
             # Mostramos datos admin básicos aun en modo chat
             from components.triage.admin_data_form import render_admin_data_form
             render_admin_data_form(reset_count, disabled=is_step1_disabled)

        else:
            # --- MODO ESTÁNDAR (código original) ---
            
            # --- DATOS ADMINISTRATIVOS (MODULARIZADO) ---
            from components.triage.admin_data_form import render_admin_data_form
            render_admin_data_form(reset_count, disabled=is_step1_disabled)
            
            # --- SECCIÓN 1: ENTRADA DE DATOS MULTIMODAL ---
            
            # --- SECCIÓN 1: ENTRADA DE DATOS MULTIMODAL (MODALES) ---
            st.markdown("##### 📥 Añadir Información")
            
            col_btns = st.columns(5)
            
            # (Diálogos movidos fuera)
    
            # Botones de acción
            with col_btns[0]:
                if st.button("🎤 Audio", use_container_width=True, disabled=not is_editing or is_step1_disabled):
                    dialog_audio()
            with col_btns[1]:
                if st.button("📷 Foto", use_container_width=True, disabled=not is_editing or is_step1_disabled):
                    dialog_photo()
            with col_btns[2]:
                if st.button("🎥 Video", use_container_width=True, disabled=not is_editing or is_step1_disabled):
                    dialog_video()
            with col_btns[3]:
                if st.button("📁 Archivo", use_container_width=True, disabled=not is_editing or is_step1_disabled):
                    dialog_file()
            with col_btns[4]:
                if st.button("🏥 Historial", use_container_width=True, disabled=not is_editing or is_step1_disabled):
                    dialog_history()
    
            # Obtener contador de reset
            reset_count = st.session_state.get('reset_counter', 0)

        # --- FUNCIÓN LOCAL: RENDERIZADO DE COMPONENTES COMUNES (FORMULARIO MANUAL) ---
        def render_shared_manual_form():
            # --- ENTREVISTA GUIADA ---
            from components.triage.guided_interview import render_guided_interview
            render_guided_interview(disabled=is_step1_disabled, key_suffix=str(reset_count))

            widget_key = f"texto_medico_input_{reset_count}"
            
            # --- Voice Input Integration (Phase 13.1) ---
            from components.triage.native_voice_input import render_native_voice_input
            # Pasamos widget_key para que el componente pueda actualizar el textarea directamente
            render_native_voice_input(reset_count, target_widget_key=widget_key)
            
            
            widget_key = f"texto_medico_input_{reset_count}"
            
            # Evitar warning de Streamlit: "created with a default value but also had its value set via the Session State API"
            # Solo pasamos 'value' si la key NO está en session_state. Si está, Streamlit usa el valor del estado.
            ta_kwargs = {
                "label": "Motivo de Consulta",
                "height": 100,
                "placeholder": "Ej: Varón de 45 años...",
                "disabled": not is_editing or is_step1_disabled,
                "key": widget_key,
                "label_visibility": "collapsed"
            }
            
            if widget_key not in st.session_state:
                ta_kwargs["value"] = st.session_state.datos_paciente.get('texto_medico', '')

            texto_medico = st.text_area(**ta_kwargs)
            st.session_state.datos_paciente['texto_medico'] = texto_medico
            is_text_valid = len(texto_medico) >= get_min_chars_motivo()

            # --- HDA DETALLADA (MODULARIZADO) ---
            from components.triage.hda_form import render_hda_form
            render_hda_form(reset_count, disabled=is_step1_disabled)

            # --- EDAD (Oculto si existe) ---
            default_age = st.session_state.datos_paciente.get('edad', 40)
            # Si no hay edad en datos_paciente (ej: paciente nuevo sin seleccionar), mostrar input
            if 'edad' not in st.session_state.datos_paciente or st.session_state.datos_paciente['edad'] is None:
                 st.session_state.datos_paciente['edad'] = st.number_input("Edad", 0, 120, default_age, disabled=is_step1_disabled, key=f"edad_input_{reset_count}")
            
            # --- CONTEXTO CLÍNICO (MODULARIZADO) ---
            from components.triage.clinical_context import render_clinical_context_form
            render_clinical_context_form(reset_count, disabled=is_step1_disabled)

            # --- ANTECEDENTES CLÍNICO (MODULARIZADO) ---
            render_patient_background_form(reset_count, disabled=is_step1_disabled)
            
            # --- HISTORIA INTEGRAL (NUEVO) ---
            from components.triage.extended_history import render_extended_history_form
            render_extended_history_form(disabled=is_step1_disabled)

            if not is_step1_disabled:
                # Pasamos la edad explícitamente para que vital_signs_form pueda cargar la config correcta
                render_vital_signs_form()
                
                # --- ALERTAS PREDICTIVAS (MODULARIZADO) ---
                # Solo mostrar si hay signos vitales registrados y está habilitado en config
                from db.repositories.general_config import get_general_config_repository
                from components.triage.risk_analysis_panel import render_risk_analysis_panel
                
                # Asegurar config cargada
                if 'general_config' not in st.session_state:
                    st.session_state.general_config = get_general_config_repository().get_config()
                
                enable_predictive = st.session_state.general_config.get('enable_predictive_alerts', True)

                # NOTA: En modo chat, esto solo se muestra si el chat ha finalizado.
                if st.session_state.datos_paciente.get('vital_signs'):
                    render_risk_analysis_panel(st.session_state.datos_paciente, enable_predictive)

            elif 'vital_signs' in st.session_state.datos_paciente:
                 st.info("Signos vitales registrados.")


            if st.session_state.datos_paciente.get('imagenes'):
                    load_css("src/assets/css/components/forms.css")
                    
                    # Marcador para CSS Scoped
                    st.markdown('<span class="media-cards-grid" style="display:none"></span>', unsafe_allow_html=True)

                    num_files = len(st.session_state.datos_paciente['imagenes'])
                    # Crear una columna por archivo para permitir wrapping
                    cols = st.columns(num_files)
                    
                    for i, file_obj in enumerate(st.session_state.datos_paciente['imagenes']):
                        with cols[i]:
                            # Contenedor para la card
                            render_media_card(file_obj, i, disabled=is_step1_disabled)

            # --- BOTONES DE CONFIRMACIÓN (MOVIDO) ---
            if is_editing:
                if st.button("Confirmar Datos", type="primary", disabled=is_step1_disabled, use_container_width=True):
                    if is_text_valid:
                        st.session_state.is_editing_text = False
                        st.session_state.show_text_error = False
                        st.rerun()
                    else:
                        st.session_state.show_text_error = True
                        st.rerun()
                if st.session_state.show_text_error:
                    c_err_icon, c_err_text = st.columns([1, 20])
                    with c_err_icon:
                        render_icon("edit", size=20, color="red")
                    with c_err_text:
                        st.caption(f"Por favor, ingrese al menos {get_min_chars_motivo()} caracteres.")
            else:
                # Botón para volver a editar si no se ha finalizado el análisis
                if not is_step1_disabled:
                    if st.button("Editar datos", icon=":material/edit:", key=f"edit_patient_data_{reset_count}", use_container_width=True):
                        st.session_state.is_editing_text = True
                        st.rerun()

            total_imagenes = len(st.session_state.datos_paciente.get('imagenes', []))
            imagenes_seleccionadas = sum(st.session_state.modal_image_selection.values()) if total_imagenes > 0 else 0
            button_label = f"Analizar con IA ({imagenes_seleccionadas} de {total_imagenes} archivos)" if total_imagenes > 0 else "Analizar con IA"
            is_button_disabled = not is_text_valid or st.session_state.is_editing_text or is_step1_disabled


            if total_imagenes > 0:
                c_lock_icon, c_lock_text = st.columns([1, 20])
                with c_lock_icon:
                    render_icon("lock", size=16, color="gray")
                with c_lock_text:
                    st.caption("**Aviso de Privacidad:** Al hacer clic, consiente el envío de los archivos a Google Gemini.")

            col_analisis_1, col_analisis_2 = st.columns(2)
            with col_analisis_1:
                if st.button("Analizar sin IA", disabled=is_button_disabled, use_container_width=True):
                    with st.spinner("Ejecutando simulación..."):
                        st.session_state.datos_paciente['imagenes_confirmadas_ia'] = []
                        
                        # --- CÁLCULO DE TRIAJE AUTOMÁTICO (WORST CASE) ---
                        from components.triage.vital_signs import get_all_configs
                        from components.triage.triage_logic import calculate_worst_case, calculate_ptr_score
                        
                        configs = get_all_configs(st.session_state.datos_paciente.get('edad', 40))
                        triage_result = calculate_worst_case(st.session_state.datos_paciente.get('vital_signs', {}), configs)
                        
                        # --- CÁLCULO PTR ---
                        vs_for_ptr = st.session_state.datos_paciente.get('vital_signs', {}).copy()
                        vs_for_ptr['dolor'] = st.session_state.datos_paciente.get('dolor', 0)
                        
                        ptr_result = calculate_ptr_score(
                            vs_for_ptr,
                            st.session_state.datos_paciente
                        )
                        triage_result['ptr_result'] = ptr_result

                        # Simulación
                        resultado_simulado = simulacion_ia(
                            st.session_state.datos_paciente['texto_medico'], 
                            st.session_state.datos_paciente['edad'], 
                            st.session_state.datos_paciente['dolor']
                        )
                        
                        # --- INTEGRACIÓN RAG (Retrieval Only) ---
                        # Aunque sea "Sin IA Generativa", usamos el buscador vectorial para sugerir protocolos
                        try:
                            from services.rag_service import get_rag_service
                            rag = get_rag_service()
                            # Buscar 2 fragmentos relevantes
                            rag_docs = rag.search_documents(st.session_state.datos_paciente['texto_medico'], n_results=2)
                            
                            if rag_docs:
                                resultado_simulado['razonamiento'].append("--- 📚 PROTOCOLOS SUGERIDOS (RAG) ---")
                                for doc in rag_docs:
                                    source = doc['metadata'].get('source', 'Desconocido')
                                    content_preview = doc['content'][:150].replace("\\n", " ") + "..."
                                    resultado_simulado['razonamiento'].append(f"📄 [{source}]: {content_preview}")
                        except Exception as e:
                            print(f"RAG Error in Manual Mode: {e}")
                        
                        # Procesar igual que la IA real
                        procesar_respuesta_ia(resultado_simulado, algo_result=triage_result)
                        st.session_state.analysis_complete = True
                        st.rerun()
            
            with col_analisis_2:
                # Botón principal con icono
                # Si ya hay análisis completo, mostrar opción de Regenerar
                if st.session_state.analysis_complete:
                    if st.button("🔄 Regenerar Respuesta IA", type="secondary", disabled=is_button_disabled, use_container_width=True, help="Generar una nueva respuesta y archivar la actual"):
                        with st.spinner("Regenerando análisis..."):
                            # Lógica idéntica a la llamada normal, el servicio se encarga de versionar
                            pass # Se ejecutará el bloque de abajo porque el botón retorna True
                    else:
                        # Si no se pulsa regenerar, y ya está completo, no hacemos nada (evita re-ejecución automática al refrescar)
                        # PERO: necesitamos que el botón original "Analizar" no se muestre o cambie de estado.
                        # Mejor estrategia: Si analysis_complete, cambiamos el botón a "Regenerar".
                        pass

                # Botón de Análisis (o Regeneración si se pulsa)
                btn_text = "🔄 Regenerar Respuesta" if st.session_state.analysis_complete else button_label
                btn_type = "secondary" if st.session_state.analysis_complete else "primary"
                
                if st.button(btn_text, type=btn_type, disabled=is_button_disabled, use_container_width=True, key="btn_analyze_main"):
                    with st.spinner("Contactando con la IA..."):
                        imagenes_a_enviar = [f for f in st.session_state.datos_paciente.get('imagenes', []) if st.session_state.modal_image_selection.get(f.name)]
                        st.session_state.datos_paciente['imagenes_confirmadas_ia'] = imagenes_a_enviar
                        
                        # Preparar texto enriquecido con transcripciones y entrevista
                        texto_completo = st.session_state.datos_paciente['texto_medico']
                        
                        # Buscar transcripciones de audios seleccionados
                        transcripciones_extra = []
                        for f in imagenes_a_enviar:
                            # Verificar si es audio
                            is_audio_file = False
                            if isinstance(f, TempFileWrapper):
                                 is_audio_file = f.name.startswith("audio_") or f.name.endswith(('.wav', '.mp3', '.ogg', '.webm', '.mp4', '.mov', '.avi'))
                            elif hasattr(f, 'name'):
                                 is_audio_file = f.name.endswith(('.wav', '.mp3', '.ogg', '.webm', '.mp4', '.mov', '.avi'))
                            
                            if is_audio_file:
                                md5 = calculate_md5(f)
                                trans = get_transcription(md5)
                                if trans:
                                    # Usar sended_text si existe, sino fallback
                                    text_to_send = trans.get('sended_text', '')
                                    if not text_to_send:
                                         user_text = trans.get('spanish_user_text', '')
                                         ia_text = trans.get('translated_ia_text', trans.get('spanish_text', ''))
                                         text_to_send = user_text if user_text else ia_text
                                    
                                    if text_to_send:
                                        # Formatear con metadatos extra si existen
                                        extra_info = []
                                        prosody = trans.get('emotional_prosody')
                                        relevance = trans.get('relevance')
                                        
                                        if prosody and prosody != "No aplicable":
                                            extra_info.append(f"Prosodia: {prosody}")
                                        if relevance is not None:
                                            extra_info.append(f"Relevancia: {relevance}/9")
                                        
                                        info_str = f" [{', '.join(extra_info)}]" if extra_info else ""
                                        transcripciones_extra.append(f"Transcripción Audio ({f.name}): {text_to_send}{info_str}")

                        if transcripciones_extra:
                            texto_completo += "\\n\\n" + "\\n".join(transcripciones_extra)

                        # Filtrar imágenes reales para la preview/envío legacy
                        imagenes_reales = [f for f in imagenes_a_enviar if not isinstance(f, TempFileWrapper) or (not f.name.startswith("audio_") and not f.name.endswith(('.wav', '.mp3')))]
                        imagen_pil = Image.open(imagenes_reales[0]) if imagenes_reales else None
                        
                        # --- CÁLCULO DE TRIAJE AUTOMÁTICO (WORST CASE) ---
                        from components.triage.vital_signs import get_all_configs
                        from components.triage.triage_logic import calculate_worst_case, calculate_ptr_score
                        
                        configs = get_all_configs(st.session_state.datos_paciente.get('edad', 40))
                        triage_result = calculate_worst_case(st.session_state.datos_paciente.get('vital_signs', {}), configs)
                        
                        # --- CÁLCULO PTR (NUEVO) ---
                        # Preparar signos vitales enriquecidos con dolor
                        vs_for_ptr = st.session_state.datos_paciente.get('vital_signs', {}).copy()
                        vs_for_ptr['dolor'] = st.session_state.datos_paciente.get('dolor', 0)
                        
                        ptr_result = calculate_ptr_score(
                            vs_for_ptr,
                            st.session_state.datos_paciente
                        )
                        triage_result['ptr_result'] = ptr_result
                        
                        # Verificar Modo Contingencia
                        from services.contingency_service import is_contingency_active, save_triage_locally
                        
                        if is_contingency_active():
                            # Lógica Manual (Directo a DB)
                            st.info("🛠️ MODO MANUAL: Guardando directamente en Base de Datos (Sin IA).")
                            
                            # Construir resultado manual
                            manual_result = {
                                "status": "SUCCESS",
                                "nivel_sugerido": triage_result.get('final_priority', 5),
                                "razonamiento": [
                                    "Modo Manual Activo.",
                                    f"Clasificación basada en signos vitales: {triage_result.get('label')}",
                                    "Análisis IA omitido por usuario."
                                ],
                                "final_priority": triage_result.get('final_priority', 5),
                                "final_color": triage_result.get('color', 'gray'),
                                "nivel": {
                                    "text": triage_result.get('label', 'Nivel V'),
                                    "color": triage_result.get('color', 'gray')
                                }
                            }
                            
                            st.session_state.resultado = manual_result
                            
                            # Guardar en DB (usando el servicio de flujo)
                            from services.patient_flow_service import save_triage_data
                            
                            # Preparar datos completos para guardado
                            full_data = {
                                "datos_paciente": st.session_state.datos_paciente,
                                "resultado": manual_result,
                                "evaluator_id": st.session_state.current_user['username'] if 'current_user' in st.session_state else 'unknown',
                                "contingency_mode": True, # Flag para indicar que fue manual
                                "is_training": st.session_state.get('training_mode', False)
                            }
                            
                            patient_code = st.session_state.datos_paciente.get('patient_code', 'unknown')
                            
                            if save_triage_data(patient_code, full_data):
                                st.success("✅ Triaje guardado correctamente en Base de Datos.")
                            else:
                                st.error("❌ Error al guardar en Base de Datos.")
                            
                            st.session_state.analysis_complete = True
                            st.rerun()
                            
                        else:
                            # Lógica Online (IA)
                            # Preparar datos de alergias (Priorizar info completa)
                            alergias_info = st.session_state.datos_paciente.get('alergias_info_completa')
                            if not alergias_info:
                                # Fallback a lógica antigua
                                alergias_info = st.session_state.datos_paciente.get('alergias_selector', 'No')

                            # Combinar antecedentes legacy con historia integral
                            antecedentes_legacy = st.session_state.datos_paciente.get('antecedentes', '')
                            historia_integral = st.session_state.datos_paciente.get('historia_integral', '')
                            
                            # --- GUARDAR TRANSCRIPCIÓN DEL CHAT (Phase 11.4) ---
                            if 'chat_history' in st.session_state and st.session_state.chat_history:
                                 st.session_state.datos_paciente['chat_transcript'] = st.session_state.chat_history
                            
                            # Llamada a la IA
                            try:
                                resultado_ia, final_prompt = llamar_modelo_gemini(
                                    motivo=texto_completo,
                                    edad=st.session_state.datos_paciente.get('edad'),
                                    dolor=st.session_state.datos_paciente.get('dolor', 0),
                                    vital_signs=st.session_state.datos_paciente.get('vital_signs', {}),
                                    imagen=imagen_pil,
                                    triage_result=triage_result,
                                    antecedentes=antecedentes_legacy,
                                    alergias=alergias_info,
                                    gender=st.session_state.datos_paciente.get('gender'),
                                    criterio_geriatrico=st.session_state.datos_paciente.get('criterio_geriatrico', False),
                                    criterio_inmunodeprimido=st.session_state.datos_paciente.get('criterio_inmunodeprimido', False),
                                    criterio_inmunodeprimido_det=st.session_state.datos_paciente.get('criterio_inmunodeprimido_det', ''),
                                    extended_history=historia_integral,
                                    nursing_assessment=st.session_state.datos_paciente.get('nursing_assessment')
                                )
                                
                                # Manejo de Errores de Conexión / Sugerencia de Contingencia
                                if isinstance(resultado_ia, dict) and resultado_ia.get("suggest_contingency"):
                                    st.error(f"⚠️ {resultado_ia.get('msg')}")
                                    st.warning("Parece que hay problemas de conexión con la IA. Se recomienda activar el modo offline.")
                                    
                                    c_cont1, c_cont2 = st.columns(2)
                                    with c_cont1:
                                        if st.button("📴 Activar Modo Contingencia", type="primary", key="btn_activate_contingency_error"):
                                            from services.contingency_service import set_contingency_mode
                                            set_contingency_mode(True)
                                            st.rerun()
                                    with c_cont2:
                                        if st.button("🔄 Reintentar", key="btn_retry_ai_error"):
                                            st.rerun()
                                    
                                    # Detener ejecución para no guardar error como resultado
                                    st.stop()
                                
                                procesar_respuesta_ia(resultado_ia, algo_result=triage_result)
                                st.session_state.analysis_complete = True
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error crítico al contactar con la IA: {str(e)}")
                                st.warning("El servicio de IA no está disponible. Puede reintentar o usar el modo manual.")
                                
                                col_err_1, col_err_2 = st.columns(2)
                                with col_err_1:
                                    if st.button("🔄 Reintentar Análisis", key="btn_retry_exception"):
                                        st.rerun()
                                with col_err_2:
                                    if st.button("📝 Continuar Manualmente (Sin IA)", key="btn_manual_fallback", type="primary"):
                                        # Simular resultado manual/fallido para permitir avanzar
                                        st.session_state.resultado = {
                                            "status": "MANUAL_FALLBACK",
                                            "nivel_sugerido": triage_result.get('final_priority', 5),
                                            "razonamiento": ["Fallo del sistema IA.", f"Error: {str(e)}", "Clasificación basada en signos vitales."]
                                        }
                                        st.session_state.analysis_complete = True
                                        st.rerun()
                                st.stop()


        # --- LÓGICA DE VISUALIZACIÓN DE FORMULARIO COMÚN ---
        if triage_mode == "Conversacional (Chat IA)":
             if st.session_state.get('chat_completed', False):
                 st.divider()
                 render_shared_manual_form()
        else:
             render_shared_manual_form()

    st.markdown('<div class="debug-footer">src/components/triage/input_form.py</div>', unsafe_allow_html=True)
