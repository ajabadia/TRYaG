# path: src/components/triage/patient_background_form.py
import streamlit as st
from src.db.repositories.clinical_options import get_clinical_options_repository

def render_patient_background_form(reset_count: int, disabled: bool = False):
    """
    Renderiza el formulario de antecedentes clínicos (Alergias, Farmacología, etc.).
    
    Args:
        reset_count: Contador para forzar el reset de los widgets si es necesario.
        disabled: Si el formulario debe estar deshabilitado.
    """
    st.subheader("Antecedentes Clínicos")
    
    # Cargar opciones desde BD
    repo = get_clinical_options_repository()
    opt_alergias = repo.get_options("allergy_agent")
    opt_patologias = repo.get_options("pathology")
    opt_social = repo.get_options("social_habit")
    opt_living = repo.get_options("living_situation")
    opt_func = repo.get_options("functional_status")
    
    # Pestañas para organizar la información
    tabs = st.tabs(["Alergias", "Farmacología", "Médicos", "Quirúrgicos", "Gineco-Obs", "Social/Funcional"])
    
    # --- 1. ALERGIAS ---
    with tabs[0]:
        has_allergies = st.radio("¿Tiene Alergias Conocidas?", ["No", "Sí"], horizontal=True, key=f"has_allergies_{reset_count}", disabled=disabled)
        
        alergias_str = "No conocidas"
        if has_allergies == "Sí":
            # Multiselect de agentes comunes
            selected_agents = st.multiselect(
                "Agentes Comunes",
                options=[opt.label for opt in opt_alergias],
                key=f"allergy_agents_{reset_count}",
                disabled=disabled
            )
            
            # Otros agentes (texto libre)
            other_agents = st.text_input("Otros Agentes (Especificar)", key=f"allergy_other_{reset_count}", disabled=disabled)
            
            # Descripción de la Reacción (Síntomas)
            reaction_details = st.text_area(
                "¿Cuál fue la reacción? (Síntomas)",
                placeholder="Ej: Hinchazón, dificultad respiratoria, náuseas...",
                height=68,
                key=f"allergy_details_{reset_count}",
                disabled=disabled
            )
            
            # Tipo de Reacción (con ejemplos detallados)
            reaction_type = st.radio(
                "Nivel de Riesgo",
                [
                    "Bajo Riesgo (Náuseas, cefalea, somnolencia, efectos secundarios)", 
                    "🔴 ALTO RIESGO (Disnea, Angioedema, Anafilaxia, Hipotensión)"
                ],
                key=f"allergy_reaction_{reset_count}",
                disabled=disabled
            )
            
            if "ALTO RIESGO" in reaction_type:
                st.error("⚠️ ALERTA: RIESGO DE ANAFILAXIA - Identificar con pulsera roja")
            
            # Construir string de alergias
            agents_list = selected_agents + ([other_agents] if other_agents else [])
            if agents_list:
                risk_prefix = "🔴 " if "ALTO RIESGO" in reaction_type else ""
                details_str = f" ({reaction_details})" if reaction_details else ""
                alergias_str = f"{risk_prefix}{', '.join(agents_list)}{details_str}. Reacción: {reaction_type}"
            else:
                alergias_str = "Sí (Sin especificar)"
        
        st.session_state.datos_paciente['alergias_selector'] = has_allergies # Compatibilidad
        st.session_state.datos_paciente['alergias_txt'] = alergias_str # Compatibilidad
        st.session_state.datos_paciente['alergias_info_completa'] = alergias_str # Guardamos el string formateado
    
    # --- 2. FARMACOLOGÍA ---
    with tabs[1]:
        meds_current = st.text_area("Medicación Actual (Nombre, Dosis, Horario)", height=100, placeholder="Ej: Enalapril 20mg 1-0-0...", key=f"meds_current_{reset_count}", disabled=disabled)
        
        c_anti, c_vac = st.columns(2)
        with c_anti:
            takes_anticoagulants = st.checkbox("🔴 Toma Anticoagulantes / Antiagregantes", key=f"anticoag_{reset_count}", disabled=disabled)
            anticoag_details = ""
            if takes_anticoagulants:
                st.warning("⚠️ Riesgo de Sangrado")
                anticoag_details = st.text_input("¿Cuál/es?", key=f"anticoag_det_{reset_count}", disabled=disabled)

        with c_vac:
            vaccines_ok = st.checkbox("Vacunación al día (Tétanos/Gripe/COVID)", key=f"vaccines_{reset_count}", disabled=disabled)
            vaccines_details = ""
            if vaccines_ok:
                vaccines_details = st.text_input("Detalles (Opcional)", key=f"vaccines_det_{reset_count}", disabled=disabled)
    
    # --- 3. MÉDICOS (CRÓNICOS) ---
    with tabs[2]:
        selected_pathologies = st.multiselect(
            "Patologías Crónicas Comunes",
            options=[opt.label for opt in opt_patologias],
            key=f"pathologies_{reset_count}",
            disabled=disabled
        )
        other_pathologies = st.text_area("Detalles / Otras Patologías", height=68, key=f"pathologies_other_{reset_count}", disabled=disabled)
        
    # --- 4. QUIRÚRGICOS ---
    with tabs[3]:
        surgeries = st.text_area("Cirugías Previas (Tipo y Año)", height=68, placeholder="Ej: Apendicectomía (2010)...", key=f"surgeries_{reset_count}", disabled=disabled)
        
        anesthesia_comp = st.checkbox("Complicaciones Anestésicas Previas", key=f"anesthesia_{reset_count}", disabled=disabled)
        anesthesia_details = ""
        if anesthesia_comp:
            anesthesia_details = st.text_input("¿Qué complicaciones?", key=f"anesthesia_det_{reset_count}", disabled=disabled)

        implants = st.checkbox("Portador de Implantes / Dispositivos (Marcapasos, etc.)", key=f"implants_{reset_count}", disabled=disabled)
        implants_details = ""
        if implants:
            implants_details = st.text_input("¿Qué dispositivo?", key=f"implants_det_{reset_count}", disabled=disabled)
        
    # --- 5. GINECO-OBSTÉTRICOS ---
    with tabs[4]:
        # Solo mostrar si no es masculino (asumiendo que gender está o se puede inferir, por ahora mostramos a todos o preguntamos)
        fur = st.date_input("Fecha Última Regla (FUR)", value=None, key=f"fur_{reset_count}", disabled=disabled)
        
        possible_pregnancy = st.checkbox("Posible Embarazo", key=f"pregnancy_{reset_count}", disabled=disabled)
        pregnancy_details = ""
        if possible_pregnancy:
            pregnancy_details = st.text_input("Semanas / Detalles", key=f"pregnancy_det_{reset_count}", disabled=disabled)
        
    # --- 6. SOCIAL / FUNCIONAL ---
    with tabs[5]:
        c_soc, c_func = st.columns(2)
        with c_soc:
            st.markdown("**Social**")
            habits = st.multiselect("Hábitos Tóxicos", options=[opt.label for opt in opt_social], key=f"habits_{reset_count}", disabled=disabled)
            living = st.selectbox("Situación Convivencia", options=[""] + [opt.label for opt in opt_living], key=f"living_{reset_count}", disabled=disabled)
            
        with c_func:
            st.markdown("**Funcional / Cognitivo**")
            func_status = st.selectbox("Estado Funcional Basal", options=[""] + [opt.label for opt in opt_func], key=f"func_{reset_count}", disabled=disabled)
            
            falls = st.checkbox("Caídas recientes (6-12 meses)", key=f"falls_{reset_count}", disabled=disabled)
            falls_details = ""
            if falls:
                falls_details = st.text_input("Causa / Consecuencias", key=f"falls_det_{reset_count}", disabled=disabled)

            cognitive = st.checkbox("Deterioro Cognitivo / Demencia", key=f"cog_{reset_count}", disabled=disabled)
            cognitive_details = ""
            if cognitive:
                cognitive_details = st.text_input("Grado / Tipo", key=f"cog_det_{reset_count}", disabled=disabled)
            
        st.divider()
        st.markdown("**Otros**")
        
        transfusions = st.checkbox("Transfusiones Previas", key=f"transf_{reset_count}", disabled=disabled)
        transfusions_details = ""
        if transfusions:
            transfusions_details = st.text_input("Fecha / Reacción", key=f"transf_det_{reset_count}", disabled=disabled)

        mrsa = st.checkbox("Historial MRSA / Multirresistentes", key=f"mrsa_{reset_count}", disabled=disabled)
        mrsa_details = ""
        if mrsa:
            mrsa_details = st.text_input("Microorganismo / Ubicación", key=f"mrsa_det_{reset_count}", disabled=disabled)

        dnr = st.checkbox("Voluntades Anticipadas / DNR", key=f"dnr_{reset_count}", disabled=disabled)
        dnr_details = ""
        if dnr:
            st.error("⚠️ ORDEN DE NO REANIMACIÓN")
            dnr_details = st.text_input("Detalles / Documento", key=f"dnr_det_{reset_count}", disabled=disabled)

    # --- AGREGACIÓN DE DATOS ---
    # Construimos un texto consolidado para 'antecedentes' que se pasará a la IA
    background_parts = []
    
    if selected_pathologies: background_parts.append(f"Patologías: {', '.join(selected_pathologies)}")
    if other_pathologies: background_parts.append(f"Otros Médicos: {other_pathologies}")
    if meds_current: background_parts.append(f"Medicación: {meds_current}")
    
    if takes_anticoagulants: 
        background_parts.append(f"🔴 ANTICOAGULADO: {anticoag_details}")
    if vaccines_ok:
        background_parts.append(f"Vacunación al día: {vaccines_details}")
        
    if surgeries: background_parts.append(f"Quirúrgicos: {surgeries}")
    
    if anesthesia_comp:
        background_parts.append(f"Complicaciones Anestesia: {anesthesia_details}")
    if implants:
        background_parts.append(f"Implantes: {implants_details}")
        
    if possible_pregnancy: 
        background_parts.append(f"Posible Embarazo: {pregnancy_details}")
        
    if habits: background_parts.append(f"Hábitos: {', '.join(habits)}")
    if living: background_parts.append(f"Social: {living}")
    if func_status: background_parts.append(f"Funcional: {func_status}")
    
    if falls: 
        background_parts.append(f"Caídas Recientes: {falls_details}")
    if cognitive: 
        background_parts.append(f"Cognitivo: {cognitive_details}")
        
    if transfusions:
        background_parts.append(f"Transfusiones: {transfusions_details}")
    if mrsa: 
        background_parts.append(f"Aislamiento (MRSA/Multi): {mrsa_details}")
    if dnr: 
        background_parts.append(f"⚠️ DNR (No Reanimar): {dnr_details}")
    
    full_background = "\n".join(background_parts)
    st.session_state.datos_paciente['antecedentes'] = full_background
    
    # --- RESUMEN PLEGABLE (VISTA PREVIA IA) ---
    with st.expander("📄 Resumen Antecedentes (Vista Previa IA)", expanded=False):
        if full_background or alergias_str:
            st.markdown("**Alergias:**")
            st.info(alergias_str)
            st.markdown("**Antecedentes:**")
            st.code(full_background if full_background else "Sin antecedentes registrados", language="text")
        else:
            st.caption("No hay datos registrados.")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/patient_background_form.py</div>', unsafe_allow_html=True)
