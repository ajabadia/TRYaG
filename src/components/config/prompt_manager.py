# path: src/components/config/prompt_manager.py
# Creado: 2025-11-29
"""
Módulo unificado para la gestión de Prompts IA.
Incluye selector de tipo de prompt y editor de versiones.
"""
import streamlit as st
import json
from core.prompt_manager import PromptManager
from utils.icons import render_icon

def render_prompt_manager():
    """
    Renderiza el gestor unificado de prompts con selector principal.
    """
    st.info("Gestión centralizada de Prompts y Reglas de IA.")
    
    # --- Selector de Tipo de Prompt ---
    prompt_types = {
        "triage_gemini": {
            "title": "Gemini (IA Generativa)",
            "desc": "Define las instrucciones, rol y ejemplos (few-shot) para el modelo Gemini.",
            "icon": "robot"
        },
        "triage_sim": {
            "title": "Simulación (Reglas)",
            "desc": "Define palabras clave, reglas y umbrales para el modo de simulación (JSON).",
            "icon": "legal"
        },
        "transcription": {
            "title": "Transcripción",
            "desc": "Instrucciones para la transcripción y traducción de audio.",
            "icon": "mic"
        },
        "triage_predictive": {
            "title": "Alertas Predictivas",
            "desc": "Detecta riesgos inminentes basados en signos vitales y antecedentes (Pre-Triaje).",
            "icon": "warning"
        }
    }
    
    # Selector visual
    selected_key = st.selectbox(
        "Seleccione el componente IA a configurar:",
        options=list(prompt_types.keys()),
        format_func=lambda k: f"{prompt_types[k]['title']}"
    )
    
    # Mostrar info del seleccionado
    current_config = prompt_types[selected_key]
    st.markdown(f"### {render_icon(current_config['icon'], size=24, color='#2196F3')} {current_config['title']}")
    st.caption(current_config['desc'])
    st.divider()
    
    # Renderizar el editor para el tipo seleccionado
    _render_prompt_editor_logic(selected_key)
    
    # Footer
    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 20px;">src/components/config/prompt_manager.py</div>', unsafe_allow_html=True)


def _render_prompt_editor_logic(prompt_type):
    """
    Lógica interna del editor de prompts (migrada de prompt_editor.py).
    """
    pm = PromptManager()
    
    # Obtener versiones y activa
    versions = pm.list_versions(prompt_type)
    active_version_id = pm.get_active_version_id(prompt_type)
    
    if not versions:
        st.warning("No hay versiones disponibles para este prompt.")
        if st.button("✨ Inicializar con Prompt por Defecto", key=f"init_{prompt_type}"):
            default_content = ""
            if prompt_type == "triage_predictive":
                from services.predictive_service import DEFAULT_PREDICTIVE_PROMPT
                default_content = DEFAULT_PREDICTIVE_PROMPT
            elif prompt_type == "triage_gemini":
                default_content = "Actúa como experto en triaje..."
            
            pm.create_version(prompt_type, default_content or "Escribe aquí tu prompt...", author="system", notes="Versión inicial")
            st.rerun()
        return

    # --- Selector de Versión ---
    def sort_key(vid):
        v = versions[vid]
        score = 0
        if vid == active_version_id: score += 1000
        if v.get("status") == "draft": score += 100
        return score

    sorted_vids = sorted(versions.keys(), key=sort_key, reverse=True)
    
    version_options = {}
    for vid in sorted_vids:
        v = versions[vid]
        status_text = v.get("status", "unknown").title()
        
        created_at = v.get('created_at')
        if created_at:
            if hasattr(created_at, 'isoformat'):
                created_at_str = created_at.isoformat()[:16]
            else:
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

    # --- Estado ---
    is_active = (selected_vid == active_version_id)
    is_draft = (selected_version.get("status") == "draft")
    
    # --- Área de Edición ---
    content = selected_version.get("content", "")
    notes = selected_version.get("notes", "")
    current_model = selected_version.get("model", "gemini-2.5-flash")
    
    can_edit = is_draft
    
    with st.expander("Editor de Contenido", expanded=True):
        # Selector de Modelo (Dinámico desde BD)
        from db.repositories.ai_models import get_ai_models_repository
        models_repo = get_ai_models_repository()
        available_models = models_repo.get_available_models()
        
        # Fallback si está vacío
        if not available_models:
            available_models = ["gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro"]
            
        model_options = available_models
        if current_model not in model_options:
            model_options.append(current_model)
            
        new_model = st.selectbox(
            "Modelo IA",
            options=model_options,
            index=model_options.index(current_model) if current_model in model_options else 0,
            disabled=not can_edit,
            key=f"model_{prompt_type}_{selected_vid}"
        )

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
        
        # Auditoría
        col_audit_icon, col_audit_text = st.columns([0.5, 20])
        with col_audit_icon:
            render_icon("schedule", size=16)
        with col_audit_text:
            st.markdown("###### Auditoría de Versión")
        
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
            st.text_input("Creado por", value=f"{created_by} | {fmt_date(created_at)}", disabled=True, key=f"aud_cr_{prompt_type}_{selected_vid}")
        with audit_c2:
            st.text_input("Modificado por", value=f"{updated_by} | {fmt_date(updated_at)}", disabled=True, key=f"aud_up_{prompt_type}_{selected_vid}")

    # --- Botonera ---
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    
    with col_b1:
        if is_draft:
            if st.button("Guardar Cambios", icon=":material/save:", key=f"save_{prompt_type}", type="primary"):
                pm.update_version(prompt_type, selected_vid, new_content, model=new_model, author="admin", notes=new_notes)
                st.success("Cambios guardados.")
                st.rerun()
        else:
            if st.button("Crear Nueva Versión", icon=":material/content_copy:", key=f"clone_{prompt_type}"):
                pm.create_version(prompt_type, content, model=current_model, author="admin", notes=f"Copia de {selected_vid}")
                st.success("Nueva versión creada.")
                st.rerun()

    with col_b2:
        if is_draft:
            if st.button("Activar esta Versión", icon=":material/rocket_launch:", key=f"activate_{prompt_type}"):
                pm.set_active_version(prompt_type, selected_vid)
                st.success(f"Versión {selected_vid} activada.")
                st.rerun()
        elif is_active:
            st.success("✅ Versión Activa")

    with col_b3:
        if is_draft:
            if st.button("Deprecar (Archivar)", icon=":material/delete:", key=f"deprecate_{prompt_type}"):
                pm.deprecate_version(prompt_type, selected_vid)
                st.success("Versión archivada.")
                st.rerun()

    # --- Sección de Pruebas ---
    st.divider()
    st.subheader("🧪 Área de Pruebas")
    
    if not is_draft:
        st.info("Las pruebas solo están habilitadas para versiones en borrador (Draft).")
    else:
        test_key_base = f"test_{prompt_type}_{selected_vid}"
        if f"{test_key_base}_result" not in st.session_state:
            st.session_state[f"{test_key_base}_result"] = None
            
        test_input = st.text_area("Input de Prueba", height=100, key=f"{test_key_base}_input")
        
        if st.button("Lanzar Prueba", key=f"{test_key_base}_btn", disabled=not test_input):
            with st.spinner("Ejecutando prueba..."):
                try:
                    response = None
                    if prompt_type == "triage_gemini":
                        from services.triage_service import llamar_modelo_gemini
                        response, _ = llamar_modelo_gemini(motivo=test_input, edad=30, dolor=5, prompt_content=new_content)
                    elif prompt_type == "triage_sim":
                        from services.simulated_ia import simulacion_ia
                        response = simulacion_ia(motivo=test_input, edad=30, dolor=5, prompt_content=new_content)
                    elif prompt_type == "transcription":
                        from services.transcription_service import transcribir_audio
                        response, _ = transcribir_audio(text_input=test_input, prompt_content=new_content)
                    elif prompt_type == "triage_predictive":
                        from services.predictive_service import generar_alertas_predictivas
                        response, _ = generar_alertas_predictivas(edad=50, vital_signs={"fc": 110}, antecedentes=test_input, prompt_content=new_content)
                    
                    st.session_state[f"{test_key_base}_result"] = response
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state[f"{test_key_base}_result"]:
            st.json(st.session_state[f"{test_key_base}_result"])
