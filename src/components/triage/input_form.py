# path: src/components/triage/input_form.py
# Creado: 2025-11-21
# Última modificación: 2025-11-28
import io
import os
import streamlit as st
from PIL import Image
from datetime import datetime

from services.triage_service import llamar_modelo_gemini
from services.simulated_ia import simulacion_ia
from utils.icons import render_icon
from utils.file_handler import save_file_to_temp, cleanup_temp_files, calculate_md5, TempFileWrapper
from src.core.transcription_handler import get_transcription
from config import get_min_chars_motivo
from components.triage.media_cards import render_media_card
from components.common.webcam_manager import render_webcam_manager
from components.common.audio_recorder import render_audio_recorder
from ui.components.common.video_recorder import render_video_recorder
from components.common.file_importer import render_file_importer
from components.triage.vital_signs_form import render_vital_signs_form, render_vital_sign_input
from components.triage.patient_background_form import render_patient_background_form

def procesar_respuesta_ia(resultado_ia):
    """
    Procesa la respuesta de la IA y la guarda en el estado de la sesión.
    """
    if resultado_ia and "nivel_sugerido" in resultado_ia:
        niveles_info = {
            1: {"color": "red", "text": "NIVEL I - RESUCITACIÓN"},
            2: {"color": "orange", "text": "NIVEL II - EMERGENCIA"},
            3: {"color": "#FFD700", "text": "NIVEL III - URGENCIA"},
            4: {"color": "green", "text": "NIVEL IV - MENOS URGENTE"},
            5: {"color": "blue", "text": "NIVEL V - NO URGENTE"}
        }
        nivel_num = resultado_ia['nivel_sugerido']
        st.session_state.resultado = {
            "status": "SUCCESS",
            "nivel": niveles_info.get(nivel_num, niveles_info[4]),
            "razones": resultado_ia.get("razonamiento", ["No se proporcionó razonamiento."])
        }
    else:
        # Si no tiene nivel_sugerido, verificar si tiene la estructura correcta
        if isinstance(resultado_ia, dict) and "nivel" in resultado_ia:
            # Ya tiene la estructura correcta
            st.session_state.resultado = resultado_ia
        else:
            # Error o formato inesperado - crear estructura por defecto
            st.session_state.resultado = {
                "status": resultado_ia.get("status", "ERROR") if isinstance(resultado_ia, dict) else "ERROR",
                "msg": resultado_ia.get("msg", "Error procesando respuesta de IA") if isinstance(resultado_ia, dict) else str(resultado_ia)
            }

def render_input_form():
    """
    Renderiza el formulario de entrada de datos del paciente.
    """
    reset_count = st.session_state.get('reset_count', 0)

    # --- CALLBACKS DE INTEGRACIÓN ---
    
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

    # --- END CALLBACKS ---

    with st.container(border=True):
        # Cabecera de sección con icono
        c_head_icon, c_head_text = st.columns([1, 20])
        with c_head_icon:
             render_icon("user", size=24) 
        with c_head_text:
            st.header("1. Datos del Paciente")

        is_step1_disabled = st.session_state.analysis_complete
        is_editing = st.session_state.is_editing_text
        
        # --- DATOS ADMINISTRATIVOS (NUEVO) ---
        with st.expander("📋 Datos Administrativos y Logística", expanded=False):
            c_adm1, c_adm2, c_adm3 = st.columns(3)
            with c_adm1:
                st.session_state.datos_paciente['fuente_informacion'] = st.selectbox(
                    "Fuente de Información", 
                    ["Paciente", "Familiar/Cuidador", "Servicio de Emergencias (EMS)", "Testigos", "Otro"],
                    index=0, disabled=is_step1_disabled, key=f"admin_source_{reset_count}"
                )
            with c_adm2:
                st.session_state.datos_paciente['referencia'] = st.text_input(
                    "Médico/Centro Referente", 
                    value=st.session_state.datos_paciente.get('referencia', ''),
                    placeholder="Ej. CAP Norte, Dr. Smith",
                    disabled=is_step1_disabled, key=f"admin_ref_{reset_count}"
                )
            with c_adm3:
                st.session_state.datos_paciente['seguro'] = st.text_input(
                    "Situación de Aseguramiento",
                    value=st.session_state.datos_paciente.get('seguro', ''),
                    placeholder="Ej. Seguridad Social, Privado...",
                    disabled=is_step1_disabled, key=f"admin_ins_{reset_count}"
                )
        
        # --- SECCIÓN 1: ENTRADA DE DATOS MULTIMODAL ---
        
        # --- SECCIÓN 1: ENTRADA DE DATOS MULTIMODAL (MODALES) ---
        st.markdown("##### 📥 Añadir Información")
        
        col_btns = st.columns(5)
        
        # Definir diálogos
        # NOTA: dismissible=False evita que se cierre al hacer click fuera (requiere Streamlit reciente)
        @st.dialog("🎤 Grabar Audio", width="large", dismissible=False)
        def dialog_audio():
            render_audio_recorder(key_prefix="triage_audio", on_audio_ready=on_audio_confirmed)
            
        @st.dialog("📷 Tomar Foto", width="large", dismissible=False)
        def dialog_photo():
            render_webcam_manager(key_prefix="triage_cam", on_close=on_webcam_close)
            
        @st.dialog("🎥 Grabar Video", width="large", dismissible=False)
        def dialog_video():
            render_video_recorder(key_prefix="triage_video", on_video_ready=on_video_confirmed)
            
        @st.dialog("📁 Subir Archivo", width="large", dismissible=False)
        def dialog_file():
            render_file_importer(key_prefix="triage_files", on_files_ready=on_files_confirmed)
            
        @st.dialog("🏥 Importar Historial", width="large", dismissible=False)
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
            
            st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/input_form.py</div>', unsafe_allow_html=True)

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

        texto_medico = st.text_area(
            "Motivo de Consulta", st.session_state.datos_paciente.get('texto_medico', ''),
            height=100, placeholder="Ej: Varón de 45 años...",
            disabled=not is_editing or is_step1_disabled, key=f"texto_medico_input_{reset_count}",
            label_visibility="collapsed"
        )
        st.session_state.datos_paciente['texto_medico'] = texto_medico
        is_text_valid = len(texto_medico) >= get_min_chars_motivo()

        # --- HDA DETALLADA (NUEVO) ---
        with st.expander("🧐 Historia de la Enfermedad Actual (HDA - ALICIA)", expanded=False):
            st.caption("Desglose estructurado del motivo de consulta.")
            c_hda1, c_hda2 = st.columns(2)
            with c_hda1:
                st.session_state.datos_paciente['hda_aparicion'] = st.text_input("Aparición (Inicio)", value=st.session_state.datos_paciente.get('hda_aparicion', ''), disabled=is_step1_disabled, key=f"hda_onset_{reset_count}")
                st.session_state.datos_paciente['hda_localizacion'] = st.text_input("Localización", value=st.session_state.datos_paciente.get('hda_localizacion', ''), disabled=is_step1_disabled, key=f"hda_loc_{reset_count}")
                st.session_state.datos_paciente['hda_intensidad'] = st.text_input("Intensidad", value=st.session_state.datos_paciente.get('hda_intensidad', ''), disabled=is_step1_disabled, key=f"hda_int_{reset_count}")
            with c_hda2:
                st.session_state.datos_paciente['hda_caracteristicas'] = st.text_input("Características (Tipo dolor)", value=st.session_state.datos_paciente.get('hda_caracteristicas', ''), disabled=is_step1_disabled, key=f"hda_char_{reset_count}")
                st.session_state.datos_paciente['hda_irradiacion'] = st.text_input("Irradiación", value=st.session_state.datos_paciente.get('hda_irradiacion', ''), disabled=is_step1_disabled, key=f"hda_rad_{reset_count}")
                st.session_state.datos_paciente['hda_alivio'] = st.text_input("Alivio/Agravantes", value=st.session_state.datos_paciente.get('hda_alivio', ''), disabled=is_step1_disabled, key=f"hda_agg_{reset_count}")
            
            st.divider()
            c_hda3, c_hda4 = st.columns(2)
            with c_hda3:
                st.session_state.datos_paciente['hda_sintomas_asoc'] = st.text_area("Síntomas Acompañantes", value=st.session_state.datos_paciente.get('hda_sintomas_asoc', ''), height=68, placeholder="Fiebre, náuseas...", disabled=is_step1_disabled, key=f"hda_assoc_{reset_count}")
            with c_hda4:
                st.session_state.datos_paciente['hda_tratamiento_casa'] = st.text_area("Tratamiento Domiciliario", value=st.session_state.datos_paciente.get('hda_tratamiento_casa', ''), height=68, placeholder="Qué tomó antes de venir...", disabled=is_step1_disabled, key=f"hda_home_tx_{reset_count}")

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
            render_vital_signs_form(age=st.session_state.datos_paciente.get('edad'))
            
            # --- ALERTAS PREDICTIVAS (MODULARIZADO) ---
            # Solo mostrar si hay signos vitales registrados y está habilitado en config
            from src.db.repositories.general_config import get_general_config_repository
            from components.triage.risk_analysis_panel import render_risk_analysis_panel
            
            # Asegurar config cargada
            if 'general_config' not in st.session_state:
                st.session_state.general_config = get_general_config_repository().get_config()
            
            enable_predictive = st.session_state.general_config.get('enable_predictive_alerts', True)

            if st.session_state.datos_paciente.get('vital_signs'):
                render_risk_analysis_panel(st.session_state.datos_paciente, enable_predictive)

        elif 'vital_signs' in st.session_state.datos_paciente:
             st.info("Signos vitales registrados.")





        if st.session_state.datos_paciente.get('imagenes'):
            with st.container(border=True):
                c_info_icon, c_info_text, c_refresh = st.columns([1, 15, 4])
                with c_info_icon:
                    render_icon("info", size=20, color="#17a2b8")
                with c_info_text:
                    st.info("Marca 'Analizar con IA' en los archivos que deseas enviar.")
                with c_refresh:
                    if st.button("🔄 Actualizar", key="btn_refresh_media", help="Recargar lista de archivos", use_container_width=True):
                        st.rerun()
                
                # CSS para Grid Responsivo (Scoped)
                st.markdown("""
                    <style>
                    /* Target container with border (wrapper) or standard block */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.media-cards-grid) [data-testid="stHorizontalBlock"],
                    div[data-testid="stVerticalBlock"]:has(.media-cards-grid) [data-testid="stHorizontalBlock"] {
                        flex-wrap: wrap !important;
                        flex-direction: row !important;
                        gap: 10px !important;
                    }
                    
                    /* Target columns */
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.media-cards-grid) [data-testid="column"],
                    div[data-testid="stVerticalBlock"]:has(.media-cards-grid) [data-testid="column"] {
                        flex: 1 1 300px !important;
                        min-width: 300px !important;
                        max-width: 33% !important;
                        width: auto !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
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
                    resultado_simulado = simulacion_ia(st.session_state.datos_paciente['texto_medico'], st.session_state.datos_paciente['edad'], st.session_state.datos_paciente['dolor'])
                    st.session_state.resultado = resultado_simulado
                    if resultado_simulado and resultado_simulado.get("status") == "SUCCESS":
                        st.session_state.analysis_complete = True
                    st.rerun()
        
        with col_analisis_2:
            # Botón principal con icono (simulado en texto o label si es posible, pero st.button no soporta markdown/html en label facilmente, se deja texto limpio)
            if st.button(button_label, type="primary", disabled=is_button_disabled, use_container_width=True):
                with st.spinner("Contactando con la IA..."):
                    imagenes_a_enviar = [f for f in st.session_state.datos_paciente.get('imagenes', []) if st.session_state.modal_image_selection.get(f.name)]
                    st.session_state.datos_paciente['imagenes_confirmadas_ia'] = imagenes_a_enviar
                    
                    # Preparar texto enriquecido con transcripciones
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
                        texto_completo += "\n\n" + "\n".join(transcripciones_extra)

                    # Filtrar imágenes reales para la preview/envío legacy
                    imagenes_reales = [f for f in imagenes_a_enviar if not isinstance(f, TempFileWrapper) or (not f.name.startswith("audio_") and not f.name.endswith(('.wav', '.mp3')))]
                    imagen_pil = Image.open(imagenes_reales[0]) if imagenes_reales else None
                    
                    # --- CÁLCULO DE TRIAJE AUTOMÁTICO (WORST CASE) ---
                    from components.triage.vital_signs_form import get_all_configs
                    from components.triage.triage_logic import calculate_worst_case
                    
                    configs = get_all_configs(st.session_state.datos_paciente.get('edad', 40))
                    triage_result = calculate_worst_case(st.session_state.datos_paciente.get('vital_signs', {}), configs)
                    
                    # Verificar Modo Contingencia
                    from services.contingency_service import is_contingency_active, save_triage_locally
                    
                    if is_contingency_active():
                        # Lógica Offline: Usar Worst Case directamente
                        st.warning("📴 MODO CONTINGENCIA: Análisis IA deshabilitado. Usando protocolo estándar.")
                        import time
                        time.sleep(1) # Simular proceso
                        
                        st.session_state.resultado = {
                            "status": "SUCCESS",
                            "nivel_sugerido": triage_result.get('final_priority', 5), # Fallback a 5 si falla
                            "razonamiento": [
                                "Modo Contingencia Activo.",
                                f"Clasificación basada en signos vitales: {triage_result.get('label')}",
                                "Protocolo de seguridad activado."
                            ]
                        }
                        
                        # Guardar localmente
                        save_triage_locally(st.session_state.datos_paciente, st.session_state.resultado)
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
                        
                        # Llamada a la IA
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
                        
                        procesar_respuesta_ia(resultado_ia)
                        st.session_state.analysis_complete = True
                        st.rerun()

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/input_form.py</div>', unsafe_allow_html=True)
