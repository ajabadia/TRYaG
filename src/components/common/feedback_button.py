# path: src/components/common/feedback_button.py
import streamlit as st
from services.feedback_service import save_feedback_report

@st.dialog("📝 Reportar Feedback / Error")
def feedback_form(module_name):
    with st.form("feedback_form_inner"):
        report_type = st.selectbox("Tipo de Reporte", ["Error", "Mejora", "Comentario"])
        title = st.text_input("Título", placeholder="Resumen del problema o sugerencia")
        description = st.text_area("Descripción", placeholder="Detalles adicionales...")
        
        uploaded_files = st.file_uploader(
            "Adjuntar archivos (opcional)", 
            accept_multiple_files=True,
            type=["png", "jpg", "jpeg", "pdf", "txt", "log"]
        )
        
        submitted = st.form_submit_button("Enviar Reporte", type="primary")
        
        if submitted:
            if not title:
                st.error("Por favor, indica un título.")
                return

            user_id = st.session_state.get("user", {}).get("username", "anonymous")
            
            data = {
                "user_id": user_id,
                "module": module_name,
                "type": report_type,
                "title": title,
                "description": description
            }
            
            if save_feedback_report(data, files=uploaded_files):
                st.success("¡Reporte enviado! Gracias por tu feedback.")
                st.rerun()
            else:
                st.error("Error al enviar el reporte.")

def render_feedback_button(module_name="General", location="header"):
    """
    Renderiza un botón discreto para abrir el formulario de feedback.
    """
    # Usamos un botón pequeño con icono
    if st.button("🐞", key=f"feedback_btn_{module_name}", help="Reportar error o sugerencia"):
        feedback_form(module_name)

    st.markdown('<div class="debug-footer">src/components/common/feedback_button.py</div>', unsafe_allow_html=True)
