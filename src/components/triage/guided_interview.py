import streamlit as st
from utils.icons import render_icon
from db.repositories.clinical_options_repository import get_clinical_options_repository

def render_guided_interview(disabled: bool = False, key_suffix: str = "0"):
    """
    Renderiza una entrevista guiada inteligente con interfaz de acordeón persistente.
    Obtiene opciones dinámicamente de la base de datos.
    """
    # Inicializar diccionario de datos de entrevista si no existe
    if 'gi_responses' not in st.session_state:
        st.session_state.gi_responses = {}

    # --- INTERFAZ DE ENTREVISTA (ACORDEÓN) ---
    repo = get_clinical_options_repository()
    
    with st.expander("🗣️ Asistente de Síntomas (Entrevista Guiada)", expanded=False):
        st.caption("Despliega las secciones relevantes y rellena la información. Los datos se guardan automáticamente.")

        # --- 1. TRAUMA ---
        st.markdown("##### 🤕 Traumatismo / Golpe / Caída")
        mech_opts = repo.get_options_map("gi_trauma_mechanism")
        loc_opts = repo.get_options_map("gi_trauma_location")
        
        # Recuperar valores previos
        prev_trauma = st.session_state.gi_responses.get('trauma', {})
        
        # Usar claves únicas para persistencia automática en session_state
        mech = st.selectbox("¿Cómo ocurrió?", ["No aplica"] + list(mech_opts.values()), 
                           index=0 if not prev_trauma else (["No aplica"] + list(mech_opts.values())).index(prev_trauma.get('mechanism', "No aplica")) if prev_trauma.get('mechanism') in (["No aplica"] + list(mech_opts.values())) else 0,
                           key="gi_trauma_mech", disabled=disabled)
        
        if mech != "No aplica":
            loc_idx = 0
            if prev_trauma.get('location') in list(loc_opts.values()):
                loc_idx = list(loc_opts.values()).index(prev_trauma['location'])
                
            loc = st.selectbox("¿Dónde es la lesión principal?", list(loc_opts.values()), index=loc_idx, key="gi_trauma_loc", disabled=disabled)
            
            bleeding_opts = ["No", "Sí, leve", "Sí, abundante"]
            bleeding_idx = bleeding_opts.index(prev_trauma.get('bleeding', "No")) if prev_trauma.get('bleeding') in bleeding_opts else 0
            bleeding = st.radio("¿Hay sangrado activo?", bleeding_opts, index=bleeding_idx, horizontal=True, key="gi_trauma_bleeding", disabled=disabled)
            
            # Guardar en estado
            st.session_state.gi_responses['trauma'] = {
                "mechanism": mech,
                "location": loc,
                "bleeding": bleeding
            }
            
            # Sincronización HDA (Trauma)
            st.session_state.datos_paciente['hda_localizacion'] = loc
            # Actualizar widget key si existe
            if f"hda_loc_sel_{key_suffix}" in st.session_state:
                # Mapear valor a opciones del selectbox si es posible, sino 'Otro'
                # (Simplificación: forzamos rerun para que la lógica de hda_form maneje el default)
                del st.session_state[f"hda_loc_sel_{key_suffix}"] # Borrar estado para forzar recarga del default
            if f"hda_loc_txt_{key_suffix}" in st.session_state:
                del st.session_state[f"hda_loc_txt_{key_suffix}"]
            
        elif 'trauma' in st.session_state.gi_responses:
            del st.session_state.gi_responses['trauma']

        st.divider()
        # --- 2. DOLOR ---
        st.markdown("##### ⚡ Dolor (Sin golpe previo)")
        # Usar la misma categoría que en HDA para consistencia
        pain_opts = repo.get_options_map("pain_characteristics")
        prev_pain = st.session_state.gi_responses.get('pain', {})
        
        has_pain = st.checkbox("¿El paciente refiere dolor?", value=bool(prev_pain), key="gi_pain_check", disabled=disabled)
        
        if has_pain:
            # Mapa Corporal
            from components.common.body_map import render_body_map
            st.markdown("**¿Dónde le duele?**")
            col_map, col_inputs = st.columns([1, 1])
            
            with col_map:
                selected_part = render_body_map(key=f"body_map_{key_suffix}")

            with col_inputs:
                # Determinar ubicación actual (prioridad: selección reciente > guardada > default)
                current_location = selected_part if selected_part else prev_pain.get('location', 'No especificado')
                st.info(f"📍 Zona: **{current_location}**")
                
                # Slider
                current_pain = st.session_state.datos_paciente.get('dolor', 0)
                lvl = st.slider("Nivel (0-10)", 0, 10, current_pain, key="gi_pain_lvl", disabled=disabled)
                st.session_state.datos_paciente['dolor'] = lvl
                
                # Tipo
                type_idx = 0
                if prev_pain.get('type') in list(pain_opts.values()):
                    type_idx = list(pain_opts.values()).index(prev_pain['type'])
                type_pain = st.selectbox("Tipo de dolor", list(pain_opts.values()), index=type_idx, key="gi_pain_type_sel", disabled=disabled)
                
                # Duración
                duration = st.text_input("Desde cuándo", value=prev_pain.get('duration', ''), placeholder="Ej: 2 horas", key="gi_pain_duration", disabled=disabled)

            # Guardar todo
            st.session_state.gi_responses['pain'] = {
                "level": lvl,
                "type": type_pain,
                "duration": duration,
                "location": current_location
            }
            
            # Sincronización HDA (Dolor)
            st.session_state.datos_paciente['hda_intensidad'] = lvl
            st.session_state.datos_paciente['hda_caracteristicas'] = [type_pain]
            st.session_state.datos_paciente['hda_localizacion'] = current_location
            st.session_state.datos_paciente['hda_aparicion'] = duration
            
            # Sincronizar Widget Keys (Borrar para forzar recarga desde datos_paciente)
            keys_to_reset = [
                f"hda_int_{key_suffix}", 
                f"hda_char_{key_suffix}", 
                f"hda_loc_sel_{key_suffix}", 
                f"hda_onset_{key_suffix}"
            ]
            for k in keys_to_reset:
                if k in st.session_state: del st.session_state[k]
            
        elif 'pain' in st.session_state.gi_responses:
            del st.session_state.gi_responses['pain']

        st.divider()

        # --- 3. INFECCIÓN ---
        st.markdown("##### 🌡️ Fiebre / Infección / Malestar")
        sym_opts = repo.get_options_map("gi_infection_symptoms")
        prev_inf = st.session_state.gi_responses.get('infection', {})
        
        has_inf = st.checkbox("¿Síntomas de infección?", value=bool(prev_inf), key="gi_inf_check", disabled=disabled)
        
        if has_inf:
            fever_opts = ["No", "Sí, leve (<38)", "Sí, alta (>38)"]
            fever_idx = fever_opts.index(prev_inf.get('fever', "No")) if prev_inf.get('fever') in fever_opts else 0
            fever = st.radio("¿Tienes fiebre?", fever_opts, index=fever_idx, horizontal=True, key="gi_inf_fever", disabled=disabled)
            
            if fever != "No":
                # Input de temperatura (Propagación)
                current_temp = st.session_state.datos_paciente.get('vital_signs', {}).get('temp', 0.0)
                temp_val = st.number_input("Temperatura exacta (Opcional)", min_value=35.0, max_value=43.0, value=current_temp if current_temp > 0 else 36.5, step=0.1, format="%.1f", key="gi_inf_temp_val", disabled=disabled)
                
                if temp_val > 35.0:
                    if 'vital_signs' not in st.session_state.datos_paciente:
                        st.session_state.datos_paciente['vital_signs'] = {}
                    st.session_state.datos_paciente['vital_signs']['temp'] = temp_val
                    # Sincronizar widget key de Signos Vitales
                    st.session_state['vs_temp'] = temp_val

            symptoms = st.multiselect("Otros síntomas:", list(sym_opts.values()), default=prev_inf.get('symptoms', []), key="gi_inf_syms", disabled=disabled)
            
            st.session_state.gi_responses['infection'] = {
                "fever": fever,
                "symptoms": symptoms
            }
        elif 'infection' in st.session_state.gi_responses:
            del st.session_state.gi_responses['infection']

        st.divider()

        # --- 4. RESPIRATORIO ---
        st.markdown("##### 🫁 Respiratorio")
        prev_resp = st.session_state.gi_responses.get('respiratory', {})
        has_resp = st.checkbox("¿Dificultad respiratoria o tos?", value=bool(prev_resp), key="gi_resp_check", disabled=disabled)
        
        if has_resp:
            dys_opts = ["No", "Al esfuerzo", "En reposo"]
            dys_idx = dys_opts.index(prev_resp.get('dyspnea', "No")) if prev_resp.get('dyspnea') in dys_opts else 0
            dyspnea = st.radio("¿Siente falta de aire?", dys_opts, index=dys_idx, horizontal=True, key="gi_resp_dyspnea", disabled=disabled)
            
            cough = st.checkbox("¿Tiene tos?", value=prev_resp.get('cough', False), key="gi_resp_cough", disabled=disabled)
            
            st.session_state.gi_responses['respiratory'] = {
                "dyspnea": dyspnea,
                "cough": cough
            }
        elif 'respiratory' in st.session_state.gi_responses:
            del st.session_state.gi_responses['respiratory']

        st.divider()

        # --- 5. OTRO ---
        st.markdown("##### ❓ Otro Motivo")
        prev_other = st.session_state.gi_responses.get('other', {})
        desc = st.text_area("Describe brevemente qué te pasa:", value=prev_other.get('description', ''), key="gi_other_desc", disabled=disabled)
        if desc:
            st.session_state.gi_responses['other'] = {"description": desc}
        elif 'other' in st.session_state.gi_responses:
            del st.session_state.gi_responses['other']

        st.markdown("---")
        if st.button("✅ Actualizar Resumen", type="primary", use_container_width=True, disabled=disabled):
            _update_summary(key_suffix)

    st.markdown('<div class="debug-footer">src/components/triage/guided_interview.py</div>', unsafe_allow_html=True)

def _update_summary(key_suffix: str):
    """Genera el resumen final de todas las secciones y actualiza el campo de texto."""
    responses = st.session_state.get('gi_responses', {})
    summary_lines = []

    # Procesar Trauma
    if 'trauma' in responses:
        d = responses['trauma']
        line = f"TRAUMATISMO: {d['mechanism']} en {d['location']}."
        if d['bleeding'] != "No": line += f" Sangrado: {d['bleeding']}."
        summary_lines.append(line)

    # Procesar Dolor
    if 'pain' in responses:
        d = responses['pain']
        line = f"DOLOR: Nivel {d['level']}/10"
        if d.get('location') and d['location'] != 'No especificado':
            line += f" en {d['location'].upper()}"
        line += f", Tipo {d['type']}."
        if d['duration']: line += f" Desde: {d['duration']}."
        summary_lines.append(line)

    # Procesar Infección
    if 'infection' in responses:
        d = responses['infection']
        line = "INFECCIÓN:"
        if d['fever'] != "No": line += f" Fiebre {d['fever']}."
        if d['symptoms']: line += f" Síntomas: {', '.join(d['symptoms'])}."
        summary_lines.append(line)

    # Procesar Respiratorio
    if 'respiratory' in responses:
        d = responses['respiratory']
        line = "RESPIRATORIO:"
        if d['dyspnea'] != "No": line += f" Disnea {d['dyspnea']}."
        if d['cough']: line += " Con tos."
        summary_lines.append(line)

    # Procesar Otro
    if 'other' in responses:
        summary_lines.append(f"OTRO: {responses['other']['description']}")

    if not summary_lines:
        st.warning("No has introducido ninguna información.")
        return

    final_text = "\n".join(summary_lines)
    st.session_state.datos_paciente['guided_interview_summary'] = final_text
    
    # Concatenar al motivo de consulta existente (evitando duplicados si ya se añadió)
    current_text = st.session_state.datos_paciente.get('texto_medico', '')
    
    # Simple check para no duplicar masivamente
    if "[ENTREVISTA GUIADA]" not in current_text:
        _apply_summary_update(final_text, current_text, key_suffix, mode="append")
    else:
        # Diálogo de resolución de conflictos
        resolve_summary_conflict(final_text, current_text, key_suffix)

def _apply_summary_update(new_content, current_text, key_suffix, mode="append"):
    """Aplica la actualización del resumen al texto médico."""
    if mode == "append":
        updated_text = current_text + "\n\n[ENTREVISTA GUIADA]:\n" + new_content if current_text else "[ENTREVISTA GUIADA]:\n" + new_content
    elif mode == "overwrite":
        # Intentar reemplazar el bloque existente
        import re
        # Regex para buscar el bloque: desde [ENTREVISTA GUIADA]: hasta el final o doble salto de línea
        pattern = r"\[ENTREVISTA GUIADA\]:.*?(?=\n\n\[|$)" 
        if re.search(pattern, current_text, re.DOTALL):
            updated_text = re.sub(pattern, f"[ENTREVISTA GUIADA]:\n{new_content}", current_text, flags=re.DOTALL)
        else:
            # Fallback si no encuentra patrón exacto pero detectamos la etiqueta
            updated_text = current_text + "\n\n[ENTREVISTA GUIADA]:\n" + new_content
    
    st.session_state.datos_paciente['texto_medico'] = updated_text
    widget_key = f"texto_medico_input_{key_suffix}"
    st.session_state[widget_key] = updated_text
    st.toast("✅ Resumen actualizado.")
    st.rerun()

@st.dialog("⚠️ Actualizar Resumen", width="small")
def resolve_summary_conflict(final_text, current_text, key_suffix):
    st.warning("Ya existe un resumen de entrevista en el motivo de consulta.")
    st.markdown("¿Qué deseas hacer?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Añadir al final", use_container_width=True):
            _apply_summary_update(final_text, current_text, key_suffix, mode="append")
    with col2:
        if st.button("✏️ Sobrescribir", type="primary", use_container_width=True):
            _apply_summary_update(final_text, current_text, key_suffix, mode="overwrite")
    
    if st.button("❌ Cancelar", type="secondary", use_container_width=True):
        st.rerun()
