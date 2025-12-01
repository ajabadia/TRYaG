import streamlit as st

def render_nutrition_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza Nutrición y Dieta en un acordeón.
    """
    with st.expander("🍎 Nutrición y Dieta", expanded=False):
        from db.repositories.clinical_options import get_clinical_options_repository
        repo = get_clinical_options_repository()

        c_nut1, c_nut2 = st.columns(2)
        with c_nut1:
            opt_diet = repo.get_options("diet_type")
            diet_labels = [""] + [opt.label for opt in opt_diet] + ["Otra"]
            
            st.session_state.datos_paciente['nut_dieta'] = st.selectbox(
                "🍽️ Tipo de Dieta Habitual",
                options=diet_labels,
                index=0,
                disabled=disabled,
                key=f"nut_diet_{reset_count}",
                help="Régimen alimenticio del paciente"
            )
            
            if st.session_state.datos_paciente['nut_dieta'] == "Otra":
                 st.session_state.datos_paciente['nut_dieta_otra'] = st.text_input("Especifique Dieta", value=st.session_state.datos_paciente.get('nut_dieta_otra', ''), key=f"nut_diet_oth_{reset_count}", disabled=disabled)
            
            has_dysphagia = st.checkbox("⚠️ Disfagia (Dificultad para tragar)", value=st.session_state.datos_paciente.get('nut_disfagia', False), disabled=disabled, key=f"nut_dys_{reset_count}", help="Riesgo de broncoaspiración")
            st.session_state.datos_paciente['nut_disfagia'] = has_dysphagia
            if has_dysphagia:
                st.session_state.datos_paciente['nut_disfagia_det'] = st.text_input("📝 Grado/Tipo Disfagia", value=st.session_state.datos_paciente.get('nut_disfagia_det', ''), key=f"nut_dys_det_{reset_count}", disabled=disabled, help="Líquidos, sólidos, mixta...")

        with c_nut2:
            has_weight_loss = st.checkbox("📉 Pérdida de peso no intencionada (>5% en 3 meses)", value=st.session_state.datos_paciente.get('nut_peso', False), disabled=disabled, key=f"nut_weight_{reset_count}", help="Signo de alarma nutricional u oncológico")
            st.session_state.datos_paciente['nut_peso'] = has_weight_loss
            if has_weight_loss:
                st.session_state.datos_paciente['nut_peso_det'] = st.text_input("⚖️ Kg perdidos / Tiempo", value=st.session_state.datos_paciente.get('nut_peso_det', ''), key=f"nut_weight_det_{reset_count}", disabled=disabled, help="Cuantificación de la pérdida")

            # Fetch all allergy agents and filter for food
            opt_agents = repo.get_options("allergy_agent")
            opt_food = [opt for opt in opt_agents if opt.meta and opt.meta.get('type') == 'food']
            
            st.session_state.datos_paciente['nut_alergias_alim'] = st.multiselect(
                "🥜 Alergias/Intolerancias Alimentarias",
                options=[opt.label for opt in opt_food],
                default=st.session_state.datos_paciente.get('nut_alergias_alim', []) if isinstance(st.session_state.datos_paciente.get('nut_alergias_alim'), list) else [],
                disabled=disabled, key=f"nut_alg_{reset_count}",
                help="Gluten, lactosa, frutos secos..."
            )
            st.session_state.datos_paciente['nut_alergias_otros'] = st.text_input("Otras Alergias Alimentarias", value=st.session_state.datos_paciente.get('nut_alergias_otros', ''), key=f"nut_alg_oth_{reset_count}", disabled=disabled)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/nutrition_history.py</div>', unsafe_allow_html=True)
