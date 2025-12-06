import sys
import os
import logging

# Add src to path
web_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(web_root)
sys.path.append(os.path.join(web_root, 'src'))

from fastapi.testclient import TestClient
from src.api.main import app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

client = TestClient(app)

def test_triage_analyze():
    logging.info("Testing POST /v1/core/analyze...")
    payload = {
        "motivo_consulta": "Dolor torácico opresivo",
        "edad": 55,
        "dolor": 8,
        "signos_vitales": {
            "sistolica": 160,
            "diastolica": 95,
            "frecuencia_cardiaca": 110,
            "saturacion": 98,
            "glasgow": 15
        }
    }
    
    response = client.post("/v1/core/analyze", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        logging.info(f"✅ Success! Response: {data}")
        # Verify logic from mock (dolor > 7 -> priority 3)
        if data['nivel_sugerido'] <= 3:
             logging.info("   Logic Verification: Correctly detected urgency based on pain.")
        else:
             logging.warning("   Logic Verification: Unexpected priority level.")
    else:
        logging.error(f"❌ Failed: {response.status_code} - {response.text}")

def test_risk_prediction():
    logging.info("\nTesting POST /v1/core/predict/risk...")
    payload = {
        "edad": 70,
        "signos_vitales": {
            "sistolica": 90,
            "frecuencia_cardiaca": 120,
            "saturacion": 92
        }
    }
    
    response = client.post("/v1/core/predict/risk", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        logging.info(f"✅ Success! Response: {data}")
        if data['risk_level'] in ['Medio', 'Alto']:
             logging.info("   Logic Verification: Correctly detected risk.")
    else:
        logging.error(f"❌ Failed: {response.status_code} - {response.text}")

def test_fhir_conversion():
    logging.info("\nTesting FHIR Transformation logic (Phase 12.4)...")
    from services.fhir_service import FHIRService
    
    mock_triage = {
        "patient_id": "TEST-123",
        "fecha_hora": "2023-10-10T10:00:00",
        "motivo_consulta": "Fiebre alta",
        "nivel_prioridad": 3,
        "datos_paciente": {
            "nombre": "Juan",
            "apellido1": "Perez",
            "genero": "Masculino",
            "identification_number": "12345678A"
        },
        "signos_vitales": {
            "temperatura": 39.5,
            "frecuencia_cardiaca": 100
        }
    }
    
    try:
        bundle = FHIRService.create_triage_bundle(mock_triage)
        if bundle['resourceType'] == 'Bundle':
            logging.info("✅ Success! FHIR Bundle created.")
            # Verify entries
            entries = bundle.get('entry', [])
            has_patient = any(e['resource']['resourceType'] == 'Patient' for e in entries)
            has_encounter = any(e['resource']['resourceType'] == 'Encounter' for e in entries)
            has_observation = any(e['resource']['resourceType'] == 'Observation' for e in entries)
            
            if has_patient and has_encounter and has_observation:
                logging.info(f"   Structure Verification: Found {len(entries)} resources (Patient, Encounter, Observation).")
            else:
                 logging.warning("   Structure Verification: Missing expected resources.")
        else:
             logging.error("❌ Failed: Result is not a Bundle.")
             
    except Exception as e:
        logging.error(f"❌ Critical Error in FHIR Service: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando Verificación de Fase 12.1 (API)...")
    try:
        test_triage_analyze()
        test_risk_prediction()
        test_fhir_conversion()
        print("\n✨ Verificación Completada.")
    except Exception as e:
        logging.error(f"Critical Error: {e}")
