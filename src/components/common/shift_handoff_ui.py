
import streamlit as st
from datetime import datetime, timedelta

def show_handoff_dialog():
    """Muestra el diálogo de informe de relevo."""
    if hasattr(st, "dialog"):
        @st.dialog("📝 Informe de Relevo (Handoff)", width="large")
        def _render():
            
            # --- FRAGMENTO DE UI PARA EVITAR RECARGA COMPLETA ---
            # Si Streamlit soporta fragmentos, lo usamos para que "Regenerar" 
            # solo recargue el contenido del diálogo y no cierre el modal.
            if hasattr(st, "fragment"):
                @st.fragment
                def _render_content():
                    _dialog_logic()
                _render_content()
            else:
                _dialog_logic()

        def _dialog_logic():
            st.caption("Analizando actividad de las últimas 8 horas...")

            # -- CONFIGURACIÓN DE RANGO --
            with st.expander("🛠️ Configuración Avanzada / Rango Personalizado", expanded=False):
                col_d1, col_d2 = st.columns(2)
                
                # Valores por defecto: Últimas 8 horas
                default_end = datetime.now()
                default_start = default_end - timedelta(hours=8)
                
                with col_d1:
                    d_start = st.date_input("Fecha Inicio", value=default_start)
                    t_start = st.time_input("Hora Inicio", value=default_start.time())
                    
                with col_d2:
                    d_end = st.date_input("Fecha Fin", value=default_end)
                    t_end = st.time_input("Hora Fin", value=default_end.time())
                
                dt_start = datetime.combine(d_start, t_start)
                dt_end = datetime.combine(d_end, t_end)
                
                use_custom = st.checkbox("Usar rango personalizado", value=False)
                
                if st.button("🔄 Regenerar Informe", type="primary", use_container_width=True):
                    # Forzar regeneración
                    st.session_state["handoff_report_cache"] = None
                    st.rerun()

            # Cache simple para evitar regeneración al interactuar con widgets
            if "handoff_report_cache" not in st.session_state:
                st.session_state["handoff_report_cache"] = None

            report_content = st.session_state["handoff_report_cache"]

            if not report_content:
                with st.spinner("Consultando IA y generando informe..."):
                    from services.shift_service import get_shift_service
                    try:
                        svc = get_shift_service()
                        
                        if use_custom:
                            report = svc.generate_handoff_report(start_date=dt_start, end_date=dt_end)
                        else:
                            report = svc.generate_handoff_report(hours=8)
                        
                        st.session_state["handoff_report_cache"] = report
                        report_content = report
                    except Exception as e:
                        st.error(f"Error generando informe: {e}")
                        return

            if report_content:
                st.markdown(report_content)
                st.divider()
                st.download_button(
                    "📥 Descargar Informe (MD)",
                    data=report_content,
                    file_name=f"relevo_turno_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown",
                    type="primary"
                )
        _render()
    else:
        st.error("Esta funcionalidad requiere una versión más reciente de Streamlit.")
