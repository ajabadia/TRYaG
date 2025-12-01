# path: src/components/triage/hda_form.py
import streamlit as st

def render_hda_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Historia de la Enfermedad Actual (HDA - ALICIA).
    """
    with st.expander("🧐 Historia de la Enfermedad Actual (HDA - ALICIA)", expanded=False):
        st.caption("Desglose estructurado del motivo de consulta.")
        c_hda1, c_hda2 = st.columns(2)
        with c_hda1:
            st.session_state.datos_paciente['hda_aparicion'] = st.text_input("⏱️ Aparición (Inicio)", value=st.session_state.datos_paciente.get('hda_aparicion', ''), disabled=disabled, key=f"hda_onset_{reset_count}", help="¿Cuándo comenzó el síntoma?")
            st.session_state.datos_paciente['hda_localizacion'] = st.text_input("📍 Localización", value=st.session_state.datos_paciente.get('hda_localizacion', ''), disabled=disabled, key=f"hda_loc_{reset_count}", help="¿Dónde se encuentra el síntoma?")
            st.session_state.datos_paciente['hda_intensidad'] = st.slider("📈 Intensidad (EVA)", min_value=1, max_value=10, value=int(st.session_state.datos_paciente.get('hda_intensidad', 5) if str(st.session_state.datos_paciente.get('hda_intensidad', '5')).isdigit() else 5), key=f"hda_int_{reset_count}", help="Escala Visual Analógica (1=Leve, 10=Insuportable)")
        with c_hda2:
            from src.db.repositories.clinical_options import get_clinical_options_repository
            repo = get_clinical_options_repository()
            opt_pain_char = repo.get_options("pain_characteristics")
            
            st.session_state.datos_paciente['hda_caracteristicas'] = st.multiselect(
                "📝 Características (Tipo dolor)",
                options=[opt.label for opt in opt_pain_char],
                default=st.session_state.datos_paciente.get('hda_caracteristicas', []) if isinstance(st.session_state.datos_paciente.get('hda_caracteristicas'), list) else [],
                disabled=disabled, key=f"hda_char_{reset_count}",
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

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/hda_form.py</div>', unsafe_allow_html=True)
