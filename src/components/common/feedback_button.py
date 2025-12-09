# path: src/components/common/feedback_button.py
import streamlit as st
from services.feedback_service import (
    save_feedback_report, 
    get_user_feedback, 
    add_reply_to_report,
    mark_as_read_by_user,
    soft_delete_feedback
)
from datetime import datetime

@st.dialog("📝 Centro de Feedback y Soporte", width="large")
def feedback_dashboard(module_name):
    """
    Panel unificado para enviar y gestionar feedback del usuario.
    """
    tab_new, tab_list = st.tabs(["✨ Nuevo Reporte", "🗂️ Mis Reportes"])
    
    current_user = st.session_state.get("current_user", {}).get("username", "anonymous")

    # --- TAB 1: NUEVO REPORTE ---
    with tab_new:
        with st.form("feedback_form_inner"):
            report_type = st.selectbox("Tipo de Reporte", ["Error", "Mejora", "Comentario"])
            title = st.text_input("Título", placeholder="Resumen del problema o sugerencia")
            description = st.text_area("Descripción", placeholder="Detalles adicionales...")
            
            uploaded_files = st.file_uploader(
                "Adjuntar archivos (opcional)", 
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg", "pdf", "txt", "log"],
                key="new_report_uploader"
            )
            
            submitted = st.form_submit_button("Enviar Reporte", type="primary")
            
            if submitted:
                if not title:
                    st.error("Por favor, indica un título.")
                    return # Stop execution inside form

                data = {
                    "user_id": current_user,
                    "module": module_name,
                    "type": report_type,
                    "title": title,
                    "description": description
                }
                
                with st.spinner("Enviando reporte..."):
                    if save_feedback_report(data, files=uploaded_files):
                        st.success("¡Reporte enviado! Gracias por tu feedback.")
                        st.rerun()
                    else:
                        st.error("Error al enviar el reporte.")

    # --- TAB 2: MIS REPORTES ---
    with tab_list:
        user_reports = get_user_feedback(current_user)
        
        if not user_reports:
            st.info("No has enviado ningún reporte todavía.")
        else:
            for rep in user_reports:
                # Meta info visual
                status = rep.get("status", "New")
                unread = rep.get("unread_by_user", False)
                rep_id = str(rep["_id"])
                
                status_icon = {
                    "New": "🔴",
                    "In Progress": "🟠",
                    "Resolved": "🟢",
                    "Rejected": "⚫"
                }.get(status, "⚪")
                
                # Alerta visual si hay novedades
                alert_badge = "🔔 Novedades" if unread else ""
                
                with st.expander(f"{status_icon} {rep.get('title', 'Sin título')} | {rep['timestamp'].strftime('%d/%m/%Y')} {alert_badge}"):
                    # Si se expande y tenía nvoedades, marcar como leído
                    if unread:
                        mark_as_read_by_user(rep_id)
                        # No hacemos rerun forzado para no cerrar el expander, pero la próxima carga ya saldrá limpio
                    
                    c1, c2 = st.columns([0.8, 0.2])
                    with c1:
                        st.markdown(f"**Estado:** {status} | **Módulo:** {rep.get('module')}")
                    with c2:
                         if st.button("🗑️ Eliminar", key=f"del_{rep_id}", help="Eliminar reporte (soft delete)", type="secondary"):
                             if soft_delete_feedback(rep_id, current_user):
                                 st.toast("Reporte eliminado correctamente")
                                 st.rerun()
                                 
                    st.info(rep.get("description"))
                    
                    # Conversation
                    st.markdown("---")
                    st.markdown("###### 💬 Historial")
                    
                    conversation = rep.get("conversation", [])
                    if not conversation:
                        st.caption("No hay respuestas aún.")
                        
                    for msg in conversation:
                        is_admin = msg.get("is_admin_reply", False)
                        align = "right" if not is_admin else "left" # Usuario a la derecha, Soporte izq
                        bg_color = "#e3f2fd" if not is_admin else "#f1f8e9" # Azulito usuario, verdecito soporte
                        author = "Tú" if not is_admin else "Soporte"
                        
                        st.markdown(
                             f"""
                            <div style="display: flex; justify-content: {align}; margin-bottom: 5px;">
                                <div style="background-color: {bg_color}; padding: 8px; border-radius: 8px; max-width: 85%;">
                                    <small><b>{author}</b> {msg['timestamp'].strftime('%d/%m %H:%M')}</small><br>
                                    {msg['message']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    # Reply Box
                    with st.form(key=f"user_reply_{rep_id}"):
                        u_reply = st.text_area("Responder", height=70, placeholder="Escribe aquí...", key=f"txt_{rep_id}")
                        u_files = st.file_uploader("Adjuntar", accept_multiple_files=True, key=f"uf_{rep_id}")
                        if st.form_submit_button("📩 Enviar Respuesta"):
                            if u_reply:
                                add_reply_to_report(
                                    rep_id,
                                    u_reply,
                                    current_user,
                                    is_admin=False,
                                    files=u_files
                                )
                                st.success("Enviado")
                                st.rerun()

def render_feedback_button(module_name="General", location="header"):
    """
    Renderiza un botón discreto para abrir el formulario de feedback.
    """
    # Chequear notificaciones pendientes para mostrar badge en botón
    from services.feedback_service import check_unread_updates
    current_user = st.session_state.get("current_user", {}).get("username", "anonymous")
    unread_count = check_unread_updates(current_user)
    
    label = "📢 Feedback"
    if unread_count > 0:
        label = f"📢 Feedback ({unread_count})"
    
    def _reset_sidebar_modals():
        """Cierra otros modales laterales para evitar conflictos de Streamlit."""
        if "show_handoff_modal" in st.session_state:
            st.session_state["show_handoff_modal"] = False

    # Botón normal
    if st.button(label, key=f"feedback_btn_{module_name}", help="Reportar error o ver mis tickets", use_container_width=True, on_click=_reset_sidebar_modals):
        feedback_dashboard(module_name)
    

    st.markdown('<div class="debug-footer">src/components/common/feedback_button.py</div>', unsafe_allow_html=True)
