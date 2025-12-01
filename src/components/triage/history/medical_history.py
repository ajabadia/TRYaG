import streamlit as st
from db.repositories.clinical_options import get_clinical_options_repository

def render_medical_history_form(reset_count: int, disabled: bool = False):
    """
    Renderiza la sección de Antecedentes Médicos en un acordeón.
    """
    # Cargar opciones
    repo = get_clinical_options_repository()
    opt_patologias = repo.get_options("pathology")

    with st.expander("🩺 Antecedentes Médicos (Patologías)", expanded=False):
        # Multiselect de patologías comunes
        selected_pathologies = st.multiselect(
            "🦠 Patologías Crónicas Comunes",
            options=[opt.label for opt in opt_patologias],
            default=st.session_state.datos_paciente.get('ant_patologias_sel', []),
            disabled=disabled, key=f"ant_path_{reset_count}",
            help="Seleccione enfermedades crónicas diagnosticadas"
        )
        st.session_state.datos_paciente['ant_patologias_sel'] = selected_pathologies

        st.divider()
        st.session_state.datos_paciente['ant_otros_medicos'] = st.text_area(
            "📝 Detalles / Otras Patologías",
            value=st.session_state.datos_paciente.get('ant_otros_medicos', ''),
            placeholder="Ej. Hipotiroidismo, Insuficiencia Renal...",
            height=68, disabled=disabled, key=f"ant_other_med_{reset_count}",
            help="Especifique otras enfermedades no listadas arriba"
        )

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/history/medical_history.py</div>', unsafe_allow_html=True)
