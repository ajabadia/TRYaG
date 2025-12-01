import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.report_service import generate_triage_pdf
from datetime import datetime
import re

def test_generation():
    print("Testing PDF Generation...")
    
    # Data with special chars and emojis
    record = {
        "audit_id": "TEST_001",
        "timestamp": datetime.now(),
        "patient_data": {
            "nombre": "José María",
            "apellido1": "Nuñez",
            "apellido2": "García",
            "age": 45,
            "gender": "Masculino",
            "id_number": "12345678Z"
        },
        "vital_signs": {"fc": 80, "spo2": 98},
        "motivo_consulta": "Dolor en muñeca izquierda. 🤕", # Emoji
        "patient_background": {
            "allergies": [{"agent": "Penicilina"}],
            "pathologies": [{"name": "Hipertensión"}],
            "medications": "Paracetamol"
        },
        "triage_result": {
            "final_priority": 3,
            "final_color": "yellow",
            "wait_time": "60 min",
            "details": []
        },
        "destination": "Sala de Espera",
        "evaluator_id": "Dr. House"
    }

    try:
        pdf_bytes = generate_triage_pdf(record)
        print(f"✅ PDF Generated successfully. Size: {len(pdf_bytes)} bytes")
    except Exception as e:
        print(f"❌ PDF Generation FAILED: {e}")

    # Test filename sanitization
    print("\nTesting Filename Sanitization...")
    raw_name = f"{record['patient_data']['nombre']}_{record['patient_data']['apellido1']}"
    
    # Current logic
    safe_name_current = re.sub(r'[^\w\-_]', '_', raw_name)
    print(f"Current Safe Name: {safe_name_current}")
    
    # Proposed ASCII logic
    import unicodedata
    normalized = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('ASCII')
    safe_name_ascii = re.sub(r'[^\w\-_]', '_', normalized)
    print(f"ASCII Safe Name: {safe_name_ascii}")

if __name__ == "__main__":
    test_generation()
