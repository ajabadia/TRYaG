# path: src/components/common/user_selector.py
# Creado: 2025-11-25
"""
Componente para la selección temporal de usuario (Testing/Dev).
Permite cambiar la identidad del usuario actual sin proceso de login.
"""
import streamlit as st
from src.db.repositories.users import get_users_repository
from src.db.repositories.roles import get_role_by_code

def render_user_selector():
    """
    Renderiza un selector de usuarios en la barra lateral.
    Actualiza st.session_state.current_user con el usuario seleccionado.
    """
    repo = get_users_repository()
    users = repo.get_all_users(active_only=True)
    
    if not users:
        st.sidebar.error("No hay usuarios activos.")
        return

    # Mapeo para el selectbox: "Nombre (Rol)" -> User Object
    # Usamos el ID como clave única para evitar problemas con nombres duplicados
    user_options = {f"{u['nombre_completo']} ({u['username']})": u for u in users}
    
    # Determinar índice actual
    current_user = st.session_state.get("current_user")
    index = 0
    
    # Si no hay usuario seleccionado, seleccionar el primero (Superadmin por defecto si está)
    if not current_user:
        # Intentar buscar superadmin por defecto
        superadmin = next((u for u in users if u["username"] == "superadmin"), None)
        if superadmin:
            st.session_state.current_user = superadmin
            current_user = superadmin
        else:
            st.session_state.current_user = list(user_options.values())[0]
            current_user = st.session_state.current_user

    if current_user:
        current_key = f"{current_user['nombre_completo']} ({current_user['username']})"
        if current_key in user_options:
            index = list(user_options.keys()).index(current_key)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Usuario Actual")
    
    selected_key = st.sidebar.selectbox(
        "Cambiar Usuario",
        options=list(user_options.keys()),
        index=index,
        label_visibility="collapsed",
        key="user_selector_sidebar"
    )
    
    selected_user = user_options[selected_key]
    
    # Actualizar session_state si cambia (comparando IDs)
    if current_user and str(current_user["_id"]) != str(selected_user["_id"]):
        st.session_state.current_user = selected_user
        st.rerun()
        
    # Mostrar info del usuario seleccionado
    role_def = get_role_by_code(selected_user.get("rol"))
    role_name = role_def["nombre"] if role_def else selected_user.get("rol")
    
    st.sidebar.info(
        f"**{selected_user['nombre_completo']}**\n\n"
        f"🆔 {selected_user.get('internal_id', '-')}\n\n"
        f"🔑 {role_name}"
    )
