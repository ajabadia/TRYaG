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
    # --- NUEVA LÓGICA: Mostrar Info + Botón de Cambio (Logout) ---
    
    current_user = st.session_state.get("current_user")
    
    if not current_user:
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Usuario Actual")
    
    # Mostrar info del usuario
    display_name = current_user.get('nombre_completo')
    if not display_name:
         parts = [current_user.get('nombre', ''), current_user.get('apellidos', '')]
         display_name = " ".join(p for p in parts if p).strip() or current_user['username']
         
    role_def = get_role_by_code(current_user.get("rol"))
    role_name = role_def["nombre"] if role_def else current_user.get("rol")

    st.sidebar.info(
        f"**{display_name}**\n\n"
        f"🆔 {current_user.get('internal_id', '-')}\n\n"
        f"🔑 {role_name}"
    )

    # Botón para cambiar de usuario (Logout explícito)
    if st.sidebar.button("🔄 Cambiar Usuario / Salir", key="btn_switch_user_sidebar", use_container_width=True):
        # Registrar Logout
        try:
            from db.repositories.login_logs import get_login_logs_repository
            from utils.network_utils import get_client_ip
            
            log_repo = get_login_logs_repository()
            client_ip = get_client_ip()
            
            log_repo.log_logout(
                user_id=current_user["_id"],
                username=current_user.get("username", "unknown"),
                ip_address=client_ip
            )
        except Exception as e:
            print(f"Error logging logout: {e}")
            
        # Limpiar sesión
        st.session_state.current_user = None
        st.session_state.login_selected_user = None
        st.rerun()

    # --- INTEGRACIÓN MENÚ DE USUARIO (Migrado desde user_menu.py) ---
    st.sidebar.divider()
    
    # 1. Sistema / Modos
    st.sidebar.markdown("⚙️ **Sistema**")
    
    # Modo Contingencia
    from services.contingency_service import is_contingency_active, set_contingency_mode, get_unsynced_count
    is_offline = is_contingency_active()
    new_state = st.sidebar.toggle("Modo Manual (Sin IA)", value=is_offline, key="toggle_offline_sidebar", help="Activa este modo para guardar directamente en Base de Datos sin pasar por el análisis de Gemini.")
    
    if new_state != is_offline:
        set_contingency_mode(new_state)
        st.rerun()
        
    unsynced = get_unsynced_count()
    if unsynced > 0:
        st.sidebar.caption(f"⚠️ {unsynced} registros locales")

    # Modo Formación
    is_training = st.session_state.get('training_mode', False)
    new_training = st.sidebar.toggle("Modo Formación", value=is_training, key="toggle_training_sidebar")
    if new_training != is_training:
        st.session_state.training_mode = new_training
        st.rerun()
        
    st.sidebar.divider()

    # 2. Herramientas (Lo último)
    st.sidebar.markdown("🛠️ **Herramientas**")
    
    # Feedback
    from components.common.feedback_button import render_feedback_button
    # Renderizar feedback en sidebar
    with st.sidebar:
        render_feedback_button("SidebarUserMenu")
        
    st.sidebar.divider()
    

    st.markdown('<div class="debug-footer">src/components/common/user_selector.py</div>', unsafe_allow_html=True)
