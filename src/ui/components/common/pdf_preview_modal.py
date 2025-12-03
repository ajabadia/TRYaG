import streamlit as st
from datetime import datetime
from services.report_service import generate_triage_pdf
import re
import unicodedata

# dismissible=False evita cierre accidental (Streamlit 1.34+)
@st.dialog("Vista Previa del Informe")
def show_pdf_preview_modal(record: dict, patient: dict):
    """
    Muestra una modal con los datos que irán al PDF y el botón de descarga.
    """
    st.caption("Revise los datos antes de generar el documento.")
    
    # 1. Datos del Paciente
    st.subheader("👤 Datos del Paciente")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Nombre:** {patient.get('nombre_completo', 'N/A')}")
        st.markdown(f"**ID:** {patient.get('patient_code', 'N/A')}")
    with c2:
        st.markdown(f"**Edad:** {patient.get('edad', 'N/A')}")
        st.markdown(f"**Género:** {patient.get('gender', 'N/A')}")
        
    st.divider()
    
    # 2. Datos Clínicos
    st.subheader("🏥 Datos Clínicos")
    
    # Motivo
    st.markdown("**Motivo de Consulta:**")
    st.info(record.get('motivo_consulta', 'No disponible'))
    
    # Signos Vitales
    st.markdown("**Signos Vitales:**")
    vitals = record.get('vital_signs', {})
    if vitals:
        cols = st.columns(4)
        metrics = [
            ("FC", vitals.get('fc'), "bpm"),
            ("SpO2", vitals.get('spo2'), "%"),
            ("TA", f"{vitals.get('pas')}/{vitals.get('pad')}" if vitals.get('pas') else None, "mmHg"),
            ("Temp", vitals.get('temp'), "°C")
        ]
        for i, (label, val, unit) in enumerate(metrics):
            with cols[i]:
                if val:
                    st.metric(label, f"{val} {unit}")
                else:
                    st.markdown(f"**{label}:** -")
    else:
        st.caption("No registrados")
        
    # Antecedentes
    st.markdown("**Antecedentes:**")
    bg = record.get('patient_background', {})
    if bg and (bg.get('allergies') or bg.get('pathologies')):
        if bg.get('allergies'):
            st.markdown(f"**Alergias:** {', '.join([a.get('agent','') for a in bg.get('allergies', [])])}")
        if bg.get('pathologies'):
            st.markdown(f"**Patologías:** {', '.join([p.get('name','') for p in bg.get('pathologies', [])])}")
    else:
        st.caption("No registrados")

    st.divider()

    # 3. Resultado Triaje
    st.subheader("🚑 Clasificación")
    level = record.get('triage_result', {}).get('final_priority')
    color = record.get('triage_result', {}).get('final_color', 'grey')
    
    if level:
        st.markdown(
            f"""
            <div style="background-color: {color}; color: white; padding: 10px; border-radius: 5px; text-align: center;">
                <h3>NIVEL {level}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("Pendiente de clasificación")

    st.divider()
    
    # 4. Generación
    col_gen, col_close = st.columns([2, 1])
    
    with col_gen:
        # Generar PDF en memoria
        # Nota: En st.dialog, el download_button funciona, pero a veces cierra el diálogo.
        # Es mejor generar los bytes aquí mismo.
        
        # Preparar record final con datos actualizados del paciente si hace falta
        record['patient_data'].update(patient)
        
        try:
            pdf_bytes = generate_triage_pdf(record)
            
            # Sanitizar nombre
            raw_name = f"{patient.get('nombre', 'Paciente')}_{patient.get('apellido1', '')}"
            normalized = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('ASCII')
            safe_name = re.sub(r'[^\w\-_]', '_', normalized)
            file_name = f"Informe_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            st.download_button(
                label="⬇️ Generar y Descargar PDF",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generando PDF: {e}")
            
    with col_close:
        if st.button("Cerrar", use_container_width=True):
            st.rerun()
