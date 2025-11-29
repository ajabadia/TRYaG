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
from components.common.audio_recorder import render_audio_recorder
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
    # --- CALLBACKS DE INTEGRACIÓN ---
    
    def on_audio_confirmed(audio_wrapper):
        if 'imagenes' not in st.session_state.datos_paciente:
            st.session_state.datos_paciente['imagenes'] = []
        st.session_state.datos_paciente['imagenes'].append(audio_wrapper)
        st.session_state.triage_input_type = "" # Resetear selector

    def on_webcam_close(photos):
        if photos:
            if 'imagenes' not in st.session_state.datos_paciente:
                st.session_state.datos_paciente['imagenes'] = []
            st.session_state.datos_paciente['imagenes'].extend(photos)
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
        
        # --- SECCIÓN 1: ENTRADA DE DATOS MULTIMODAL ---
        
        # Selector de Tipo de Entrada
        input_type = st.selectbox(
            "Seleccione método de entrada:",
            ["", "🎤 Audio", "📷 Foto / Cámara", "📁 Archivo", "🏥 Importar Expediente"],
            index=0,
            key="triage_input_type",
            label_visibility="collapsed",
            disabled=not is_editing or is_step1_disabled
        )

        # Contenedor Dinámico (Solo si hay selección)
        if input_type:
            with st.container(border=True):
                
                # 1. AUDIO (MODULARIZADO)
                if "Audio" in input_type:
                    render_audio_recorder(key_prefix="triage_audio", on_audio_ready=on_audio_confirmed, disabled=is_step1_disabled)

                # 2. FOTO / CÁMARA (MODULARIZADO)
                elif "Foto" in input_type:
                    render_webcam_manager(key_prefix="triage_cam", on_close=on_webcam_close, disabled=is_step1_disabled)

                # 3. ARCHIVO (MODULARIZADO)
                elif "Archivo" in input_type:
                    render_file_importer(key_prefix="triage_files", on_files_ready=on_files_confirmed, disabled=is_step1_disabled)

                # 4. IMPORTAR EXPEDIENTE
                elif "Importar" in input_type:
                    st.markdown("##### 🏥 Importación de Historia Clínica")
                    st.info("Simulación de conexión con HCE (Historia Clínica Electrónica).")
                    st.button("⬇️ Importar Últimos Informes", key="sim_import_btn", on_click=import_callback, disabled=is_step1_disabled)

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

        # --- EDAD (Oculto si existe) ---
        default_age = st.session_state.datos_paciente.get('edad', 40)
        # Si no hay edad en datos_paciente (ej: paciente nuevo sin seleccionar), mostrar input
        if 'edad' not in st.session_state.datos_paciente or st.session_state.datos_paciente['edad'] is None:
             st.session_state.datos_paciente['edad'] = st.number_input("Edad", 0, 120, default_age, disabled=is_step1_disabled, key=f"edad_input_{reset_count}")
        
        # --- ANTECEDENTES CLÍNICO (MODULARIZADO) ---
        render_patient_background_form(reset_count, disabled=is_step1_disabled)
        if not is_step1_disabled:
            # Pasamos la edad explícitamente para que vital_signs_form pueda cargar la config correcta
            render_vital_signs_form(age=st.session_state.datos_paciente.get('edad'))
            
            # --- ALERTAS PREDICTIVAS (NUEVO) ---
            # Solo mostrar si hay signos vitales registrados y está habilitado en config
            from src.db.repositories.general_config import get_general_config_repository
            
            # Asegurar config cargada
            if 'general_config' not in st.session_state:
                st.session_state.general_config = get_general_config_repository().get_config()
            
            enable_predictive = st.session_state.general_config.get('enable_predictive_alerts', True)

            if st.session_state.datos_paciente.get('vital_signs') and enable_predictive:
                with st.expander("🛡️ Análisis de Riesgos (Pre-Triaje)", expanded=True):
                    col_pred_btn, col_pred_res = st.columns([1, 3])
                    
                    with col_pred_btn:
                        if st.button("Verificar Riesgos", help="Analizar signos vitales con IA para detectar riesgos inminentes", key="btn_predictive_check"):
                            with st.spinner("Analizando riesgos..."):
                                from services.predictive_service import generar_alertas_predictivas
                                
                                # Preparar datos
                                antecedentes_txt = st.session_state.datos_paciente.get('antecedentes', '')
                                alergias_txt = st.session_state.datos_paciente.get('alergias_txt', '')
                                
                                pred_result, _ = generar_alertas_predictivas(
                                    edad=st.session_state.datos_paciente.get('edad'),
                                    vital_signs=st.session_state.datos_paciente.get('vital_signs'),
                                    antecedentes=antecedentes_txt,
                                    alergias=alergias_txt
                                )
                                st.session_state.predictive_result = pred_result
                    
                    with col_pred_res:
                        if 'predictive_result' in st.session_state and st.session_state.predictive_result:
                            res = st.session_state.predictive_result
                            
                            # Etiqueta de origen IA
                            st.caption("🤖 Análisis IA Generativa")
                            
                            if res.get("status") == "ERROR":
                                st.error(f"Error en análisis: {res.get('msg')}")
                            else:
                                risk = res.get("risk_level", "Low")
                                alerts = res.get("alerts", [])
                                
                                if risk == "High":
                                    st.error(f"🚨 RIESGO ALTO DETECTADO")
                                    for alert in alerts:
                                        st.markdown(f"- **{alert}**")
                                elif risk == "Medium":
                                    st.warning(f"⚠️ RIESGO MODERADO")
                                    for alert in alerts:
                                        st.markdown(f"- {alert}")
                                else:
                                    st.success("✅ Sin riesgos inminentes detectados por la IA.")
                                    if alerts:
                                        for alert in alerts:
                                            st.caption(f"- {alert}")
                                
                                # --- VALIDACIÓN HUMANA ---
                                st.divider()
                                st.markdown("**¿Es correcta esta predicción?**")
                                c_val_1, c_val_2 = st.columns(2)
                                
                                # Claves únicas para los botones
                                key_up = "pred_val_up"
                                key_down = "pred_val_down"
                                
                                if st.button("👍 Correcto", key=key_up, use_container_width=True):
                                    st.toast("Gracias por tu feedback (Positivo)", icon="✅")
                                    # Aquí se podría guardar en BD
                                    st.session_state.predictive_feedback = "positive"
                                    
                                if st.button("👎 Incorrecto", key=key_down, use_container_width=True):
                                    st.toast("Gracias por tu feedback (Negativo)", icon="📝")
                                    # Aquí se podría guardar en BD
                                    st.session_state.predictive_feedback = "negative"
                                    
                                if 'predictive_feedback' in st.session_state:
                                    if st.session_state.predictive_feedback == "positive":
                                        st.caption("✅ Validado positivamente")
                                    else:
                                        st.caption("❌ Marcado como incorrecto")

        elif 'vital_signs' in st.session_state.datos_paciente:
             st.info("Signos vitales registrados.")





        if st.session_state.datos_paciente.get('imagenes'):
            with st.container(border=True):
                c_info_icon, c_info_text = st.columns([1, 20])
                with c_info_icon:
                    render_icon("info", size=20, color="#17a2b8")
                with c_info_text:
                    st.info("Marca 'Analizar con IA' en los archivos que deseas enviar.")
                
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
                             is_audio_file = f.name.startswith("audio_") or f.name.endswith(('.wav', '.mp3', '.ogg'))
                        elif hasattr(f, 'name'):
                             is_audio_file = f.name.endswith(('.wav', '.mp3', '.ogg'))
                        
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
                    
                    # Preparar datos de alergias (Priorizar info completa)
                    alergias_info = st.session_state.datos_paciente.get('alergias_info_completa')
                    if not alergias_info:
                        # Fallback a lógica antigua
                        alergias_info = st.session_state.datos_paciente.get('alergias_selector', 'No')
                        if alergias_info != "No":
                            detalles = st.session_state.datos_paciente.get('alergias_txt', '')
                            if detalles:
                                alergias_info += f": {detalles}"
                    
                    resultado_ia, _ = llamar_modelo_gemini(
                        texto_completo, 
                        st.session_state.datos_paciente['edad'], 
                        st.session_state.datos_paciente['dolor'], 
                        vital_signs=st.session_state.datos_paciente.get('vital_signs'),
                        imagen=imagen_pil,
                        triage_result=triage_result,
                        antecedentes=st.session_state.datos_paciente.get('antecedentes'),
                        alergias=alergias_info
                    )
                    procesar_respuesta_ia(resultado_ia)
                    if st.session_state.resultado and st.session_state.resultado.get("status") != "ERROR":
                        st.session_state.analysis_complete = True
                    st.rerun()



    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/input_form.py</div>', unsafe_allow_html=True)
