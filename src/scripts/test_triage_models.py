# path: scripts/test_triage_models.py
import sys
import os
from datetime import datetime

# Añadir el directorio raíz al path para poder importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.models import TriageRecord, VitalSigns, TriageRangeConfig
from src.db.repositories.triage import get_triage_repository
from src.db.repositories.triage_config import get_triage_config_repository

def test_triage_record():
    print("--- Testing TriageRecord ---")
    repo = get_triage_repository()
    
    # Crear signos vitales
    vitals = VitalSigns(
        fc=80,
        pas=120,
        pad=80,
        spo2=98,
        temp=36.5,
        fr=16,
        gcs=15,
        eva=2,
        pupilas="Normal",
        oxigeno_suplementario=False,
        notas="Paciente tranquilo"
    )
    
    # Crear registro de triaje
    audit_id = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    record = TriageRecord(
        audit_id=audit_id,
        sugerencia_ia={"nivel": 4, "razon": "Estable"},
        vital_signs=vitals,
        nivel_sugerido=4,
        color_sugerido="Verde",
        nivel_final=4,
        color_final="Verde",
        motivo_urgencia="Sin riesgo vital",
        evaluator_id="admin_test"
    )
    
    # Guardar
    print(f"Saving record with audit_id: {audit_id}")
    doc_id = repo.create(record.model_dump(by_alias=True))
    print(f"Saved with ID: {doc_id}")
    
    # Recuperar
    retrieved = repo.get_by_audit_id(audit_id)
    if retrieved:
        print("Record retrieved successfully.")
        print(f"Vital Signs: {retrieved.get('vital_signs')}")
        
        # Verificar que se puede parsear de nuevo al modelo
        parsed = TriageRecord(**retrieved)
        print(f"Parsed back to model: OK. FC={parsed.vital_signs.fc}")
    else:
        print("ERROR: Record not found.")

def test_triage_config():
    print("\n--- Testing TriageRangeConfig ---")
    repo = get_triage_config_repository()
    
    # Crear configuración para FC
    config = TriageRangeConfig(
        metric="fc",
        red_min=0, red_max=40,
        orange_min=40, orange_max=50,
        yellow_min=50, yellow_max=60,
        green_min=60, green_max=100
        # ... y así sucesivamente
    )
    
    # Guardar
    print("Saving FC config...")
    success = repo.save_config(config.model_dump())
    if success:
        print("Config saved successfully.")
    else:
        print("ERROR: Failed to save config.")
        
    # Recuperar
    retrieved = repo.get_by_metric("fc")
    if retrieved:
        print("Config retrieved successfully.")
        print(f"Metric: {retrieved.get('metric')}")
        print(f"Green Max: {retrieved.get('green_max')}")
    else:
        print("ERROR: Config not found.")

if __name__ == "__main__":
    try:
        test_triage_record()
        test_triage_config()
        print("\nAll tests completed.")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
