# path: src/ui/config/center_groups_manager.py
import streamlit as st
from db.repositories.center_groups import get_center_group_repository
from db.models import CenterGroup
from db.repositories.general_config import get_general_config_repository
from db.repositories.centros import get_centros_repository

def render_center_groups_manager():
    """Renderiza el gestor de grupos de centros."""
    st.subheader("🏢 Grupos de Centros (Multi-Tenant)")
    st.info("Agrupe centros para gestión consolidada (ej: Zona Norte, Hospitales Privados).")

    repo = get_center_group_repository()
    centros_repo = get_centros_repository()
    
    groups = repo.get_all()

    # --- CREAR NUEVO GRUPO ---
    with st.expander("➕ Crear Nuevo Grupo", expanded=False):
        with st.form("new_group_form"):
            new_name = st.text_input("Nombre del Grupo")
            new_desc = st.text_area("Descripción")
            
            if st.form_submit_button("Crear Grupo"):
                if new_name:
                    new_group = CenterGroup(
                        name=new_name,
                        description=new_desc,
                        center_ids=[] # Deprecated
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
                
                # Obtener centros asignados
                assigned_centers = centros_repo.get_centers_by_group(str(group.id))
                center_names = [c.get('denominacion', 'Sin nombre') for c in assigned_centers]
                
                if center_names:
                    st.success(f"**Centros Asignados:** {', '.join(center_names)}")
                else:
                    st.warning("Sin centros asignados. (Asigne el grupo desde Configuración > Centro > Datos)")
            
            with c2:
                if st.button("🗑️ Eliminar", key=f"del_{group.id}"):
                    repo.delete(str(group.id))
                    st.rerun()

            # Edición rápida
            with st.expander(f"✏️ Editar {group.name}"):
                with st.form(f"edit_group_{group.id}"):
                    edit_name = st.text_input("Nombre", value=group.name)
                    edit_desc = st.text_area("Descripción", value=group.description)
                    
                    if st.form_submit_button("Guardar Cambios"):
                        repo.update(str(group.id), {
                            "name": edit_name,
                            "description": edit_desc
                        })
                        st.success("Grupo actualizado.")
                        st.rerun()

    st.markdown('<div class="debug-footer">src/ui/config/center_groups_manager.py</div>', unsafe_allow_html=True)
