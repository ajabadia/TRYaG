import streamlit as st
from datetime import datetime
import re
import unicodedata
from services.report_service import generate_triage_pdf
from utils.triage_utils import get_current_triage_record
from components.common.feedback_button import render_feedback_button

def render_tools_panel(module_name="General", patient=None, show_pdf=True):
    """
    Renderiza un panel de herramientas común (Feedback, Descargas, etc.)
    
    Args:
        module_name (str): Nombre del módulo para el reporte de feedback.
        patient (dict): Datos del paciente para generar el PDF (opcional).
        show_pdf (bool): Si mostrar o no la opción de descarga de PDF.
    """
    with st.expander("🛠️ Herramientas", expanded=False):
        cols = st.columns([1, 1, 1])
        
        with cols[0]:
            st.markdown("**Feedback**")
            render_feedback_button(module_name)
            
        with cols[1]:
            if show_pdf:
                st.markdown("**Descargas**")
                if patient:
                    # Intentar obtener registro actual, si falla o está vacío, no mostrar botón
                    try:
                        record = get_current_triage_record()
                    except:
                        record = None
                        
                    if record:
                        record["destination"] = "BORRADOR - EN PROCESO"
                        try:
                            pdf_bytes = generate_triage_pdf(record)
                            
                            raw_name = f"{patient.get('nombre', 'Paciente')}_{patient.get('apellido1', '')}"
                            normalized = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('ASCII')
                            safe_name = re.sub(r'[^\w\-_]', '_', normalized)
                            file_name = f"Borrador_{safe_name}_{datetime.now().strftime('%H%M')}.pdf"
                            
                            st.download_button(
                                label="📄 Borrador PDF",
                                data=pdf_bytes,
                                file_name=file_name,
                                mime="application/octet-stream",
                                use_container_width=True,
                                key=f"btn_download_draft_pdf_{module_name}"
                            )
                        except Exception as e:
                            st.error(f"Error PDF: {e}")
                    else:
                        st.caption("Sin datos para PDF")
                else:
                    st.caption("Seleccione paciente")

        with cols[2]:
            st.markdown("**Sistema**")
            from services.contingency_service import is_contingency_active, set_contingency_mode, get_unsynced_count
            
            is_offline = is_contingency_active()
            # Toggle para simular desconexión
            new_state = st.toggle("Modo Contingencia (Offline)", value=is_offline, key=f"toggle_offline_{module_name}")
            
            if new_state != is_offline:
                set_contingency_mode(new_state)
                st.rerun()
                
            unsynced = get_unsynced_count()
            if unsynced > 0:
                st.caption(f"⚠️ {unsynced} registros locales")

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/components/common/tools_panel.py</div>', unsafe_allow_html=True)
