import streamlit as st
from datetime import datetime

def get_current_triage_record():
    """
    Construye un registro de triaje (dict) a partir del estado actual de la sesión.
    Útil para generar informes preliminares o finales.
    """
    p = st.session_state.get('triage_patient', {})
    datos_paciente = st.session_state.get('datos_paciente', {})
    
    # Asegurar que vital_signs es un dict
    vital_signs = datos_paciente.get('vital_signs', {})
    if not isinstance(vital_signs, dict):
        vital_signs = {}

    # Construir antecedentes
    background = {
        "allergies": datos_paciente.get('alergias', []),
        "pathologies": datos_paciente.get('patologias', []),
        "medications": datos_paciente.get('medicacion', '')
    }
    
    # Resultado (puede ser None si es borrador)
    resultado = st.session_state.get('resultado', {})
    
    # Adaptar estructura de resultado para report_service (ia_result)
    # report_service espera: ia_result -> nivel -> {text, color}
    ia_result = {}
    if resultado:
        ia_result = {
            "nivel": {
                "text": resultado.get('nivel_texto', 'PENDIENTE'),
                "color": resultado.get('nivel_color', 'gray')
            },
            "wait_time": resultado.get('tiempo_espera', 'N/A'),
            "razones": resultado.get('razonamiento', [])
        }
    else:
        ia_result = {
            "nivel": {"text": "PENDIENTE", "color": "gray"},
            "wait_time": "N/A",
            "razones": []
        }

    # Construir registro base
    record = {
        "audit_id": st.session_state.get('current_audit_id', 'DRAFT'),
        "timestamp": st.session_state.get('triage_start_time', datetime.now()),
        # Flatten patient data for report_service (is_draft=True mode)
        "nombre": p.get('nombre', ''),
        "apellido1": p.get('apellido1', ''),
        "edad": p.get('edad', ''),
        "gender": p.get('sexo', ''),
        "patient_id": p.get('patient_code', 'UNKNOWN'),
        
        "vital_signs": vital_signs,
        "motivo_consulta": datos_paciente.get('texto_medico', ''),
        "guided_interview_summary": datos_paciente.get('guided_interview', ''), # Assuming key
        
        # HDA fields (flattened)
        "hda_aparicion": datos_paciente.get('hda', {}).get('aparicion', ''),
        "hda_localizacion": datos_paciente.get('hda', {}).get('localizacion', ''),
        "hda_intensidad": datos_paciente.get('hda', {}).get('intensidad', ''),
        "hda_caracteristicas": datos_paciente.get('hda', {}).get('caracteristicas', ''),
        "hda_irradiacion": datos_paciente.get('hda', {}).get('irradiacion', ''),
        "hda_alivio": datos_paciente.get('hda', {}).get('alivio', ''),
        "hda_sintomas_asoc": datos_paciente.get('hda', {}).get('sintomas_asoc', ''),

        "patient_background": background, # This might need to be flattened too or report_service updated
        # report_service uses: alergias_info_completa, antecedentes, historia_integral
        "alergias": ", ".join(background['allergies']) if isinstance(background['allergies'], list) else str(background['allergies']),
        "antecedentes": ", ".join(background['pathologies']) if isinstance(background['pathologies'], list) else str(background['pathologies']),
        
        "ia_result": ia_result,
        "recommendations": st.session_state.get('recommendations', []),
        
        "destination": "En proceso...",
        "evaluator_id": st.session_state.get('username', 'Sistema'),
        "status": "BORRADOR"
    }
    
    return record

def get_triage_record_for_pdf(patient_code: str) -> dict:
    """
    Recupera el registro de triaje de la BD y lo formatea para el generador de PDF.
    """
    from db.repositories.triage import get_triage_repository
    repo = get_triage_repository()
    
    # Buscar el último triaje
    db_record = repo.get_latest_by_patient_id(patient_code)
    
    if not db_record:
        return None
        
    # Mapear campos de BD a estructura esperada por report_service
    # La estructura en BD (TriageRecord) es ligeramente distinta a la de sesión
    
    # Extraer datos del paciente del snapshot o buscar en BD si es necesario
    # Aquí asumimos que db_record tiene lo necesario o lo reconstruimos
    
    # Reconstruir estructura
    record = {
        "audit_id": db_record.get('audit_id', 'N/A'),
        "timestamp": db_record.get('timestamp', datetime.now()),
        "patient_data": {
            # Intentar sacar datos del paciente si están en el record, 
            # si no, habría que pasarlos o buscarlos. 
            # Por ahora usaremos placeholders si no están en el snapshot.
            "nombre": "Paciente", # Esto debería venir del contexto de llamada si no está en record
            "patient_code": patient_code
        },
        "vital_signs": db_record.get('vital_signs', {}),
        "motivo_consulta": db_record.get('sugerencia_ia', {}).get('analysis', {}).get('reason', 'No disponible'),
        "patient_background": {
            # Si guardamos antecedentes en el record, usarlos. Si no, vacíos.
            # TriageRecord tiene 'sintomas_detectados' pero no background estructurado completo a veces.
            "allergies": [], 
            "pathologies": [],
            "medications": ""
        },
        "triage_result": {
            "final_priority": db_record.get('nivel_final') or db_record.get('nivel_sugerido'),
            "final_color": db_record.get('color_final') or db_record.get('color_sugerido'),
            "wait_time": "N/A", # Calcular si es posible
            "details": []
        },
        "destination": "N/A", # No siempre se guarda el destino final en el record de triaje mismo, sino en el flujo
        "evaluator_id": db_record.get('evaluator_id', 'Sistema')
    }
    
    # Intentar enriquecer con datos reales si están disponibles en el objeto
    if 'patient_snapshot' in db_record:
        record['patient_data'] = db_record['patient_snapshot']
        
    return record
