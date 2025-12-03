import streamlit as st
from datetime import datetime
import re
import unicodedata
from services.report_service import generate_triage_pdf

@st.dialog("📄 Informe Clínico Detallado", width="large")
def render_report_viewer(record: dict, patient: dict):
    """
    Módulo independiente para visualizar el informe clínico completo antes de generar el PDF.
    Muestra todos los valores detallados y permite la descarga.
    """
    st.caption("Revise los datos detallados del paciente y del triaje.")

    # Tabs para organizar la información
    tab_datos, tab_clinica, tab_triaje, tab_pdf = st.tabs([
        "👤 Datos Paciente", 
        "🏥 Historia Clínica", 
        "🚑 Triaje y Signos", 
        "🖨️ Generar PDF"
    ])

    with tab_datos:
        st.markdown("### Datos Demográficos y Administrativos")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nombre Completo", value=patient.get('nombre_completo', 'N/A'), disabled=True)
            st.text_input("ID Paciente", value=patient.get('patient_code', 'N/A'), disabled=True)
            st.text_input("Fecha Nacimiento", value=str(patient.get('fecha_nacimiento', 'N/A')), disabled=True)
        with c2:
            st.text_input("Edad", value=str(patient.get('edad', 'N/A')), disabled=True)
            st.text_input("Género", value=patient.get('gender', 'N/A'), disabled=True)
            st.text_input("Seguro", value=patient.get('insurance_info', {}).get('insurer_name', 'N/A'), disabled=True)

    with tab_clinica:
        st.markdown("### Historia Clínica Integral")
        
        # Motivo
        st.info(f"**Motivo de Consulta:** {record.get('motivo_consulta', 'No disponible')}")
        
        # Antecedentes (Expandido)
        bg = record.get('patient_background', {})
        
        with st.expander("Antecedentes Personales y Alergias", expanded=True):
            if bg.get('allergies'):
                st.write("**Alergias:**")
                for a in bg.get('allergies', []):
                    st.markdown(f"- {a.get('agent')} ({a.get('reaction', 'Sin detalles')})")
            else:
                st.markdown("*Sin alergias registradas*")
                
            if bg.get('pathologies'):
                st.write("**Patologías:**")
                for p in bg.get('pathologies', []):
                    st.markdown(f"- {p.get('name')} ({p.get('status', '')})")
            else:
                st.markdown("*Sin patologías registradas*")
                
            st.text_area("Medicación Habitual", value=bg.get('medications', ''), disabled=True)

        # Historia Extendida (Recuperando campos planos del paciente si no están en record estructurado)
        # Nota: En un caso real, esto debería venir estructurado en 'record', pero por ahora lo sacamos de 'patient'
        # que se pasa como argumento y suele tener los datos de session_state.
        with st.expander("Historia Extendida (Detalles)", expanded=False):
            ext_fields = [
                ("Antecedentes Familiares", "ant_familiares"),
                ("Psiquiatría", "ant_psiquiatricos"),
                ("Quirúrgicos", "ant_quirurgicos"),
                ("Hábitos Tóxicos", "habitos_toxicos"),
                ("Nutrición", "nutricion_dieta"),
                ("Viajes/Exposición", "viajes_recientes"),
                ("Sensorial", "sensorial_ayudas"),
                ("Dolor Crónico", "dolor_cronico"),
                ("Hospitalizaciones", "hospitalizaciones_previas"),
                ("Situación Legal", "situacion_legal")
            ]
            
            for label, key in ext_fields:
                val = patient.get(key)
                if val:
                    if isinstance(val, list):
                        val = ", ".join([str(v) for v in val])
                    st.markdown(f"**{label}:** {val}")

    with tab_triaje:
        st.markdown("### Signos Vitales y Clasificación")
        
        # Signos Vitales
        vitals = record.get('vital_signs', {})
        if vitals:
            cols = st.columns(3)
            for i, (k, v) in enumerate(vitals.items()):
                if k == 'notas': continue
                with cols[i % 3]:
                    st.metric(k.upper(), str(v))
        else:
            st.warning("No hay signos vitales registrados.")
            
        st.divider()
        
        # Resultado Triaje
        res = record.get('triage_result', {})
        level = res.get('final_priority')
        color = res.get('final_color', 'gray') or 'gray' # Safety fallback
        
        c_res, c_det = st.columns([1, 2])
        with c_res:
            st.markdown(f"""
            <div style="background-color: {color}; color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h1>NIVEL {level}</h1>
                <p>{res.get('wait_time', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with c_det:
            st.write("**Detalles del Análisis:**")
            for det in res.get('details', []):
                st.markdown(f"- **{det.get('metric', 'Gral').upper()}**: {det.get('label', '')}")
            
            st.write(f"**Destino:** {record.get('destination', 'Pendiente')}")
            st.write(f"**Evaluador:** {record.get('evaluator_id', 'Sistema')}")

    with tab_pdf:
        st.markdown("### Generación de Documento")
        st.info("Pulse el botón para generar el PDF oficial. Esta acción puede tardar unos segundos.")
        
        if st.button("🖨️ Generar PDF Ahora", type="primary", use_container_width=True):
            try:
                # Preparar record final
                record['patient_data'].update(patient)
                
                # Generar
                pdf_bytes = generate_triage_pdf(record)
                
                # Nombre archivo
                raw_name = f"{patient.get('nombre', 'Paciente')}_{patient.get('apellido1', '')}"
                normalized = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('ASCII')
                safe_name = re.sub(r'[^\w\-_]', '_', normalized)
                file_name = f"Informe_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                
                st.success("PDF Generado Correctamente")
                
                st.download_button(
                    label="⬇️ Descargar Archivo PDF",
                    data=pdf_bytes,
                    file_name=file_name,
                    mime="application/pdf",
                    type="secondary",
                    icon="📥",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Error al generar el PDF: {str(e)}")
                st.exception(e)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 15px; border-top: 1px solid #eee; padding-top: 5px;">src/ui/components/reports/report_viewer.py</div>', unsafe_allow_html=True)
