import streamlit as st
import pandas as pd
from src.db.repositories.clinical_options import get_clinical_options_repository
from src.db.models import ClinicalOption

def render_clinical_options_manager():
    """
    Renderiza el gestor de opciones clínicas (CRUD).
    """
    st.markdown("### 📋 Gestión de Opciones Clínicas")
    st.info("Aquí puedes administrar las listas desplegables utilizadas en el formulario de antecedentes.")
    
    repo = get_clinical_options_repository()
    
    # Categorías disponibles (Hardcoded por ahora, o podrían venir de un enum)
    categories = {
        "allergy_agent": "Alergias (Agentes)",
        "pathology": "Patologías Crónicas",
        "social_habit": "Hábitos Sociales",
        "living_situation": "Situación Convivencia",
        "functional_status": "Estado Funcional"
    }
    
    # Selector de categoría
    selected_cat_key = st.selectbox("Seleccione Categoría", list(categories.keys()), format_func=lambda x: categories[x])
    
    # Cargar opciones actuales
    options = repo.get_options(selected_cat_key)
    
    # --- TABLA DE OPCIONES ---
    if options:
        data = []
        for opt in options:
            data.append({
                "Etiqueta": opt.label,
                "Valor Interno": opt.value,
                "Riesgo": opt.risk_level or "-",
                "Activo": "✅" if opt.active else "❌",
                "_obj": opt
            })
        
        df = pd.DataFrame(data)
        st.dataframe(
            df[["Etiqueta", "Valor Interno", "Riesgo", "Activo"]], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay opciones configuradas para esta categoría.")

    st.divider()
    
    # --- FORMULARIO DE CREACIÓN / EDICIÓN ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Añadir Nueva Opción")
        with st.form(key=f"add_opt_{selected_cat_key}"):
            new_label = st.text_input("Etiqueta (Visible)")
            new_value = st.text_input("Valor Interno (snake_case)", help="Ej: penicilina_derivados")
            new_risk = st.selectbox("Nivel de Riesgo", ["", "high"], format_func=lambda x: "Alto Riesgo" if x == "high" else "Normal")
            
            if st.form_submit_button("Añadir Opción"):
                if new_label and new_value:
                    # Verificar duplicados
                    existing = repo.get_by_value(selected_cat_key, new_value)
                    if existing:
                        st.error(f"El valor '{new_value}' ya existe en esta categoría.")
                    else:
                        new_opt = ClinicalOption(
                            category=selected_cat_key,
                            value=new_value,
                            label=new_label,
                            risk_level=new_risk if new_risk else None
                        )
                        # Guardar (usando update_one con upsert como en el seed, o crear un método create en repo)
                        # Como el repo hereda de BaseRepository, podemos usar create o save.
                        # Pero BaseRepository.create espera un modelo.
                        # Vamos a usar el método genérico del repo si existe, o acceder a la colección.
                        # Mejor añadir un método 'save' al repo o usar create.
                        # Asumimos que BaseRepository tiene create.
                        try:
                            repo.create(new_opt)
                            st.success("Opción añadida correctamente.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar: {e}")
                else:
                    st.warning("Etiqueta y Valor son obligatorios.")

    with c2:
        st.markdown("#### Acciones Rápidas")
        # Aquí podríamos poner botones para borrar o desactivar seleccionando de una lista
        if options:
            opt_to_delete = st.selectbox("Seleccionar opción para eliminar/desactivar", options, format_func=lambda x: x.label)
            if st.button("🗑️ Eliminar Opción", type="primary"):
                if opt_to_delete:
                    repo.delete(opt_to_delete.id)
                    st.success("Opción eliminada.")
                    st.rerun()
