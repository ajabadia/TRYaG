"""
Componente modular para visualizar tarjetas de archivos multimedia (Audio, Imagen, etc.).
Permite la visualización, reproducción, transcripción y gestión de archivos adjuntos.
"""
import streamlit as st
import os
from utils.icons import render_icon
from utils.file_handler import TempFileWrapper, calculate_md5
from core.transcription_handler import get_transcription, save_transcription
from services.transcription_service import transcribir_audio

def render_media_card(file_obj, index):
    """
    Renderiza una tarjeta para un archivo multimedia específico.
    Detecta el tipo de archivo y delega en el renderizador específico.
    
    Args:
        file_obj: Objeto del archivo (UploadedFile, TempFileWrapper, etc.)
        index (int): Índice del archivo en la lista (para claves únicas).
    """
    # Calcular MD5 único para el archivo
    file_md5 = calculate_md5(file_obj)
    
    # Contenedor principal de la card con borde
    with st.container(border=True):
        # 1. Determinar tipo y renderizar contenido específico
        is_audio = _is_audio_file(file_obj)
        
        if is_audio:
            _render_audio_card(file_obj, index, file_md5)
        else:
            _render_image_card(file_obj, index, file_md5)
            
        # 2. Renderizar Footer Genérico (Checkbox Analizar y Botón Borrar)
        _render_card_footer(file_obj, index, file_md5, is_audio)

def _is_audio_file(file_obj):
    """Determina si el archivo es de audio."""
    # Duck typing para evitar problemas de importación cruzada
    if hasattr(file_obj, 'name'):
        return file_obj.name.startswith("audio_") or file_obj.name.endswith(('.wav', '.mp3', '.ogg'))
    return False

def _get_file_content(file_obj):
    """
    Extrae el contenido seguro (bytes o path) de un objeto de archivo.
    Maneja TempFileWrapper, UploadedFile y paths.
    """
    # 1. Si es path string
    if isinstance(file_obj, str):
        return file_obj
        
    # 2. Si es TempFileWrapper (por tipo o duck typing)

    if hasattr(file_obj, 'temp_path') and file_obj.temp_path:
        # Verificar si existe realmente en disco
        if os.path.exists(file_obj.temp_path):
            return os.path.abspath(file_obj.temp_path)
        # Si no existe (borrado o error), intentamos usar el objeto en memoria si es wrapper
        if hasattr(file_obj, 'file_obj'):
            return file_obj.file_obj
        
    # 3. Si tiene método read (UploadedFile, BytesIO, o Wrapper sin temp_path)
    if hasattr(file_obj, 'read'):
        try:
            # Intentar guardar posición si existe tell
            pos = 0
            if hasattr(file_obj, 'tell'):
                try:
                    pos = file_obj.tell()
                except:
                    pass
            
            file_obj.seek(0)
            content = file_obj.read()
            
            # Intentar restaurar
            try:
                file_obj.seek(pos)
            except:
                pass
                
            return content
        except Exception as e:
            print(f"Error leyendo archivo: {e}")
            # Si falla lectura, devolver None para evitar pasar wrapper a streamlit
            return None
            
    return None

def render_media_card(file_obj, index):
    """
    Renderiza una tarjeta para un archivo multimedia específico.
    Detecta el tipo de archivo y delega en el renderizador específico.
    """
    # Calcular MD5 único para el archivo
    file_md5 = calculate_md5(file_obj)
    
    # Contenedor principal de la card con borde
    with st.container(border=True):
        # 1. Determinar tipo
        file_name = file_obj.name.lower() if hasattr(file_obj, 'name') else ""
        
        if file_name.endswith(('.wav', '.mp3', '.ogg')) or file_name.startswith("audio_"):
            _render_audio_card(file_obj, index, file_md5)
        elif file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            _render_image_card(file_obj, index, file_md5)
        elif file_name.endswith(('.mp4', '.mov', '.avi', '.mkv')):
            _render_video_card(file_obj, index, file_md5)
        elif file_name.endswith(('.pdf')):
            _render_pdf_card(file_obj, index, file_md5)
        else:
            # Fallback genérico
            st.markdown(f"📄 **{file_obj.name}**")
            st.caption("Archivo genérico")
            
        # 2. Renderizar Footer Genérico (Checkbox Analizar y Botón Borrar)
        # Solo audio y video suelen ser analizables por IA de forma especial (transcripción)
        # Imágenes también, pero la lógica actual de 'is_audio' controlaba transcripción.
        # Ajustaremos para que 'is_audio' signifique 'tiene transcripción'.
        is_transcribable = file_name.endswith(('.wav', '.mp3', '.ogg', '.mp4', '.mov', '.avi')) or file_name.startswith("audio_")
        _render_card_footer(file_obj, index, file_md5, is_transcribable)

def _render_audio_card(file_obj, index, file_md5):
    """Renderiza tarjeta de Audio."""
    transcription = get_transcription(file_md5)
    audio_source = _get_file_content(file_obj)
    
    if audio_source is None:
        st.error("Error cargando audio")
        return

    st.audio(audio_source, format='audio/wav')
    
    c_icon, c_name = st.columns([0.15, 0.85])
    with c_icon: render_icon("mic", size=16)
    with c_name: st.caption(file_obj.name)
        
    if transcription:
        _render_transcription_details(transcription, index, file_md5)
    else:
        _render_transcription_actions(file_obj, index, file_md5)

def _render_video_card(file_obj, index, file_md5):
    """Renderiza tarjeta de Video."""
    transcription = get_transcription(file_md5)
    video_source = _get_file_content(file_obj)
    
    if video_source is None:
        st.error("Error cargando video")
        return

    st.video(video_source)
    
    c_icon, c_name = st.columns([0.15, 0.85])
    with c_icon: render_icon("videocam", size=16)
    with c_name: st.caption(file_obj.name)
    
    # Videos también pueden tener transcripción
    if transcription:
        _render_transcription_details(transcription, index, file_md5)
    else:
        _render_transcription_actions(file_obj, index, file_md5)

def _render_image_card(file_obj, index, file_md5):
    """Renderiza tarjeta de Imagen."""
    img_source = _get_file_content(file_obj)
    if img_source is None:
        st.error("Error cargando imagen")
        return
        
    st.image(img_source, use_container_width=True)
    st.caption(file_obj.name)

def _render_pdf_card(file_obj, index, file_md5):
    """Renderiza tarjeta de PDF (Preview simple)."""
    # Para PDF, streamlit no tiene visor nativo embebido simple sin iframe/base64 hack.
    # Mostraremos un icono grande y nombre.
    c1, c2 = st.columns([1, 3])
    with c1:
        render_icon("description", size=40, color="#e74c3c") # Rojo PDF
    with c2:
        st.markdown(f"**{file_obj.name}**")
        st.caption("Documento PDF")
    
    # Podríamos intentar mostrar primera página como imagen si tuviéramos pdf2image, 
    # pero por ahora mantenemos simple.

def _render_transcription_details(transcription, index, file_md5):
    """Muestra los detalles de una transcripción existente y permite edición."""
    source = transcription.get('source', 'AI')
    
    source_config = {
        'AI': ("IA", "robot"),
        'MANUAL': ("Manual", "person"),
        'AI_MODIFIED': ("IA (Editado)", "edit"),
        'AI_ERROR': ("Error IA", "warning")
    }
    label, icon = source_config.get(source, (source, "info"))
    
    c_src, c_info = st.columns([0.15, 0.85])
    with c_src: render_icon(icon, size=14)
    with c_info: st.caption(f"Fuente: {label} | Idioma: {transcription.get('language_name', 'Unknown')}")

    relevance = transcription.get('relevance')
    prosody = transcription.get('emotional_prosody')
    
    if relevance is not None:
        color = "red" if relevance == 0 else "green" if relevance >= 7 else "orange"
        st.caption(f"Relevancia: :{color}[{relevance}/9]")
        if relevance == 0: st.caption(":red[⚠️ Irrelevante (No seleccionable)]")

    if prosody:
        c_p_icon, c_p_text = st.columns([0.15, 0.85])
        with c_p_icon: render_icon("record_voice", size=14)
        with c_p_text: st.caption(prosody)

    if source == 'AI_ERROR':
        st.error(f"Error: {transcription.get('error_msg', 'Desconocido')}")

    current_text = transcription.get('spanish_user_text', '')
    if not current_text:
        current_text = transcription.get('translated_text', transcription.get('translated_ia_text', transcription.get('spanish_text', '')))

    edit_key = f"edit_text_{index}_{file_md5}"
    new_text = st.text_area("Texto:", value=current_text, height=100, key=edit_key)
    
    if st.button("Guardar Cambios", key=f"save_{index}_{file_md5}", use_container_width=True):
        if new_text.strip():
            new_source = 'AI_MODIFIED' if source in ['AI', 'AI_MODIFIED', 'AI_ERROR'] else 'MANUAL'
            save_transcription(file_md5, transcription, source=new_source, spanish_user_text=new_text)
            st.success("Guardado")
            st.rerun()
        else:
            st.warning("El texto no puede estar vacío")

    if transcription.get('original_text'):
        with st.expander("Ver original"):
            st.markdown(f"_{transcription.get('original_text')}_")

def _render_transcription_actions(file_obj, index, file_md5):
    """Muestra las acciones disponibles cuando no hay transcripción (IA vs Manual)."""
    mode_key = f"mode_{index}_{file_md5}"
    mode = st.radio("Modo:", ["IA", "Manual"], horizontal=True, key=mode_key, label_visibility="collapsed")
    
    if mode == "IA":
        if st.button("Transcribir con IA", key=f"btn_ai_{index}_{file_md5}", use_container_width=True):
            with st.spinner("Transcribiendo..."):
                result, _ = transcribir_audio(file_obj)
                if result.get("status") != "ERROR":
                    save_transcription(file_md5, result, source="AI")
                    st.rerun()
                else:
                    err_data = {"original_text": "", "language_code": "error", "translated_text": ""}
                    save_transcription(file_md5, err_data, source="AI_ERROR", error_msg=result.get('msg'))
                    st.rerun()
    else:
        man_text = st.text_area("Texto manual:", key=f"man_txt_{index}_{file_md5}")
        man_rel = st.number_input("Relevancia (0-9):", 0, 9, 5, key=f"man_rel_{index}_{file_md5}")
        
        if st.button("Guardar Manual", key=f"btn_man_{index}_{file_md5}", use_container_width=True):
            if man_text.strip():
                data = {
                    "original_text": man_text,
                    "translated_text": man_text,
                    "language_code": "es",
                    "language_name": "Manual",
                    "relevance": man_rel,
                    "emotional_prosody": "Manual"
                }
                save_transcription(file_md5, data, source="MANUAL", spanish_user_text=man_text)
                st.rerun()

def _render_card_footer(file_obj, index, file_md5, is_transcribable):
    """
    Renderiza el pie de la tarjeta con:
    - Checkbox 'Analizar' (si aplica)
    - Botón de borrado
    """
    c_check, c_del = st.columns([0.7, 0.3])
    
    with c_check:
        can_analyze = True
        if is_transcribable:
            # Solo analizar si hay transcripción válida y relevante
            trans = get_transcription(file_md5)
            if not trans:
                can_analyze = False
            elif trans.get('relevance') == 0:
                can_analyze = False
        
        is_selected = st.session_state.modal_image_selection.get(file_obj.name, False)
        
        if not can_analyze and is_selected:
            st.session_state.modal_image_selection[file_obj.name] = False
            is_selected = False
            
        new_val = st.checkbox(
            "Analizar",
            value=is_selected,
            disabled=not can_analyze,
            key=f"chk_{index}_{file_md5}"
        )
        
        if new_val != is_selected:
            st.session_state.modal_image_selection[file_obj.name] = new_val

    with c_del:
        if st.button("🗑️", key=f"del_{index}_{file_md5}"):
            if 'deleted_filenames' not in st.session_state:
                st.session_state.deleted_filenames = set()
            st.session_state.deleted_filenames.add(file_obj.name)
            st.rerun()
    
    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/media_cards.py</div>', unsafe_allow_html=True)
