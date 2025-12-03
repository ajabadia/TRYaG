import streamlit as st
from components.common.feedback_button import render_feedback_button
from services.contingency_service import is_contingency_active, set_contingency_mode, get_unsynced_count
from services.permissions_service import get_current_user

def render_user_menu():
    """
    Renderiza el menú de usuario en la cabecera (Avatar/Icono).
    Al hacer clic, muestra un popover con información y herramientas.
    """
    user = get_current_user()
    if user:
        username = user.get("username", "Usuario")
        role = user.get("role", "Desconocido")
    else:
        username = "Usuario"
        role = "Invitado"
    
    # Usar un popover para el menú
    with st.popover(f"👤 {username}", help="Menú de Usuario"):
        st.markdown(f"**Rol:** {role}")
        st.divider()
        
        # --- HERRAMIENTAS ---
        st.markdown("🛠️ **Herramientas**")
        
        # Feedback
        render_feedback_button("UserMenu")
        
        st.divider()
        
        # --- SISTEMA ---
        st.markdown("⚙️ **Sistema**")
        
        # Modo Contingencia
        is_offline = is_contingency_active()
        new_state = st.toggle("Modo Contingencia (Offline)", value=is_offline, key="toggle_offline_menu")
        
        if new_state != is_offline:
            set_contingency_mode(new_state)
            st.rerun()
            
        unsynced = get_unsynced_count()
        if unsynced > 0:
            st.caption(f"⚠️ {unsynced} registros locales")

        # Modo Formación
        is_training = st.session_state.get('training_mode', False)
        new_training = st.toggle("Modo Formación", value=is_training, key="toggle_training_menu")
        if new_training != is_training:
            st.session_state.training_mode = new_training
            st.rerun()
            
        st.divider()
        
        # --- SESIÓN ---
        if st.button("Cerrar Sesión", key="btn_logout_menu", use_container_width=True):
            # Placeholder para logout real
            st.warning("Funcionalidad de Logout pendiente de implementar en Auth Service.")

    st.markdown('<div class="debug-footer">src/ui/components/common/user_menu.py</div>', unsafe_allow_html=True)
