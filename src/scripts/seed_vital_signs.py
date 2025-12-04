# path: scripts/seed_vital_signs.py
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.repositories.vital_signs_repo import VitalSignsRepository
from src.db.models import VitalSignReference, VitalSignAgeConfig

def seed_vital_signs():
    repo = VitalSignsRepository()
    
    # Datos iniciales (Adultos Estándar y algunos pediátricos básicos)
    # Rangos basados en valores clínicos generales
    
    data = [
        {
            "name": "Frecuencia Cardíaca",
            "key": "fc",
            "unit": "ppm",
            "configs": [
                {
                    "min_age": 12, "max_age": 120,
                    "val_min": 0, "val_max": 300,
                    "normal_min": 60, "normal_max": 100,
                    "default_value": 80,
                    "ranges": [
                        {"min_val": 60, "max_val": 100, "color": "green", "priority": 0, "label": "Normal"},
                        {"min_val": 50, "max_val": 59, "color": "yellow", "priority": 1, "label": "Bradicardia Leve"},
                        {"min_val": 101, "max_val": 120, "color": "yellow", "priority": 1, "label": "Taquicardia Leve"},
                        {"min_val": 40, "max_val": 49, "color": "orange", "priority": 2, "label": "Bradicardia Moderada"},
                        {"min_val": 121, "max_val": 140, "color": "orange", "priority": 2, "label": "Taquicardia Moderada"},
                        {"min_val": 0, "max_val": 39, "color": "red", "priority": 3, "label": "Bradicardia Severa / Parada"},
                        {"min_val": 141, "max_val": 300, "color": "red", "priority": 3, "label": "Taquicardia Severa"}
                    ]
                }
            ]
        },
        {
            "name": "Presión Arterial Sistólica",
            "key": "pas",
            "unit": "mmHg",
            "configs": [
                {
                    "min_age": 12, "max_age": 120,
                    "val_min": 0, "val_max": 300,
                    "normal_min": 100, "normal_max": 129,
                    "default_value": 120,
                    "ranges": [
                        {"min_val": 100, "max_val": 129, "color": "green", "priority": 0, "label": "Normal"},
                        {"min_val": 90, "max_val": 99, "color": "yellow", "priority": 1, "label": "Hipotensión Leve"},
                        {"min_val": 130, "max_val": 159, "color": "yellow", "priority": 1, "label": "Hipertensión Moderada"},
                        {"min_val": 80, "max_val": 89, "color": "orange", "priority": 2, "label": "Hipotensión Moderada"},
                        {"min_val": 160, "max_val": 179, "color": "orange", "priority": 2, "label": "Hipertensión Severa"},
                        {"min_val": 0, "max_val": 79, "color": "red", "priority": 3, "label": "Hipotensión Crítica"},
                        {"min_val": 180, "max_val": 300, "color": "red", "priority": 3, "label": "Crisis Hipertensiva"}
                    ]
                }
            ]
        },
        {
            "name": "Presión Arterial Diastólica",
            "key": "pad",
            "unit": "mmHg",
            "configs": [
                {
                    "min_age": 12, "max_age": 120,
                    "val_min": 0, "val_max": 300,
                    "normal_min": 60, "normal_max": 85,
                    "default_value": 80,
                    "ranges": [
                        {"min_val": 60, "max_val": 85, "color": "green", "priority": 0, "label": "Normal"},
                        {"min_val": 50, "max_val": 59, "color": "yellow", "priority": 1, "label": "Hipotensión Leve"},
                        {"min_val": 86, "max_val": 105, "color": "yellow", "priority": 1, "label": "Hipertensión Leve"},
                        {"min_val": 40, "max_val": 49, "color": "orange", "priority": 2, "label": "Hipotensión Moderada"},
                        {"min_val": 106, "max_val": 120, "color": "orange", "priority": 2, "label": "Hipertensión Moderada"},
                        {"min_val": 0, "max_val": 39, "color": "red", "priority": 3, "label": "Hipotensión Severa"},
                        {"min_val": 121, "max_val": 300, "color": "red", "priority": 3, "label": "Hipertensión Severa"}
                    ]
                }
            ]
        },
        {
            "name": "Saturación de Oxígeno",
            "key": "spo2",
            "unit": "%",
            "configs": [
                {
                    "min_age": 0, "max_age": 120,
                    "val_min": 0, "val_max": 100,
                    "normal_min": 95, "normal_max": 100,
                    "default_value": 98,
                    "ranges": [
                        {"min_val": 95, "max_val": 100, "color": "green", "priority": 0, "label": "Normal"},
                        {"min_val": 93, "max_val": 94, "color": "yellow", "priority": 1, "label": "Hipoxemia Leve"},
                        {"min_val": 90, "max_val": 92, "color": "orange", "priority": 2, "label": "Hipoxemia Moderada"},
                        {"min_val": 0, "max_val": 89, "color": "red", "priority": 3, "label": "Hipoxemia Severa"}
                    ]
                }
            ]
        },
        {
            "name": "Temperatura",
            "key": "temp",
            "unit": "°C",
            "configs": [
                {
                    "min_age": 0, "max_age": 120,
                    "val_min": 25, "val_max": 45,
                    "normal_min": 36.5, "normal_max": 37.5,
                    "default_value": 37.0,
                    "ranges": [
                        {"min_val": 36.5, "max_val": 37.5, "color": "green", "priority": 0, "label": "Normal"},
                        {"min_val": 35.0, "max_val": 36.4, "color": "yellow", "priority": 1, "label": "Hipotermia Leve"},
                        {"min_val": 37.6, "max_val": 37.9, "color": "yellow", "priority": 1, "label": "Febrícula"},
                        {"min_val": 0, "max_val": 34.9, "color": "orange", "priority": 2, "label": "Hipotermia Moderada"}, # User said < 35 is Orange/Red, clarified in table <35 is Orange, <34 is Red? Table says <35 is Orange/Red. Let's follow table: <35.0 Orange, <34.0 Red.
                        {"min_val": 38.0, "max_val": 39.9, "color": "orange", "priority": 2, "label": "Fiebre"},
                        {"min_val": 40.0, "max_val": 45.0, "color": "red", "priority": 3, "label": "Hipertermia"},
                        {"min_val": 0, "max_val": 33.9, "color": "red", "priority": 3, "label": "Hipotermia Severa"} # Assuming <34 based on table logic gap
                    ]
                }
            ]
        },
        {
            "name": "Frecuencia Respiratoria",
            "key": "fr",
            "unit": "rpm",
            "configs": [
                {
                    "min_age": 12, "max_age": 120,
                    "val_min": 0, "val_max": 100,
                    "normal_min": 12, "normal_max": 20,
                    "default_value": 16,
                    "ranges": [
                        {"min_val": 12, "max_val": 20, "color": "green", "priority": 0, "label": "Normal"},
                        {"min_val": 8, "max_val": 11, "color": "yellow", "priority": 1, "label": "Bradipnea Leve"},
                        {"min_val": 21, "max_val": 24, "color": "yellow", "priority": 1, "label": "Taquipnea Leve"},
                        {"min_val": 6, "max_val": 7, "color": "orange", "priority": 2, "label": "Bradipnea Moderada"},
                        {"min_val": 25, "max_val": 29, "color": "orange", "priority": 2, "label": "Taquipnea Moderada"},
                        {"min_val": 0, "max_val": 5, "color": "red", "priority": 3, "label": "Fallo Respiratorio"},
                        {"min_val": 30, "max_val": 100, "color": "red", "priority": 3, "label": "Taquipnea Severa"}
                    ]
                }
            ]
        },
        {
            "name": "Escala de Glasgow",
            "key": "gcs",
            "unit": "pts",
            "configs": [
                {
                    "min_age": 0, "max_age": 120,
                    "val_min": 3, "val_max": 15,
                    "normal_min": 15, "normal_max": 15,
                    "default_value": 15,
                    "ranges": [
                        {"min_val": 15, "max_val": 15, "color": "green", "priority": 0, "label": "Consciente"},
                        {"min_val": 13, "max_val": 14, "color": "yellow", "priority": 1, "label": "Alteración Leve"},
                        {"min_val": 9, "max_val": 12, "color": "orange", "priority": 2, "label": "Alteración Moderada"},
                        {"min_val": 3, "max_val": 8, "color": "red", "priority": 3, "label": "Coma / Trauma Grave"}
                    ]
                }
            ]
        },
        {
            "name": "Escala de Dolor (EVA)",
            "key": "eva",
            "unit": "pts",
            "configs": [
                {
                    "min_age": 0, "max_age": 120,
                    "val_min": 0, "val_max": 10,
                    "normal_min": 0, "normal_max": 3,
                    "default_value": 0,
                    "ranges": [
                        {"min_val": 0, "max_val": 3, "color": "green", "priority": 0, "label": "Leve"},
                        {"min_val": 4, "max_val": 6, "color": "yellow", "priority": 1, "label": "Moderado"},
                        {"min_val": 7, "max_val": 8, "color": "orange", "priority": 2, "label": "Severo"},
                        {"min_val": 9, "max_val": 10, "color": "red", "priority": 3, "label": "Insoportable"}
                    ]
                }
            ]
        }
    ]
    
    print("Iniciando carga de datos de signos vitales...")
    
    # Limpiar colección existente para evitar duplicados en desarrollo
    repo.collection.delete_many({})
    
    for item in data:
        ref = VitalSignReference(**item)
        repo.create(ref.model_dump(by_alias=True, exclude_none=True))
        print(f"Creado: {ref.name}")
        
    print("Carga completada exitosamente.")

if __name__ == "__main__":
    seed_vital_signs()
