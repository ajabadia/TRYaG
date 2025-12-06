import streamlit as st
from datetime import datetime

def show_handoff_dialog():
    """Muestra el diálogo de informe de relevo."""
    if hasattr(st, "dialog"):
        @st.dialog("📝 Informe de Relevo (Handoff)", width="large")
        def _render():
            st.caption("Analizando actividad de las últimas 8 horas...")
            
            # Botón para iniciar generación (para no hacerlo auto al abrir si es costoso, o auto?)
            # Auto es mejor UX para "Generar Relevo".
            
            # Usar session state para caché simple dentro del dialogo si se cierra/abre?
            # No, queremos fresco.
            
            with st.spinner("Consultando IA..."):
                from services.shift_service import get_shift_service
                try:
                    svc = get_shift_service()
                    report = svc.generate_handoff_report(hours=8)
                    
                    st.markdown(report)
                    st.divider()
                    st.download_button(
                        "📥 Descargar Informe (MD)",
                        data=report,
                        file_name=f"relevo_turno_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                        mime="text/markdown",
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Error generando informe: {e}")

        _render()
    else:
        st.error("Esta funcionalidad requiere una versión más reciente de Streamlit.")
