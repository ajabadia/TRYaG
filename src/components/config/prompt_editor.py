# path: src/components/config/prompt_editor.py
# Creado: 2025-11-23
# Actualizado: 2025-11-23 - Fix para datetime de MongoDB
"""
Componente de UI para editar y gestionar versiones de prompts.
"""
import streamlit as st
from src.core.prompt_manager import PromptManager
from src.utils.icons import render_icon
import json

def render_prompt_editor(prompt_type, title, help_text=""):
    """
    Renderiza el editor de prompts para un tipo específico.
    
    Args:
        prompt_type (str): Identificador del prompt (ej. 'triage_gemini').
        title (str): Título de la sección.
        help_text (str): Texto de ayuda opcional.
    """
    st.subheader(title)
    if help_text:
        st.info(help_text)

    pm = PromptManager()
    
    # Obtener versiones y activa
    versions = pm.list_versions(prompt_type)
    active_version_id = pm.get_active_version_id(prompt_type)
    
    if not versions:
        st.warning("No hay versiones disponibles para este prompt.")
        return

    # --- Selector de Versión ---
    # Ordenar versiones: Activa primero, luego drafts recientes, luego deprecadas
    def sort_key(vid):
        v = versions[vid]
        score = 0
        if vid == active_version_id: score += 1000
        if v.get("status") == "draft": score += 100
        return score

    sorted_vids = sorted(versions.keys(), key=sort_key, reverse=True)
    
    # Crear etiquetas para el selectbox
    version_options = {}
    for vid in sorted_vids:
        v = versions[vid]
        
        # Iconos de estado con SVG
        status_colors = {
            "active": "#4CAF50",
            "draft": "#FFC107",
            "deprecated": "#757575"
        }
        status_color = status_colors.get(v.get("status"), "#757575")
        status_text = v.get("status", "unknown").title()
        
        # FIX: Manejar created_at como datetime o string
        created_at = v.get('created_at')
        if created_at:
            if hasattr(created_at, 'isoformat'):
                # Es un objeto datetime de MongoDB
                created_at_str = created_at.isoformat()[:16]
            else:
                # Es un string
                created_at_str = str(created_at)[:16]
        else:
            created_at_str = "N/A"
        
        author = v.get('author', 'unknown')
        label = f"{status_text} - {vid} - {created_at_str} ({author})"
        version_options[label] = vid

    col_sel, col_actions = st.columns([3, 1])
    
    with col_sel:
        selected_label = st.selectbox(
            "Seleccionar Versión", 
            options=list(version_options.keys()),
            key=f"sel_ver_{prompt_type}"
        )
        selected_vid = version_options[selected_label]
        selected_version = versions[selected_vid]

    # --- Estado de la versión seleccionada ---
    is_active = (selected_vid == active_version_id)
    is_deprecated = (selected_version.get("status") == "deprecated")
    is_draft = (selected_version.get("status") == "draft")
    
    # --- Área de Edición ---
    content = selected_version.get("content", "")
    notes = selected_version.get("notes", "")
    
    # Solo editable si es draft
    can_edit = is_draft
    
    with st.expander("Editor de Contenido", expanded=True):
        new_content = st.text_area(
            "Contenido del Prompt", 
            value=content, 
            height=400, 
            disabled=not can_edit,
            key=f"txt_{prompt_type}_{selected_vid}"
        )
        
        new_notes = st.text_input(
            "Notas de la versión", 
            value=notes, 
            disabled=not can_edit,
            key=f"note_{prompt_type}_{selected_vid}"
        )

        st.divider()
        
        # Auditoría con iconos
        col_audit_icon, col_audit_text = st.columns([0.5, 20])
        with col_audit_icon:
            render_icon("schedule", size=16)
        with col_audit_text:
            st.markdown("###### Auditoría de Versión")
        
        # Helper para formatear fechas
        def fmt_date(d):
            if not d: return "N/A"
            if hasattr(d, 'strftime'): return d.strftime("%Y-%m-%d %H:%M:%S")
            return str(d)[:19].replace('T', ' ')

        audit_c1, audit_c2 = st.columns(2)
        
        created_at = selected_version.get('created_at')
        created_by = selected_version.get('author', 'admin')
        
        updated_at = selected_version.get('updated_at')
        updated_by = selected_version.get('updated_by', 'admin')

        with audit_c1:
            st.text_input(
                "Creado por", 
                value=f"{created_by} | {fmt_date(created_at)}", 
                disabled=True,
                key=f"aud_cr_{prompt_type}_{selected_vid}"
            )
            
        with audit_c2:
            st.text_input(
                "Modificado por", 
                value=f"{updated_by} | {fmt_date(updated_at)}", 
                disabled=True,
                key=f"aud_up_{prompt_type}_{selected_vid}"
            )

    # --- Botonera de Acciones ---
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    
    with col_b1:
        if is_draft:
            if st.button("Guardar Cambios", icon=":material/save:", key=f"save_{prompt_type}", type="primary"):
                pm.update_version(prompt_type, selected_vid, new_content, author="admin", notes=new_notes)
                st.success("Cambios guardados.")
                st.rerun()
        else:
            if st.button("Crear Nueva Versión", icon=":material/content_copy:", key=f"clone_{prompt_type}"):
                new_vid = pm.create_version(prompt_type, content, author="admin", notes=f"Copia de {selected_vid}")
                st.success(f"Nueva versión {new_vid} creada.")
                st.rerun()

    with col_b2:
        if is_draft:
            if st.button("Activar esta Versión", icon=":material/rocket_launch:", key=f"activate_{prompt_type}"):
                pm.set_active_version(prompt_type, selected_vid)
                st.success(f"Versión {selected_vid} activada.")
                st.rerun()
        elif is_active:
            col_check_icon, col_check_text = st.columns([0.3, 10])
            with col_check_icon:
                render_icon("check_circle", size=14, color="#4CAF50")
            with col_check_text:
                st.caption("Esta es la versión activa")

    with col_b3:
        if is_draft:
            if st.button("Deprecar (Archivar)", icon=":material/delete:", key=f"deprecate_{prompt_type}"):
                pm.deprecate_version(prompt_type, selected_vid)
                st.success("Versión archivada.")
                st.rerun()

    # --- Sección de Pruebas ---
    st.divider()
    
    col_test_icon, col_test_text = st.columns([0.5, 20])
    with col_test_icon:
        render_icon("science", size=20)
    with col_test_text:
        st.subheader("Área de Pruebas")
    
    can_test = is_draft
    
    if not can_test:
        col_warn_icon, col_warn_text = st.columns([0.3, 20])
        with col_warn_icon:
            render_icon("warning", size=16, color="#FFC107")
        with col_warn_text:
            st.info("Las pruebas solo están habilitadas para versiones en borrador (Draft). Para probar esta versión, cree una copia.")
    else:
        # Inicializar estado de prueba
        test_key_base = f"test_{prompt_type}_{selected_vid}"
        if f"{test_key_base}_result" not in st.session_state:
            st.session_state[f"{test_key_base}_result"] = None
        if f"{test_key_base}_locked" not in st.session_state:
            st.session_state[f"{test_key_base}_locked"] = False
            
        input_disabled = st.session_state[f"{test_key_base}_locked"]
        
        test_input = st.text_area(
            "Datos de Entrada para Prueba (Texto)",
            height=100,
            placeholder="Escriba aquí el motivo de consulta o texto a procesar...",
            disabled=input_disabled,
            key=f"{test_key_base}_input"
        )
        
        # Botón de Lanzar Prueba
        if not st.session_state[f"{test_key_base}_result"]:
            if st.button("Lanzar Prueba", icon=":material/science:", key=f"{test_key_base}_btn", disabled=not test_input or input_disabled):
                with st.spinner("Ejecutando prueba..."):
                    response = None
                    model_used = "Unknown"
                    
                    try:
                        final_prompt_used = new_content
                        
                        if prompt_type == "triage_gemini":
                            from src.services.triage_service import llamar_modelo_gemini
                            from src.config import get_model_triage
                            model_used = get_model_triage()
                            response, final_prompt_used = llamar_modelo_gemini(
                                motivo=test_input, 
                                edad=30,
                                dolor=5,
                                prompt_content=new_content
                            )
                            
                        elif prompt_type == "triage_sim":
                            from src.services.simulated_ia import simulacion_ia
                            model_used = "Simulación (Local)"
                            response = simulacion_ia(
                                motivo=test_input,
                                edad=30,
                                dolor=5,
                                prompt_content=new_content
                            )
                            final_prompt_used = new_content
                            
                        elif prompt_type == "transcription":
                            from src.services.transcription_service import transcribir_audio
                            from src.config import get_model_transcription
                            model_used = get_model_transcription()
                            response, final_prompt_used = transcribir_audio(
                                text_input=test_input,
                                prompt_content=new_content
                            )
                            
                        else:
                            response = {"status": "ERROR", "msg": "Tipo de prompt desconocido."}
                            
                    except Exception as e:
                        response = {"status": "ERROR", "msg": str(e)}
                    
                    st.session_state[f"{test_key_base}_result"] = response
                    st.session_state[f"{test_key_base}_model"] = model_used
                    st.session_state[f"{test_key_base}_final_prompt"] = final_prompt_used
                    st.session_state[f"{test_key_base}_locked"] = True
                    st.rerun()
        
        # Mostrar Resultado y Calificación
        if st.session_state[f"{test_key_base}_result"]:
            result = st.session_state[f"{test_key_base}_result"]
            
            st.markdown("### Resultado de la IA")
            st.json(result)
            
            st.info("Por favor, califique el resultado para desbloquear y realizar otra prueba.")
            
            col_like, col_dislike = st.columns(2)
            
            def submit_feedback(rating):
                final_prompt_logged = st.session_state.get(f"{test_key_base}_final_prompt", new_content)
                pm.log_test_result(
                    prompt_type=prompt_type,
                    version_id=selected_vid,
                    prompt_content=final_prompt_logged,
                    response=json.dumps(result, ensure_ascii=False),
                    model=st.session_state[f"{test_key_base}_model"],
                    rating=rating,
                    user="admin"
                )
                st.session_state[f"{test_key_base}_result"] = None
                st.session_state[f"{test_key_base}_locked"] = False
                st.success("Feedback registrado. Panel desbloqueado.")
                
            with col_like:
                if st.button("Buen Resultado", icon=":material/thumb_up:", key=f"{test_key_base}_like", use_container_width=True):
                    submit_feedback(1)
                    st.rerun()
                    
            with col_dislike:
                if st.button("Mal Resultado", icon=":material/thumb_down:", key=f"{test_key_base}_dislike", use_container_width=True):
                    submit_feedback(0)
                    st.rerun()
