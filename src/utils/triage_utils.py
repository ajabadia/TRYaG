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
    if not resultado:
        resultado = {
            "final_priority": 0,
            "final_color": "gray",
            "wait_time": "N/A",
            "details": []
        }

    record = {
        "audit_id": st.session_state.get('current_audit_id', 'DRAFT'),
        "timestamp": st.session_state.get('triage_start_time', datetime.now()),
        "patient_data": p,
        "vital_signs": vital_signs,
        "motivo_consulta": datos_paciente.get('texto_medico', ''),
        "patient_background": background,
        "triage_result": resultado,
        "destination": "En proceso...",
        "evaluator_id": st.session_state.get('username', 'Sistema')
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
