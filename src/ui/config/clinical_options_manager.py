import streamlit as st
from db.repositories.clinical_options import get_clinical_options_repository, ClinicalOption

def render_clinical_options_manager():
    """
    Renderiza el gestor de Opciones Clínicas.
    Permite crear, editar y desactivar opciones para los diferentes selectores.
    """
    st.markdown("### 📋 Gestión de Opciones Clínicas")
    st.info("Aquí puedes administrar los valores disponibles en los desplegables de los formularios de triaje.")

    repo = get_clinical_options_repository()

    # 1. Selector de Categoría
    CATEGORIES = {
        "immuno_onco": "Inmunodeprimido / Oncológico",
        "allergy_agent": "Alergias (Agentes Comunes)",
        "allergy_reaction": "Alergias (Reacciones Graves)",
        "vaccine": "Vacunas",
        "implant": "Implantes / Dispositivos",
        "dementia": "Demencia / Deterioro Cognitivo",
        "mrsa_type": "MRSA / Multirresistentes",
        "family_cardio": "Antecedentes Familiares: Cardio",
        "family_cancer": "Antecedentes Familiares: Cáncer",
        "family_diabetes": "Antecedentes Familiares: Diabetes",
        "family_genetic": "Antecedentes Familiares: Genética",
        "food_allergy": "Alergias Alimentarias",
        "animal_contact": "Contacto Animales",
        "sensory_auditory": "Déficit Auditivo",
        "sensory_visual": "Déficit Visual",
        "sensory_language": "Idioma / Intérprete",
        "sensory_prosthesis": "Prótesis",
        "forensic_violence": "Violencia (Tipos)",
        "forensic_cultural": "Consideraciones Culturales",
        "forensic_religion": "Preferencias Religiosas",
        "social_habit": "Hábitos Tóxicos",
        "living_situation": "Situación Convivencia",
        "functional_status": "Estado Funcional"
    }

    selected_cat_key = st.selectbox(
        "Selecciona la Categoría a editar",
        options=list(CATEGORIES.keys()),
        format_func=lambda x: CATEGORIES[x]
    )

    # 2. Listado de Opciones Existentes
    options = repo.get_options(selected_cat_key)
    
    st.divider()
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(f"Opciones para: {CATEGORIES[selected_cat_key]}")
    with c2:
        if st.button("➕ Nueva Opción", use_container_width=True):
            st.session_state.show_add_option_form = True

    # Mostrar tabla simple
    if not options:
        st.warning("No hay opciones configuradas para esta categoría.")
    else:
        for opt in options:
            with st.container(border=True):
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a:
                    st.markdown(f"**{opt.label}**")
                    st.caption(f"Valor interno: `{opt.value}`")
                    if opt.meta:
                        st.caption(f"Meta: {opt.meta}")
                with col_b:
                    if opt.active:
                        st.success("Activo")
                    else:
                        st.error("Inactivo")
                with col_c:
                    # Toggle Active/Inactive (Simulado por ahora, idealmente update en DB)
                    # Para simplificar, solo mostramos estado. Implementar edición requeriría más UI.
                    pass

    # 3. Formulario de Añadir (en expander o modal)
    if st.session_state.get('show_add_option_form', False):
        with st.form("add_option_form"):
            st.markdown("#### Añadir Nueva Opción")
            new_label = st.text_input("Etiqueta Visible (Label)")
            new_value = st.text_input("Valor Interno (Value - sin espacios, minúsculas)")
            
            # Campos extra según categoría
            meta_data = {}
            if selected_cat_key == "immuno_onco":
                c_meta1, c_meta2 = st.columns(2)
                with c_meta1:
                    is_imm = st.checkbox("Es Inmunodeprimido")
                with c_meta2:
                    is_onc = st.checkbox("Es Oncológico")
                meta_data = {"is_immuno": is_imm, "is_onco": is_onc}
            
            submitted = st.form_submit_button("Guardar")
            if submitted:
                if new_label and new_value:
                    # Crear objeto
                    new_opt = ClinicalOption(
                        category=selected_cat_key,
                        value=new_value,
                        label=new_label,
                        meta=meta_data if meta_data else None,
                        active=True
                    )
                    # Guardar en DB
                    repo.create(new_opt.model_dump(by_alias=True))
                    st.success("Opción guardada correctamente")
                    st.session_state.show_add_option_form = False
                    st.rerun()
                else:
                    st.error("Debe rellenar etiqueta y valor.")
            
            if st.form_submit_button("Cancelar"):
                st.session_state.show_add_option_form = False
                st.rerun()
