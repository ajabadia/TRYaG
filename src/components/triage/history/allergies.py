import streamlit as st
from src.db.repositories.clinical_options import get_clinical_options_repository

def render_allergies_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Alergias en un acordeón.
    """
    # Cargar opciones
    repo = get_clinical_options_repository()
    opt_alergias = repo.get_options("allergy_agent")

    with st.expander("🤧 Alergias e Intolerancias", expanded=False):
        has_allergies = st.radio("¿Tiene Alergias Conocidas?", ["No", "Sí"], horizontal=True, index=0, disabled=disabled, key=f"alg_sel_{reset_count}")
        
        alergias_str = "No conocidas"
        
        if has_allergies == "Sí":
            c1, c2 = st.columns(2)
            with c1:
                # Multiselect de agentes comunes
                selected_agents = st.multiselect(
                    "Agentes Comunes",
                    options=[opt.label for opt in opt_alergias],
                    disabled=disabled, key=f"alg_agents_{reset_count}"
                )
                other_agents = st.text_input("Otros Agentes (Especificar)", disabled=disabled, key=f"alg_other_{reset_count}")
            
            with c2:
                # Descripción de la Reacción
                reaction_details = st.text_area(
                    "¿Cuál fue la reacción? (Síntomas)",
                    placeholder="Ej: Hinchazón, dificultad respiratoria...",
                    height=68, disabled=disabled, key=f"alg_det_{reset_count}"
                )
                
                # Nivel de Riesgo
                reaction_type = st.radio(
                    "Nivel de Riesgo",
                    [
                        "Bajo Riesgo (Náuseas, cefalea, somnolencia)", 
                        "🔴 ALTO RIESGO (Disnea, Angioedema, Anafilaxia)"
                    ],
                    disabled=disabled, key=f"alg_risk_{reset_count}"
                )
                
                if "ALTO RIESGO" in reaction_type:
                    st.error("⚠️ ALERTA: RIESGO DE ANAFILAXIA - Identificar con pulsera roja")

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
