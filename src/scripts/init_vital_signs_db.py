# path: src/scripts/init_vital_signs_db.py
# Script para inicializar la base de datos de signos vitales con rangos estándar (Manchester)
import sys
import os

# Añadir root al path para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from db.repositories.vital_signs_repo import VitalSignsRepository
from db.models import VitalSignReference, VitalSignAgeConfig, VitalSignSeverityRange

def init_vital_signs():
    repo = VitalSignsRepository()
    
    print("🚀 Inicializando base de datos de signos vitales (REINICIO COMPLETO)...")
    
    # Limpiar colección existente para asegurar datos limpios
    repo.collection.delete_many({}) 
    # if repo.get_all_references():
    #     print("⚠️ Ya existen configuraciones de signos vitales. Saltando inicialización.")
    #     return

    # --- 1. Frecuencia Cardíaca (FC) ---
    fc_adulto = VitalSignAgeConfig(
        min_age=12, max_age=120,
        val_min=0, val_max=300,
        normal_min=60, normal_max=100,
        default_value=80,
        ranges=[
            VitalSignSeverityRange(min_val=0, max_val=39, color="red", priority=3, label="Bradicardia Extrema"),
            VitalSignSeverityRange(min_val=40, max_val=49, color="orange", priority=2, label="Bradicardia Severa"),
            VitalSignSeverityRange(min_val=50, max_val=59, color="yellow", priority=1, label="Bradicardia Leve"),
            VitalSignSeverityRange(min_val=60, max_val=100, color="green", priority=0, label="Normal"),
            VitalSignSeverityRange(min_val=101, max_val=120, color="yellow", priority=1, label="Taquicardia Leve"),
            VitalSignSeverityRange(min_val=121, max_val=140, color="orange", priority=2, label="Taquicardia Severa"),
            VitalSignSeverityRange(min_val=141, max_val=300, color="red", priority=3, label="Taquicardia Extrema"),
        ]
    )
    
    fc_ref = VitalSignReference(name="Frecuencia Cardíaca", key="fc", unit="ppm", configs=[fc_adulto])
    data = fc_ref.model_dump(by_alias=True)
    if data.get("_id") is None: del data["_id"]
    repo.create(data)
    print("✅ FC creada.")

    # --- 2. Saturación O2 (SpO2) ---
    spo2_adulto = VitalSignAgeConfig(
        min_age=0, max_age=120,
        val_min=0, val_max=100,
        normal_min=95, normal_max=100,
        default_value=98,
        ranges=[
            VitalSignSeverityRange(min_val=0, max_val=89, color="red", priority=3, label="Hipoxia Crítica"),
            VitalSignSeverityRange(min_val=90, max_val=94, color="orange", priority=2, label="Hipoxia Moderada"),
            VitalSignSeverityRange(min_val=95, max_val=100, color="green", priority=0, label="Normal"),
        ]
    )
    spo2_ref = VitalSignReference(name="Saturación O2", key="spo2", unit="%", configs=[spo2_adulto])
    data = spo2_ref.model_dump(by_alias=True)
    if data.get("_id") is None: del data["_id"]
    repo.create(data)
    print("✅ SpO2 creada.")

    # --- 3. Temperatura (Temp) ---
    temp_adulto = VitalSignAgeConfig(
        min_age=0, max_age=120,
        val_min=20, val_max=45,
        normal_min=36.0, normal_max=37.5,
        default_value=36.5,
        ranges=[
            VitalSignSeverityRange(min_val=0, max_val=34.9, color="orange", priority=2, label="Hipotermia"),
            VitalSignSeverityRange(min_val=35.0, max_val=35.9, color="yellow", priority=1, label="Hipotermia Leve"),
            VitalSignSeverityRange(min_val=36.0, max_val=37.5, color="green", priority=0, label="Afebril"),
            VitalSignSeverityRange(min_val=37.6, max_val=38.4, color="yellow", priority=1, label="Febrícula"),
            VitalSignSeverityRange(min_val=38.5, max_val=40.0, color="orange", priority=2, label="Fiebre Alta"),
            VitalSignSeverityRange(min_val=40.1, max_val=50.0, color="red", priority=3, label="Hiperpirexia"),
        ]
    )
    temp_ref = VitalSignReference(name="Temperatura", key="temp", unit="°C", configs=[temp_adulto])
    data = temp_ref.model_dump(by_alias=True)
    if data.get("_id") is None: del data["_id"]
    repo.create(data)
    print("✅ Temperatura creada.")

    # --- 4. Presión Sistólica (PAS) ---
    pas_adulto = VitalSignAgeConfig(
        min_age=12, max_age=120,
        val_min=0, val_max=300,
        normal_min=100, normal_max=140,
        default_value=120,
        ranges=[
            VitalSignSeverityRange(min_val=0, max_val=79, color="red", priority=3, label="Hipotensión Severa"),
            VitalSignSeverityRange(min_val=80, max_val=99, color="orange", priority=2, label="Hipotensión"),
            VitalSignSeverityRange(min_val=100, max_val=140, color="green", priority=0, label="Normal"),
            VitalSignSeverityRange(min_val=141, max_val=160, color="yellow", priority=1, label="Hipertensión Leve"),
            VitalSignSeverityRange(min_val=161, max_val=200, color="orange", priority=2, label="Hipertensión Moderada"),
            VitalSignSeverityRange(min_val=201, max_val=300, color="red", priority=3, label="Crisis Hipertensiva"),
        ]
    )
    pas_ref = VitalSignReference(name="Presión Sistólica", key="pas", unit="mmHg", configs=[pas_adulto])
    data = pas_ref.model_dump(by_alias=True)
    if data.get("_id") is None: del data["_id"]
    repo.create(data)
    print("✅ PAS creada.")

    # --- 5. Presión Diastólica (PAD) ---
    pad_adulto = VitalSignAgeConfig(
        min_age=12, max_age=120,
        val_min=0, val_max=200,
        normal_min=60, normal_max=90,
        default_value=80,
        ranges=[
            VitalSignSeverityRange(min_val=0, max_val=130, color="green", priority=0, label="Normal/Baja"), # Simplificado
            VitalSignSeverityRange(min_val=131, max_val=200, color="red", priority=3, label="Hipertensión Diastólica Severa"),
        ]
    )
    pad_ref = VitalSignReference(name="Presión Diastólica", key="pad", unit="mmHg", configs=[pad_adulto])
    data = pad_ref.model_dump(by_alias=True)
    if data.get("_id") is None: del data["_id"]
    repo.create(data)
    print("✅ PAD creada.")

    # --- 6. Frecuencia Respiratoria (FR) ---
    fr_adulto = VitalSignAgeConfig(
        min_age=12, max_age=120,
        val_min=0, val_max=100,
        normal_min=12, normal_max=20,
        default_value=16,
        ranges=[
            VitalSignSeverityRange(min_val=0, max_val=8, color="red", priority=3, label="Bradipnea Extrema"),
            VitalSignSeverityRange(min_val=9, max_val=11, color="orange", priority=2, label="Bradipnea"),
            VitalSignSeverityRange(min_val=12, max_val=20, color="green", priority=0, label="Normal"),
            VitalSignSeverityRange(min_val=21, max_val=24, color="yellow", priority=1, label="Taquipnea Leve"),
            VitalSignSeverityRange(min_val=25, max_val=29, color="orange", priority=2, label="Taquipnea Moderada"),
            VitalSignSeverityRange(min_val=30, max_val=100, color="red", priority=3, label="Taquipnea Severa"),
        ]
    )
    fr_ref = VitalSignReference(name="Frecuencia Respiratoria", key="fr", unit="rpm", configs=[fr_adulto])
    data = fr_ref.model_dump(by_alias=True)
    if data.get("_id") is None: del data["_id"]
    repo.create(data)
    print("✅ FR creada.")

    # --- 7. Glasgow (GCS) ---
    gcs_adulto = VitalSignAgeConfig(
        min_age=0, max_age=120,
        val_min=3, val_max=15,
        normal_min=15, normal_max=15,
        default_value=15,
        ranges=[
            VitalSignSeverityRange(min_val=3, max_val=8, color="red", priority=3, label="Coma (Grave)"),
            VitalSignSeverityRange(min_val=9, max_val=12, color="orange", priority=2, label="Moderado"),
            VitalSignSeverityRange(min_val=13, max_val=14, color="yellow", priority=1, label="Leve"),
            VitalSignSeverityRange(min_val=15, max_val=15, color="green", priority=0, label="Consciente"),
        ]
    )
    gcs_ref = VitalSignReference(name="Glasgow", key="gcs", unit="pts", configs=[gcs_adulto])
    data = gcs_ref.model_dump(by_alias=True)
    if data.get("_id") is None: del data["_id"]
    repo.create(data)
    print("✅ GCS creada.")

    # --- 8. Dolor (EVA) ---
    eva_adulto = VitalSignAgeConfig(
        min_age=0, max_age=120,
        val_min=0, val_max=10,
        normal_min=0, normal_max=3,
        default_value=0,
        ranges=[
            VitalSignSeverityRange(min_val=0, max_val=3, color="green", priority=0, label="Leve"),
            VitalSignSeverityRange(min_val=4, max_val=6, color="yellow", priority=1, label="Moderado"),
            VitalSignSeverityRange(min_val=7, max_val=8, color="orange", priority=2, label="Severo"),
            VitalSignSeverityRange(min_val=9, max_val=10, color="red", priority=3, label="Insoportable"),
        ]
    )
    eva_ref = VitalSignReference(name="Escala Dolor", key="eva", unit="EVA", configs=[eva_adulto])
    data = eva_ref.model_dump(by_alias=True)
    if data.get("_id") is None: del data["_id"]
    repo.create(data)
    print("✅ EVA creada.")

    print("🎉 Inicialización completada.")

if __name__ == "__main__":
    init_vital_signs()
