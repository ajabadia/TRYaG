# path: src/components/triage/hda_form.py
import streamlit as st

def render_hda_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Historia de la Enfermedad Actual (HDA - ALICIA).
    """
    with st.expander("🧐 Historia de la Enfermedad Actual (HDA - ALICIA)", expanded=False):
        st.caption("Desglose estructurado del motivo de consulta.")
        
        # --- LOGICA DE SINCRONIZACIÓN ---
        # Verificar si hay datos de la entrevista guiada para pre-rellenar y bloquear
        gi_responses = st.session_state.get('gi_responses', {})
        
        # 1. Localización (Trauma o Dolor)
        gi_loc = None
        if 'trauma' in gi_responses and gi_responses['trauma'].get('location'):
            gi_loc = gi_responses['trauma']['location']
        elif 'pain' in gi_responses and gi_responses['pain'].get('location'):
            gi_loc = gi_responses['pain']['location']
            
        # 2. Intensidad (Dolor)
        gi_int = None
        if 'pain' in gi_responses and gi_responses['pain'].get('level') is not None:
            gi_int = gi_responses['pain']['level']
            
        # 3. Características (Dolor)
        gi_char = None
        if 'pain' in gi_responses and gi_responses['pain'].get('type'):
            gi_char = [gi_responses['pain']['type']] # Convertir a lista para multiselect
            
        # --- RENDERIZADO ---
        c_hda1, c_hda2 = st.columns(2)
        with c_hda1:
            st.session_state.datos_paciente['hda_aparicion'] = st.text_input("⏱️ Aparición (Inicio)", value=st.session_state.datos_paciente.get('hda_aparicion', ''), disabled=disabled, key=f"hda_onset_{reset_count}", help="¿Cuándo comenzó el síntoma?")
            
            # Localización: Selector + Texto (Sincronizado)
            from db.repositories.clinical_options_repository import get_clinical_options_repository
            repo = get_clinical_options_repository()
            loc_opts = list(repo.get_options_map("gi_trauma_location").values())
            
            # Determinar valor actual
            current_loc = st.session_state.datos_paciente.get('hda_localizacion', '')
            if gi_loc: current_loc = gi_loc # Prioridad a GI
            
            # Intentar mapear a selector
            loc_idx = 0
            if current_loc in loc_opts:
                loc_idx = loc_opts.index(current_loc)
                
            # Si viene de GI, deshabilitamos
            is_loc_disabled = disabled or (gi_loc is not None)
            
            sel_loc = st.selectbox(
                "📍 Localización (¿Dónde le duele?)", 
                ["Otro/No especificado"] + loc_opts, 
                index=loc_idx + 1 if current_loc in loc_opts else 0,
                disabled=is_loc_disabled,
                key=f"hda_loc_sel_{reset_count}"
            )
            
            if sel_loc == "Otro/No especificado":
                st.session_state.datos_paciente['hda_localizacion'] = st.text_input("Especificar Localización", value=current_loc if current_loc not in loc_opts else "", disabled=is_loc_disabled, key=f"hda_loc_txt_{reset_count}")
            else:
                st.session_state.datos_paciente['hda_localizacion'] = sel_loc

            # Intensidad
            int_val = int(st.session_state.datos_paciente.get('hda_intensidad', 5) if str(st.session_state.datos_paciente.get('hda_intensidad', '5')).isdigit() else 5)
            if gi_int is not None: int_val = int(gi_int)
            
            is_int_disabled = disabled or (gi_int is not None)
            
            st.session_state.datos_paciente['hda_intensidad'] = st.slider(
                "📈 Intensidad (EVA - Nivel 1-10)", 
                min_value=1, max_value=10, 
                value=int_val, 
                disabled=is_int_disabled,
                key=f"hda_int_{reset_count}", 
                help="Escala Visual Analógica (1=Leve, 10=Insuportable)"
            )
            
        with c_hda2:
            opt_pain_char = repo.get_options_by_category("pain_characteristics")
            
            # Características
            current_char = st.session_state.datos_paciente.get('hda_caracteristicas', [])
            if not isinstance(current_char, list): current_char = []
            if gi_char: current_char = gi_char
            
            is_char_disabled = disabled or (gi_char is not None)
            
            st.session_state.datos_paciente['hda_caracteristicas'] = st.multiselect(
                "📝 Características (tipo de dolor)",
                options=[opt['label'] for opt in opt_pain_char],
                default=current_char,
                disabled=is_char_disabled, 
                key=f"hda_char_{reset_count}",
                help="¿Cómo es el dolor? (Punzante, opresivo, quemante...)"
            )
            
            st.session_state.datos_paciente['hda_irradiacion'] = st.text_input("↗️ Irradiación", value=st.session_state.datos_paciente.get('hda_irradiacion', ''), disabled=disabled, key=f"hda_rad_{reset_count}", help="¿Se mueve el dolor a otra zona?")
            st.session_state.datos_paciente['hda_alivio'] = st.text_input("💊 Alivio/Agravantes", value=st.session_state.datos_paciente.get('hda_alivio', ''), disabled=disabled, key=f"hda_agg_{reset_count}", help="¿Qué lo mejora o empeora?")
        
        st.divider()
        c_hda3, c_hda4 = st.columns(2)
        with c_hda3:
            st.session_state.datos_paciente['hda_sintomas_asoc'] = st.text_area("➕ Síntomas Acompañantes", value=st.session_state.datos_paciente.get('hda_sintomas_asoc', ''), height=68, placeholder="Fiebre, náuseas...", disabled=disabled, key=f"hda_assoc_{reset_count}", help="Otros síntomas que acompañan al principal")
        with c_hda4:
            st.session_state.datos_paciente['hda_tratamiento_casa'] = st.text_area("🏠 Tratamiento Domiciliario", value=st.session_state.datos_paciente.get('hda_tratamiento_casa', ''), height=68, placeholder="Qué tomó antes de venir...", disabled=disabled, key=f"hda_home_tx_{reset_count}", help="Medicamentos o medidas tomadas en casa")

    st.markdown('<div class="debug-footer">src/components/triage/hda_form.py</div>', unsafe_allow_html=True)
