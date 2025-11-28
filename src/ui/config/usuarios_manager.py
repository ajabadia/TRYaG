# path: src/ui/config/usuarios_manager.py
# Creado: 2025-11-25
"""
UI para la gestión de usuarios del sistema.
Permite crear, editar y desactivar usuarios, asignando roles y funciones.
"""
import streamlit as st
import time
from datetime import datetime
from src.db.repositories.users import get_users_repository
from src.db.repositories.people import get_people_repository
from src.db.repositories.roles import get_all_roles, get_role_by_code
from src.db.repositories.funciones import get_all_funciones, get_funcion_by_code, get_funciones_repository

def render_user_card(user: dict):
    """Renderiza una tarjeta de usuario."""
    role_info = get_role_by_code(user.get("rol", "usuario"))
    role_name = role_info["nombre"] if role_info else user.get("rol")
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"#### {user.get('nombre_completo', 'Sin Nombre')}")
            st.caption(f"🆔 {user.get('internal_id', '-')} | 👤 {user.get('username', '-')}")
            st.markdown(f"**Rol:** {role_name}")
            
            funciones = user.get("funciones", [])
            if funciones:
                funcs_str = ", ".join([f.capitalize() for f in funciones])
                st.markdown(f"**Funciones:** {funcs_str}")
                
        with col2:
            if st.button("✏️", key=f"edit_usr_{user.get('_id')}"):
                edit_user_dialog(user)
            
            # Botón de estado (Activo/Inactivo)
            is_active = user.get("activo", True)
            btn_label = "🛑" if is_active else "✅"
            btn_help = "Desactivar usuario" if is_active else "Activar usuario"
            
            if st.button(btn_label, key=f"toggle_usr_{user.get('_id')}", help=btn_help):
                _toggle_user_status(user)

def _toggle_user_status(user: dict):
    """Cambia el estado activo/inactivo de un usuario."""
    repo = get_users_repository()
    new_status = not user.get("activo", True)
    if repo.update_user(str(user["_id"]), {"activo": new_status}):
        st.toast(f"Usuario {'activado' if new_status else 'desactivado'} correctamente")
        time.sleep(0.5)
        st.rerun()
    else:
        st.error("Error al actualizar estado")


@st.dialog("Gestión de Usuario", width="large")
def edit_user_dialog(user: dict = None):
    """Modal para crear o editar usuario."""
    from ui.config.people_manager import person_dialog
    
    is_new = user is None
    user = user or {}
    
    # Recuperar datos de persona si existe person_id
    person_data = {}
    if user.get("person_id"):
        repo_p = get_people_repository()
        person_data = repo_p.get_by_id(user["person_id"]) or {}
    
    # Título
    if is_new:
        st.markdown("### Nuevo Usuario")
    else:
        st.markdown(f"### Editar: {user.get('username')}")
    
    # Botón para gestionar datos personales (abre otro dialog)
    col_link, col_info = st.columns([1, 2])
    with col_link:
        if st.button("👤 Gestionar Datos Personales", type="primary", use_container_width=True):
            def on_person_save(pid):
                st.session_state[f"temp_person_id_{user.get('_id', 'new')}"] = pid
            
            person_dialog(user.get("person_id") or st.session_state.get(f"temp_person_id_{user.get('_id', 'new')}"), on_save=on_person_save)
    
    # Verificar si hay un ID temporal guardado en session_state tras crear persona
    temp_pid = st.session_state.get(f"temp_person_id_{user.get('_id', 'new')}")
    if temp_pid:
        user["person_id"] = temp_pid
        repo_p = get_people_repository()
        person_data = repo_p.get_by_id(temp_pid) or {}

    with st.form(key=f"form_user_{user.get('_id', 'new')}"):
        col_pers, col_sys = st.columns(2)
        
        # Datos Personales (Read-Only, vienen de People)
        with col_pers:
            st.markdown("##### 👤 Datos Personales (Vinculados)")
            if not person_data:
                st.warning("⚠️ Debes vincular una persona primero.")
            
            # Mostrar datos de persona (solo lectura)
            nombre_completo = (person_data.get("nombre") or "") + " " + (person_data.get("apellido1") or "") + " " + (person_data.get("apellido2") or "")
            ids = person_data.get("identificaciones", [])
            dni = ids[0]["value"] if ids else ""
            
            st.text_input("Nombre Completo", value=nombre_completo.strip(), disabled=True)
            st.text_input("DNI / Identificación", value=dni, disabled=True)
            
            # Estos campos siguen en usuario o se migran? El plan dice "Eliminar duplicidad".
            # Asumimos que email/telefono pueden ser específicos de usuario corporativo, 
            # pero idealmente vendrían de contact_info de persona.
            # Por ahora mantenemos editable lo específico de usuario si se desea, o read-only.
            # El plan dice: "Eliminar duplicidad de datos de identificación".
            # Mantendremos internal_id, email, telefono en usuario por compatibilidad, pero idealmente sync.
            internal_id = st.text_input("ID Interno (Empleado)", value=user.get("internal_id", ""))
            email = st.text_input("Email Corporativo", value=user.get("email", ""))
            telefono = st.text_input("Teléfono Corporativo", value=user.get("telefono", ""))

        # Datos de Sistema
        with col_sys:
            st.markdown("##### 🔐 Acceso y Permisos")
            username = st.text_input("Nombre de Usuario", value=user.get("username", ""))
            
            # Selector de Rol
            roles = get_all_roles()
            role_options = [r["code"] for r in roles]
            role_labels = [r["nombre"] for r in roles]
            current_role = user.get("rol", "usuario")
            try:
                role_index = role_options.index(current_role)
            except ValueError:
                role_index = 0
            
            selected_role = st.selectbox("Rol del Sistema", options=role_options, format_func=lambda x: role_labels[role_options.index(x)], index=role_index)
            
            # Selector de Funciones
            funciones = get_all_funciones()
            func_options = [f["code"] for f in funciones]
            func_labels = [f["nombre"] for f in funciones]
            default_funcs = user.get("funciones", [])
            
            selected_funcs = st.multiselect("Funciones Asignadas", options=func_options, default=default_funcs, format_func=lambda x: func_labels[func_options.index(x)])
            
            # Opción para crear nueva función inline
            st.caption("O crea una nueva y asígnala directamente:")
            new_func_name_input = st.text_input("Nueva Función (Nombre)", placeholder="Ej: Celador de Planta", help="Se creará esta función y se asignará al usuario.")
            
            puesto = st.text_input("Puesto / Cargo", value=user.get("puesto", ""))

        submitted = st.form_submit_button("💾 Guardar Usuario")
        
        if submitted:
            if not username:
                st.error("El nombre de usuario es obligatorio.")
            elif not user.get("person_id") and not temp_pid:
                st.error("Debes vincular una persona antes de guardar.")
            else:
            # Lógica para crear nueva función si se especificó
                if new_func_name_input:
                    repo_f = get_funciones_repository()
                    new_code = new_func_name_input.lower().strip().replace(" ", "_")
                    # Verificar si ya existe
                    if not repo_f.get_funcion_by_code(new_code):
                        new_func_data = {
                            "code": new_code,
                            "nombre": new_func_name_input.strip(),
                            "descripcion": f"Función: {new_func_name_input}",
                            "color": "#6C757D",
                            "icon": "work",
                            "tipos_sala_compatibles": []
                        }
                        repo_f.create_funcion(new_func_data)
                        selected_funcs.append(new_code)
                        st.toast(f"Función '{new_func_name_input}' creada y asignada.")
                    else:
                        # Si ya existe, solo la asignamos si no estaba
                        if new_code not in selected_funcs:
                            selected_funcs.append(new_code)
                            st.toast(f"La función '{new_func_name_input}' ya existía, se ha asignado.")

                repo = get_users_repository()
                user_data = {
                    "person_id": user.get("person_id") or temp_pid,
                    "nombre_completo": nombre_completo.strip(), # Se guarda redundante por performance/compatibilidad, pero viene de persona
                    "identification_number": dni, # Redundante
                    "internal_id": internal_id,
                    "email": email,
                    "telefono": telefono,
                    "username": username,
                    "rol": selected_role,
                    "funciones": selected_funcs,
                    "puesto": puesto,
                    "activo": user.get("activo", True)
                }
                
                if is_new:
                    repo.create_user(user_data)
                    st.success("Usuario creado exitosamente")
                else:
                    repo.update_user(str(user["_id"]), user_data)
                    st.success("Usuario actualizado exitosamente")
                
                # Limpiar temp
                if f"temp_person_id_{user.get('_id', 'new')}" in st.session_state:
                    del st.session_state[f"temp_person_id_{user.get('_id', 'new')}"]
                
                time.sleep(1)
                st.rerun()

def render_usuarios_manager():
    """Componente principal de gestión de usuarios."""
    st.markdown("### 👤 Gestión de Usuarios")
    st.caption("Administra los usuarios, roles y permisos del sistema.")
    
    # Botón Nuevo Usuario
    if st.button("➕ Nuevo Usuario", type="primary"):
        edit_user_dialog(None)
    
    # Filtros y Búsqueda
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_term = st.text_input("🔍 Buscar usuario", placeholder="Nombre, usuario o DNI...")
    with col_filter:
        role_filter = st.selectbox("Filtrar por Rol", ["Todos"] + [r["nombre"] for r in get_all_roles()])
    
    # Obtener usuarios
    repo = get_users_repository()
    users = repo.get_all_users(active_only=False)
    
    # Filtrado en memoria (para este MVP)
    if search_term:
        term = search_term.lower()
        users = [u for u in users if term in u.get("nombre_completo", "").lower() or term in u.get("username", "").lower()]
    
    if role_filter != "Todos":
        # Mapear nombre de rol a código
        roles = get_all_roles()
        role_code = next((r["code"] for r in roles if r["nombre"] == role_filter), None)
        if role_code:
            users = [u for u in users if u.get("rol") == role_code]
    
    # Agrupar por Rol para visualización
    roles_order = ["superadministrador", "administrador", "usuario", "auditor"]
    
    for role_code in roles_order:
        role_users = [u for u in users if u.get("rol") == role_code]
        if role_users:
            role_def = get_role_by_code(role_code)
            st.subheader(f"{role_def['nombre']} ({len(role_users)})")
            
            # Grid de tarjetas
            cols = st.columns(2)
            for i, user in enumerate(role_users):
                with cols[i % 2]:
                    render_user_card(user)
            st.divider()
