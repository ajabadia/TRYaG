import streamlit as st
from src.db.repositories.clinical_options import get_clinical_options_repository

def render_social_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Antecedentes Sociales y Funcionales en un acordeón.
    """
    # Cargar opciones
    repo = get_clinical_options_repository()
    opt_social = repo.get_options("social_habit")
    opt_living = repo.get_options("living_situation")
    opt_func = repo.get_options("functional_status")

    with st.expander("🏠 Social y Funcional", expanded=False):
        c_soc, c_func = st.columns(2)
        with c_soc:
            st.markdown("**Social**")
            # Hábitos Tóxicos (Multiselect)
            st.session_state.datos_paciente['soc_habitos'] = st.multiselect(
                "🚬 Hábitos Tóxicos",
                options=[opt.label for opt in opt_social],
                default=st.session_state.datos_paciente.get('soc_habitos', []),
                disabled=disabled, key=f"soc_hab_{reset_count}",
                help="Consumo de tabaco, alcohol u otras sustancias"
            )
            
            # Situación Convivencia (Selectbox)
            st.session_state.datos_paciente['soc_convivencia'] = st.selectbox(
                "🏘️ Situación Convivencia",
                options=[""] + [opt.label for opt in opt_living],
                index=0, disabled=disabled, key=f"soc_live_{reset_count}",
                help="¿Con quién vive el paciente?"
            )
            
        with c_func:
            st.markdown("**Funcional / Cognitivo**")
            # Estado Funcional (Selectbox)
            st.session_state.datos_paciente['soc_funcional'] = st.selectbox(
                "♿ Estado Funcional Basal",
                options=[""] + [opt.label for opt in opt_func],
                index=0, disabled=disabled, key=f"soc_func_{reset_count}",
                help="Grado de autonomía para actividades de la vida diaria"
            )
            
            # Caídas
            falls = st.checkbox(
                "⚠️ Caídas recientes (6-12 meses)",
                value=st.session_state.datos_paciente.get('soc_caidas', False),
                disabled=disabled, key=f"soc_falls_{reset_count}",
                help="Antecedentes de caídas en el último año"
            )
            st.session_state.datos_paciente['soc_caidas'] = falls
            if falls:
                st.session_state.datos_paciente['soc_caidas_det'] = st.text_input(
                    "📝 Causa / Consecuencias",
                    value=st.session_state.datos_paciente.get('soc_caidas_det', ''),
                    disabled=disabled, key=f"soc_falls_det_{reset_count}",
                    help="Motivo de la caída y si hubo lesiones"
                )

            # Cognitivo
            cognitive = st.checkbox(
                "🧠 Deterioro Cognitivo / Demencia",
                value=st.session_state.datos_paciente.get('soc_cognitivo', False),
                disabled=disabled, key=f"soc_cog_{reset_count}",
                help="Diagnóstico previo de demencia o deterioro cognitivo"
            )
            st.session_state.datos_paciente['soc_cognitivo'] = cognitive
            if cognitive:
                from src.db.repositories.clinical_options import get_clinical_options_repository
                repo = get_clinical_options_repository()
                opt_dementia = repo.get_options("dementia")
                
                st.session_state.datos_paciente['soc_cognitivo_det'] = st.multiselect(
                    "ℹ️ Tipo de Deterioro / Demencia",
                    options=[opt.label for opt in opt_dementia],
                    default=st.session_state.datos_paciente.get('soc_cognitivo_det', []) if isinstance(st.session_state.datos_paciente.get('soc_cognitivo_det'), list) else [],
                    disabled=disabled, key=f"soc_cog_det_{reset_count}",
                    help="Seleccione el diagnóstico conocido"
                )
                
                st.session_state.datos_paciente['soc_cognitivo_otros'] = st.text_input(
                    "Otros / Estadio (GDS)",
                    value=st.session_state.datos_paciente.get('soc_cognitivo_otros', ''),
                    disabled=disabled, key=f"soc_cog_other_{reset_count}"
                )

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/social_history.py</div>', unsafe_allow_html=True)
