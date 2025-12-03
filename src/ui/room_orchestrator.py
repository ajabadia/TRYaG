# path: src/ui/room_orchestrator.py
# Creado: 2025-11-25
"""
Orquestador de Gestión de Salas.
Contiene dos subsecciones: Gestión y Dashboard.
"""
import streamlit as st


def mostrar_orquestador_salas():
    """
    Renderiza el orquestador principal con subsecciones.
    """
    st.header("📊 Control de Salas")
    st.markdown("Centro de operaciones para gestión, monitoring y análisis de salas.")
    
    # Unread notifications badge
    from services.notification_service import get_unread_count
    unread = get_unread_count()
    
    # Tabs principales
    tab_labels = [
        "🚪 Gestión",
        "📈 Dashboard & Métricas"
    ]
    
    # Añadir badge si hay notificaciones
    if unread > 0:
        tab_labels.append(f"🔔 Notificaciones ({unread})")
    else:
        tab_labels.append("🔔 Notificaciones")
    
    tabs = st.tabs(tab_labels)
    
    tab_gestion, tab_dashboard, tab_notifications = tabs
    
    with tab_gestion:
        from ui.room_manager_view import mostrar_gestor_salas
        mostrar_gestor_salas()
    
    with tab_dashboard:
        from ui.room_metrics_dashboard import render_metrics_dashboard
        render_metrics_dashboard()
    
    with tab_notifications:
        from services.notification_service import render_notifications_panel
        render_notifications_panel(user_id="admin")

        st.markdown('<div class="debug-footer">src/ui/room_orchestrator.py</div>', unsafe_allow_html=True)
