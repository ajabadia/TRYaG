# path: src/ui/config/center_groups_manager.py
import streamlit as st
from db.repositories.center_groups import get_center_group_repository
from db.models import CenterGroup
from db.repositories.general_config import get_general_config_repository

def render_center_groups_manager():
    """Renderiza el gestor de grupos de centros."""
    st.subheader("🏢 Grupos de Centros (Multi-Tenant)")
    st.info("Agrupe centros para gestión consolidada (ej: Zona Norte, Hospitales Privados).")

    repo = get_center_group_repository()
    config_repo = get_general_config_repository()
    
    # Obtener centros disponibles (simulado desde config por ahora, idealmente de una colección 'centros')
    # Asumimos que los centros están en config o hardcoded en selectores. 
    # Para este MVP, usaremos una lista de centros extraída de la configuración actual o permitiremos texto libre/IDs.
    # MEJORA: Leer de una colección real de centros si existiera. 
    # Por ahora, simulamos centros disponibles basados en lo que el usuario pueda haber configurado.
    available_centers = ["Centro Principal", "Clínica Periférica", "Hospital Norte", "Hospital Sur"] 
    
    groups = repo.get_all()

    # --- CREAR NUEVO GRUPO ---
    with st.expander("➕ Crear Nuevo Grupo", expanded=False):
        with st.form("new_group_form"):
            new_name = st.text_input("Nombre del Grupo")
            new_desc = st.text_area("Descripción")
            new_centers = st.multiselect("Asignar Centros Iniciales", available_centers)
            
            if st.form_submit_button("Crear Grupo"):
                if new_name:
                    new_group = CenterGroup(
                        name=new_name,
                        description=new_desc,
                        center_ids=new_centers
                    )
                    repo.create(new_group)
                    st.success(f"Grupo '{new_name}' creado.")
                    st.rerun()
                else:
                    st.error("El nombre es obligatorio.")

    # --- LISTAR Y EDITAR GRUPOS ---
    if not groups:
        st.warning("No hay grupos configurados.")
        return

    for group in groups:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"### {group.name}")
                if group.description:
                    st.caption(group.description)
                st.write(f"**Centros Asignados:** {', '.join(group.center_ids) if group.center_ids else 'Ninguno'}")
            
            with c2:
                if st.button("🗑️ Eliminar", key=f"del_{group.id}"):
                    repo.delete(str(group.id))
                    st.rerun()

            # Edición rápida
            with st.expander(f"✏️ Editar {group.name}"):
                with st.form(f"edit_group_{group.id}"):
                    edit_name = st.text_input("Nombre", value=group.name)
                    edit_desc = st.text_area("Descripción", value=group.description)
                    edit_centers = st.multiselect(
                        "Centros Asignados", 
                        available_centers, 
                        default=[c for c in group.center_ids if c in available_centers]
                    )
                    
                    if st.form_submit_button("Guardar Cambios"):
                        repo.update(str(group.id), {
                            "name": edit_name,
                            "description": edit_desc,
                            "center_ids": edit_centers
                        })
                        st.success("Grupo actualizado.")
                        st.rerun()

    st.markdown('<div class="debug-footer">src/ui/config/center_groups_manager.py</div>', unsafe_allow_html=True)
