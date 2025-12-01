import streamlit as st
import pandas as pd
from db.repositories.insurers import get_insurers_repository

def render_insurers_manager():
    """
    Renderiza el gestor de Aseguradoras y Mutuas.
    Permite listar, crear, editar y eliminar.
    """
    st.markdown("### 🏥 Gestión de Aseguradoras y Mutuas")
    
    repo = get_insurers_repository()
    
    # Inicializar seed si es necesario (solo para demo)
    if st.button("🔄 Recargar / Inicializar Datos por Defecto", key="btn_seed_insurers"):
        repo.seed_defaults()
        st.rerun()

    # --- LISTADO ---
    insurers = repo.get_all()
    
    if not insurers:
        st.info("No hay aseguradoras registradas.")
    else:
        # Convertir a DataFrame para visualización rápida
        df_data = []
        for i in insurers:
            df_data.append({
                "ID": str(i.get('_id')),
                "Nombre": i.get('name'),
                "Activa": "✅" if i.get('active') else "❌",
                "Admitida": "✅" if i.get('is_admitted') else "❌",
                "Aseguradora": "✅" if i.get('is_insurer') else "",
                "Mutua": "✅" if i.get('is_mutual') else "",
                "Logo": "🖼️" if i.get('logo_url') else ""
            })
        
        st.dataframe(
            pd.DataFrame(df_data),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Logo": st.column_config.TextColumn("Logo", help="Tiene logo configurado")
            }
        )

    st.divider()
    
    # --- FORMULARIO DE EDICIÓN / CREACIÓN ---
    col_list, col_form = st.columns([1, 2])
    
    with col_list:
        st.markdown("#### ✏️ Editar / Crear")
        
        # Selector para editar
        options = ["➕ Crear Nueva"] + [f"{i['name']}" for i in insurers]
        selected_option = st.selectbox("Seleccionar Aseguradora", options)
        
        selected_insurer = None
        if selected_option != "➕ Crear Nueva":
            # Buscar el objeto seleccionado
            selected_insurer = next((i for i in insurers if i['name'] == selected_option), None)

    with col_form:
        with st.form("insurer_form"):
            st.markdown(f"**{selected_option}**")
            
            name = st.text_input("Nombre", value=selected_insurer.get('name', '') if selected_insurer else "")
            logo_url = st.text_input("URL del Logo", value=selected_insurer.get('logo_url', '') if selected_insurer else "")
            
            if logo_url:
                st.image(logo_url, width=100, caption="Vista previa")
            
            c1, c2 = st.columns(2)
            with c1:
                active = st.checkbox("Activa", value=selected_insurer.get('active', True) if selected_insurer else True)
                is_admitted = st.checkbox("Admitida en Centro", value=selected_insurer.get('is_admitted', True) if selected_insurer else True, help="Si no está admitida, se mostrará aviso al intentar seleccionarla.")
            
            with c2:
                is_insurer = st.checkbox("Es Aseguradora", value=selected_insurer.get('is_insurer', True) if selected_insurer else True)
                is_mutual = st.checkbox("Es Mutua", value=selected_insurer.get('is_mutual', False) if selected_insurer else False)
            
            submitted = st.form_submit_button("💾 Guardar")
            
            if submitted:
                if not name:
                    st.error("El nombre es obligatorio.")
                else:
                    data = {
                        "name": name,
                        "logo_url": logo_url,
                        "active": active,
                        "is_admitted": is_admitted,
                        "is_insurer": is_insurer,
                        "is_mutual": is_mutual
                    }
                    
                    if selected_insurer:
                        repo.update(selected_insurer['_id'], data)
                        st.success("Aseguradora actualizada.")
                    else:
                        repo.create(data)
                        st.success("Aseguradora creada.")
                    st.rerun()

        # Botón de borrar fuera del form
        if selected_insurer:
            if st.button("🗑️ Eliminar", type="primary"):
                repo.delete(selected_insurer['_id'])
                st.success("Eliminada.")
                st.rerun()
