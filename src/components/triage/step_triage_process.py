# path: src/components/triage/step_triage_process.py
# Creado: 2025-11-24
"""
Paso 3 del Asistente de Triaje: Proceso de Triaje.
Orquesta los sub-pasos: entrada de datos, análisis IA y validación humana.
"""
import streamlit as st
from .input_form import render_input_form
from .results_display import render_results_display
from .validation_form import render_validation_form


def render_step_triage_process() -> bool:
    """
    Renderiza el proceso completo de triaje con sus sub-pasos.
    
    Returns:
        bool: True si la validación está completa, False en caso contrario.
    """
    st.subheader("3️⃣ Realizar Triaje")
    
    # Verificar que hay paciente seleccionado
    p = st.session_state.get('triage_patient')
    if not p:
        st.warning("⚠️ No hay paciente seleccionado.")
        return False
    
    # Mostrar información del paciente (Unificada)
    from ui.components.common.patient_card import render_patient_header
    render_patient_header(p, st.session_state.get('resultado'))
    
    # --- HERRAMIENTAS (PDF) ---
    from services.report_service import generate_triage_pdf
    from utils.triage_utils import get_current_triage_record
    from datetime import datetime
    
    with st.expander("🛠️ Herramientas", expanded=False):
        record = get_current_triage_record()
        record["destination"] = "BORRADOR - EN PROCESO"
        pdf_bytes = generate_triage_pdf(record)
        
        # Sanitizar nombre de archivo de forma más agresiva (ASCII only)
        import re
        import unicodedata
        
        raw_name = f"{p.get('nombre', 'Paciente')}_{p.get('apellido1', '')}"
        # Normalizar a ASCII (quitar acentos)
        normalized = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('ASCII')
        # Solo permitir letras, números y guiones bajos
        safe_name = re.sub(r'[^\w\-_]', '_', normalized)
        
        file_name = f"Borrador_{safe_name}_{datetime.now().strftime('%H%M')}.pdf"
        
        st.download_button(
            label="📄 Descargar Borrador PDF",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/octet-stream",
            use_container_width=True,
            key="btn_download_draft_pdf"
        )
    
    st.divider()
    
    # Sub-paso 1: Entrada de datos (motivo, dolor, imágenes, audio)
    analysis_done = st.session_state.get('analysis_complete', False)
    validation_done = st.session_state.get('validation_complete', False)
    
    # Plegar entrada si ya hay análisis
    with st.expander("📝 **1. Entrada de Datos**", expanded=not analysis_done):
        render_input_form()
    
    st.divider()
    
    # Sub-paso 2: Resultados y sugerencias de la IA
    # Se muestra expandido si hay análisis pero aún no se ha calificado
    results_reviewed = st.session_state.get('calificacion_humana') is not None
    with st.expander("🤖 **2. Análisis y Sugerencias de IA**", expanded=analysis_done and not results_reviewed):
        render_results_display()
    
    st.divider()
    
    # Sub-paso 3: Validación humana
    # Se expande automáticamente SOLO si ya se ha calificado la IA
    with st.expander("✅ **3. Validación Humana**", expanded=results_reviewed):
        if results_reviewed:
            render_validation_form()
        else:
            st.info("Por favor, califique la respuesta de la IA en el paso anterior para continuar.")
    
    # Retornar si la validación está completa
    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/triage/step_triage_process.py</div>', unsafe_allow_html=True)
    return st.session_state.get('validation_complete', False)
