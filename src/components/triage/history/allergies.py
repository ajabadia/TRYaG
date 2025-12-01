import streamlit as st
from db.repositories.clinical_options import get_clinical_options_repository

def render_allergies_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Alergias en un acordeón.
    """
    # Cargar opciones
    repo = get_clinical_options_repository()
    opt_alergias = repo.get_options("allergy_agent")
    # Sort by type: drug, food, environmental
    type_order = {'drug': 1, 'food': 2, 'environmental': 3}
    opt_alergias.sort(key=lambda x: type_order.get(x.meta.get('type', ''), 4) if x.meta else 4)

    with st.expander("🤧 Alergias e Intolerancias", expanded=False):
        has_allergies = st.radio("¿Tiene Alergias Conocidas?", ["No", "Sí"], horizontal=True, index=0, disabled=disabled, key=f"alg_sel_{reset_count}", help="Indique si el paciente refiere alergias a medicamentos, alimentos o látex")
        
        alergias_str = "No conocidas"
        
        if has_allergies == "Sí":
            c1, c2 = st.columns(2)
            with c1:
                # Multiselect de agentes comunes
                selected_agents = st.multiselect(
                    "🦠 Agentes Comunes",
                    options=[opt.label for opt in opt_alergias],
                    disabled=disabled, key=f"alg_agents_{reset_count}",
                    help="Seleccione los alérgenos comunes de la lista"
                )
                other_agents = st.text_input("📝 Otros Agentes (Especificar)", disabled=disabled, key=f"alg_other_{reset_count}", help="Escriba otros alérgenos no listados")
            
            with c2:
                # Descripción de la Reacción
                opt_symptoms = repo.get_options("allergy_symptoms")
                reaction_details = st.multiselect(
                    "⚠️ ¿Cuál fue la reacción? (Síntomas)",
                    options=[opt.label for opt in opt_symptoms],
                    default=st.session_state.datos_paciente.get('alergias_reaccion_detalles', []) if isinstance(st.session_state.datos_paciente.get('alergias_reaccion_detalles'), list) else [],
                    disabled=disabled, key=f"alg_det_{reset_count}",
                    help="Seleccione los síntomas presentados"
                )
                st.session_state.datos_paciente['alergias_reaccion_detalles'] = reaction_details
                
                # Nivel de Riesgo
                reaction_type = st.radio(
                    "🚨 Nivel de Riesgo",
                    [
                        "Bajo Riesgo (Náuseas, cefalea, somnolencia)", 
                        "🔴 ALTO RIESGO (Disnea, Angioedema, Anafilaxia)"
                    ],
                    disabled=disabled, key=f"alg_risk_{reset_count}",
                    help="Evalúe la gravedad de la reacción alérgica"
                )
                
                if "ALTO RIESGO" in reaction_type:
                    st.error("⚠️ ALERTA: RIESGO DE ANAFILAXIA - Identificar con pulsera roja")
                    
                    # Cargar opciones de riesgo alto
                    opt_risk = repo.get_options("allergy_reaction")
                    
                    st.session_state.datos_paciente['alergias_reaccion_tipo'] = st.multiselect(
                        "Tipo de Reacción Grave",
                        options=[opt.label for opt in opt_risk],
                        default=st.session_state.datos_paciente.get('alergias_reaccion_tipo', []),
                        disabled=disabled,
                        key=f"alg_risk_type_{reset_count}"
                    )
                    
                    st.session_state.datos_paciente['alergias_reaccion_otros'] = st.text_input(
                        "Otros Detalles Riesgo",
                        value=st.session_state.datos_paciente.get('alergias_reaccion_otros', ''),
                        disabled=disabled,
                        key=f"alg_risk_other_{reset_count}"
                    )

            # Construir string completo para IA
            agents_list = selected_agents + ([other_agents] if other_agents else [])
            if agents_list:
                risk_prefix = "🔴 " if "ALTO RIESGO" in reaction_type else ""
                details_str = f" ({reaction_details})" if reaction_details else ""
                alergias_str = f"{risk_prefix}{', '.join(agents_list)}{details_str}. Reacción: {reaction_type}"
            else:
                alergias_str = "Sí (Sin especificar)"
        
        # Guardar en session state para compatibilidad
        st.session_state.datos_paciente['alergias_selector'] = has_allergies
        st.session_state.datos_paciente['alergias_info_completa'] = alergias_str

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/allergies.py</div>', unsafe_allow_html=True)
