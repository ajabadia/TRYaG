# path: src/components/common/user_selector.py
# Creado: 2025-11-25
"""
Componente para la selección temporal de usuario (Testing/Dev).
Permite cambiar la identidad del usuario actual sin proceso de login.
"""
import streamlit as st
from db.repositories.users import get_users_repository
from db.repositories.roles import get_role_by_code

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
    user_options = {}
    for u in users:
        nombre_display = u.get('nombre_completo')
        if not nombre_display:
            # Fallback: Construct from parts or use username
            parts = [u.get('nombre', ''), u.get('apellidos', '')]
            nombre_display = " ".join(p for p in parts if p).strip() or u['username']
            
        user_options[f"{nombre_display} ({u['username']})"] = u
    
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
        # Reconstruct key for current user
        c_nombre = current_user.get('nombre_completo')
        if not c_nombre:
             parts = [current_user.get('nombre', ''), current_user.get('apellidos', '')]
             c_nombre = " ".join(p for p in parts if p).strip() or current_user['username']
             
        current_key = f"{c_nombre} ({current_user['username']})"
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
    
    display_name = selected_user.get('nombre_completo')
    if not display_name:
         parts = [selected_user.get('nombre', ''), selected_user.get('apellidos', '')]
         display_name = " ".join(p for p in parts if p).strip() or selected_user['username']

    st.sidebar.info(
        f"**{display_name}**\n\n"
        f"🆔 {selected_user.get('internal_id', '-')}\n\n"
        f"🔑 {role_name}"
    )
