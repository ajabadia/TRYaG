# path: src/ui/audit_panel/feedback_management.py
"""
Módulo de gestión de Feedback (Admin View).
Permite visualizar, filtrar y responder a los reportes de feedback de los usuarios.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from services.feedback_service import (
    get_feedback_reports,
    update_feedback_status,
    add_reply_to_report,
    soft_delete_feedback
)
from utils.icons import render_icon

def render_feedback_management():
    """
    Renderiza el panel de gestión de feedback para administradores.
    """
    st.markdown("### 📢 Gestión de Feedback y Soporte")
    st.markdown("Administración de reportes de error y sugerencias de usuarios.")
    
    # --- FILTROS ---
    with st.expander("🔍 Filtros y Búsqueda", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            status_filter = st.multiselect(
                "Estado",
                ["New", "In Progress", "Resolved", "Rejected", "Deleted"],
                default=["New", "In Progress"]
            )
        with c2:
            module_filter = st.text_input("Módulo (Búsqueda textual)", placeholder="Ej: Triaje, General")
        with c3:
           st.markdown("<br>", unsafe_allow_html=True)
           show_deleted = st.checkbox("Mostrar Eliminados", value=False)

    # --- CARGA DE DATOS ---
    try:
        # Si 'show_deleted' es True, traemos todos y filtramos en memoria o modificamos servicio
        # El servicio ya tiene parámetro include_deleted
        raw_reports = get_feedback_reports(limit=200, include_deleted=show_deleted)
        
        # Filtrado en memoria
        filtered_reports = []
        for r in raw_reports:
            # Filtro Estado
            if status_filter and r.get("status", "New") not in status_filter:
                continue
            # Filtro Modulo
            if module_filter and module_filter.lower() not in r.get("module", "").lower():
                continue
            filtered_reports.append(r)
            
        df = pd.DataFrame(filtered_reports)
    except Exception as e:
        st.error(f"Error cargando feedback: {e}")
        return

    # --- TABLA MASTER ---
    if df.empty:
        st.info("No hay reportes que coincidan con los filtros.")
    else:
        # Preparar columnas para display
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Mapeo de iconos de estado
        status_icons = {
            "New": "🔴 New",
            "In Progress": "🟠 In Progress",
            "Resolved": "🟢 Resolved",
            "Rejected": "⚫ Rejected",
            "Deleted": "🗑️ Deleted"
        }
        df["status_display"] = df["status"].map(status_icons).fillna(df["status"])
        
        # Definir configuracion de columnas
        column_config = {
            "timestamp": st.column_config.DatetimeColumn("Fecha", format="D MMM YYYY, h:mm a"),
            "status_display": st.column_config.TextColumn("Estado", width="medium"),
            "type": st.column_config.TextColumn("Tipo", width="small"),
            "title": st.column_config.TextColumn("Título", width="large"),
            "user_id": st.column_config.TextColumn("Usuario"),
            "module": st.column_config.TextColumn("Módulo"),
            "_id": st.column_config.TextColumn("ID", disabled=True),
        }
        
        # Selección
        col_list, col_detail = st.columns([2, 1]) 
        
        # Usamos dataframe con selection mode 'single-row'
        event = st.dataframe(
            df[["timestamp", "status_display", "type", "module", "user_id", "title"]],
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        selected_index = event.selection.rows
        
        if selected_index:
            report_index = selected_index[0]
            selected_report = df.iloc[report_index]
            # Recuperar objeto completo de la lista original usando index dataframe no siempre es seguro si df filtrado
            # Mejor buscar por ID si fuera necesario, pero aqui filtered_reports y df coinciden en orden
            report_data = filtered_reports[report_index]
            
            _render_report_detail_modal(report_data)

def _render_report_detail_modal(report):
    """Muestra el detalle del reporte en un diálogo."""
    
    @st.dialog(f"📝 Detalle Reporte: {report.get('title')}", width="large")
    def show_modal():
        c_status, c_actions = st.columns([2, 1])
        
        with c_status:
           status_color = {
               "New": "🔴",
               "In Progress": "🟠",
               "Resolved": "🟢",
               "Rejected": "⚫",
               "Deleted": "🗑️"
           }
           st.subheader(f"{status_color.get(report.get('status', 'New'), '⚪')} {report.get('status', 'New')}")
           st.caption(f"ID: {report['_id']} | Fecha: {report['timestamp']}")
           st.markdown(f"**Usuario:** {report.get('user_id')} | **Módulo:** {report.get('module')}")
        
        with c_actions:
            # Cambio de Estado
            new_status = st.selectbox(
                "Cambiar Estado",
                ["New", "In Progress", "Resolved", "Rejected"],
                index=["New", "In Progress", "Resolved", "Rejected"].index(report.get("status", "New")) if report.get("status", "New") in ["New", "In Progress", "Resolved", "Rejected"] else 0,
                key=f"status_sel_{report['_id']}"
            )
            
            if new_status != report.get("status", "New"):
                if st.button("Actualizar Estado"):
                    update_feedback_status(
                        str(report['_id']), 
                        new_status, 
                        st.session_state.current_user.get("username", "admin")
                    )
                    st.success("Estado actualizado")
                    st.rerun()

        st.divider()
        st.markdown("#### Descripción")
        st.info(report.get("description", "Sin descripción"))
        
        # Adjuntos Originales
        if report.get("attachments"):
            st.markdown("#### 📎 Adjuntos")
            for att in report["attachments"]:
                # Link de descarga (implementación simple leyendo binario)
                try:
                    with open(att["path"], "rb") as f:
                        st.download_button(
                            label=f"⬇️ {att['name']} ({att.get('size', 0)//1024} KB)",
                            data=f,
                            file_name=att["name"],
                            key=f"dl_{att['md5']}"
                        )
                except Exception:
                    st.warning(f"Archivo no encontrado: {att['name']}")

        st.divider()
        
        # --- HILO DE CONVERSACIÓN ---
        st.markdown("#### 💬 Conversación")
        
        conversation = report.get("conversation", [])
        
        if not conversation:
            st.caption("No hay mensajes en el hilo.")
        
        for msg in conversation:
            is_admin = msg.get("is_admin_reply", False)
            align = "right" if is_admin else "left"
            bg_color = "#e3f2fd" if is_admin else "#f5f5f5"
            avatar = "👨‍⚕️" if is_admin else "👤"
            user_label = "Soporte" if is_admin else msg.get("user_id", "Usuario")
            
            st.markdown(
                f"""
                <div style="display: flex; justify-content: {align}; margin-bottom: 10px;">
                    <div style="background-color: {bg_color}; padding: 10px; border-radius: 10px; max-width: 80%;">
                        <small><b>{avatar} {user_label}</b> - {msg['timestamp'].strftime('%d/%m %H:%M')}</small><br>
                        {msg['message']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Mostrar adjuntos del mensaje si los hay
            if msg.get("attachments"):
                for att in msg["attachments"]:
                    st.caption(f"📎 {att['name']}")
        
        st.markdown("---")
        
        # --- RESPONDER ---
        with st.form(key=f"reply_form_{report['_id']}"):
            st.markdown("##### ↩️ Responder")
            reply_text = st.text_area("Mensaje", height=100)
            reply_files = st.file_uploader("Adjuntar archivos", accept_multiple_files=True, key=f"uploader_{report['_id']}")
            
            col_submit, col_del = st.columns([4, 1])
            with col_submit:
                if st.form_submit_button("Enviar Respuesta", type="primary"):
                    if reply_text:
                        add_reply_to_report(
                            str(report['_id']),
                            reply_text,
                            st.session_state.current_user.get("username", "admin"),
                            is_admin=True,
                            files=reply_files
                        )
                        st.success("Respuesta enviada")
                        st.rerun()
                    else:
                        st.warning("Escribe un mensaje.")
            
            with col_del:
                # Soft Delete Button
                if report.get("status") != "Deleted":
                    if st.form_submit_button("🗑️ Eliminar"):
                        soft_delete_feedback(
                            str(report['_id']),
                            st.session_state.current_user.get("username", "admin")
                        )
                        st.warning("Reporte marcado como eliminado.")
                        st.rerun()

    show_modal()
