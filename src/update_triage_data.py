import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from db.connection import get_database

def update_triage_data():
    print("🚀 Iniciando actualización de datos de Triaje (Estudio Gemini 3)...")
    db = get_database()
    
    # --- 1. VITAL SIGNS REFERENCES ---
    print("📊 Actualizando Referencias de Signos Vitales...")
    vs_collection = db["vital_signs_references"]
    
    # Definición de Rangos (Estudio Gemini 3)
    # Prioridad: 0=Normal, 1=Baja(Amarillo), 2=Media(Naranja), 3=Alta(Rojo), 4=Extrema(Negro)
    
    configs = [
        {
            "key": "fc",
            "name": "Frecuencia Cardíaca",
            "unit": "ppm",
            "configs": [{
                "min_age": 0, "max_age": 150,
                "val_min": 0, "val_max": 300,
                "normal_min": 60, "normal_max": 100,
                "default_value": 80,
                "ranges": [
                    {"min_val": 0, "max_val": 0, "color": "black", "priority": 4, "label": "Parada"},
                    {"min_val": 1, "max_val": 39, "color": "red", "priority": 3, "label": "Bradicardia Extrema"},
                    {"min_val": 40, "max_val": 49, "color": "orange", "priority": 2, "label": "Bradicardia Severa"},
                    {"min_val": 50, "max_val": 59, "color": "yellow", "priority": 1, "label": "Bradicardia Leve"},
                    {"min_val": 60, "max_val": 100, "color": "green", "priority": 0, "label": "Normal"},
                    {"min_val": 101, "max_val": 120, "color": "yellow", "priority": 1, "label": "Taquicardia Leve"},
                    {"min_val": 121, "max_val": 140, "color": "orange", "priority": 2, "label": "Taquicardia Severa"},
                    {"min_val": 141, "max_val": 300, "color": "red", "priority": 3, "label": "Taquicardia Extrema"}
                ]
            }]
        },
        {
            "key": "pas",
            "name": "Presión Arterial Sistólica",
            "unit": "mmHg",
            "configs": [{
                "min_age": 0, "max_age": 150,
                "val_min": 0, "val_max": 300,
                "normal_min": 100, "normal_max": 129,
                "default_value": 120,
                "ranges": [
                    {"min_val": 0, "max_val": 79, "color": "red", "priority": 3, "label": "Hipotensión Severa"},
                    {"min_val": 80, "max_val": 89, "color": "orange", "priority": 2, "label": "Hipotensión"},
                    {"min_val": 90, "max_val": 99, "color": "yellow", "priority": 1, "label": "Pre-Hipotensión"},
                    {"min_val": 100, "max_val": 129, "color": "green", "priority": 0, "label": "Normal"},
                    {"min_val": 130, "max_val": 159, "color": "yellow", "priority": 1, "label": "Hipertensión Leve"},
                    {"min_val": 160, "max_val": 179, "color": "orange", "priority": 2, "label": "Hipertensión Moderada"},
                    {"min_val": 180, "max_val": 300, "color": "red", "priority": 3, "label": "Crisis Hipertensiva"}
                ]
            }]
        },
        {
            "key": "pad",
            "name": "Presión Arterial Diastólica",
            "unit": "mmHg",
            "configs": [{
                "min_age": 0, "max_age": 150,
                "val_min": 0, "val_max": 200,
                "normal_min": 60, "normal_max": 84,
                "default_value": 80,
                "ranges": [
                    {"min_val": 0, "max_val": 59, "color": "green", "priority": 0, "label": "Baja/Normal"}, # Simplificado según estudio
                    {"min_val": 60, "max_val": 84, "color": "green", "priority": 0, "label": "Normal"},
                    {"min_val": 85, "max_val": 99, "color": "yellow", "priority": 1, "label": "Elevada"},
                    {"min_val": 100, "max_val": 109, "color": "orange", "priority": 2, "label": "Hipertensión Grado 2"},
                    {"min_val": 110, "max_val": 200, "color": "red", "priority": 3, "label": "Crisis Hipertensiva"}
                ]
            }]
        },
        {
            "key": "spo2",
            "name": "Saturación de Oxígeno",
            "unit": "%",
            "configs": [{
                "min_age": 0, "max_age": 150,
                "val_min": 0, "val_max": 100,
                "normal_min": 95, "normal_max": 100,
                "default_value": 98,
                "ranges": [
                    {"min_val": 0, "max_val": 89, "color": "red", "priority": 3, "label": "Hipoxia Crítica"},
                    {"min_val": 90, "max_val": 92, "color": "orange", "priority": 2, "label": "Hipoxia Moderada"},
                    {"min_val": 93, "max_val": 94, "color": "yellow", "priority": 1, "label": "Hipoxia Leve"},
                    {"min_val": 95, "max_val": 100, "color": "green", "priority": 0, "label": "Normal"}
                ]
            }]
        },
        {
            "key": "temp",
            "name": "Temperatura",
            "unit": "°C",
            "configs": [{
                "min_age": 0, "max_age": 150,
                "val_min": 20, "val_max": 45,
                "normal_min": 36.5, "normal_max": 37.5,
                "default_value": 36.5,
                "ranges": [
                    {"min_val": 0, "max_val": 34.0, "color": "red", "priority": 3, "label": "Hipotermia Severa"},
                    {"min_val": 34.1, "max_val": 34.9, "color": "orange", "priority": 2, "label": "Hipotermia"},
                    {"min_val": 35.0, "max_val": 36.4, "color": "yellow", "priority": 1, "label": "Hipotermia Leve"},
                    {"min_val": 36.5, "max_val": 37.5, "color": "green", "priority": 0, "label": "Normal"},
                    {"min_val": 37.6, "max_val": 37.9, "color": "yellow", "priority": 1, "label": "Febrícula"},
                    {"min_val": 38.0, "max_val": 39.9, "color": "orange", "priority": 2, "label": "Fiebre"},
                    {"min_val": 40.0, "max_val": 50.0, "color": "red", "priority": 3, "label": "Hipertermia"}
                ]
            }]
        },
        {
            "key": "fr",
            "name": "Frecuencia Respiratoria",
            "unit": "rpm",
            "configs": [{
                "min_age": 0, "max_age": 150,
                "val_min": 0, "val_max": 100,
                "normal_min": 12, "normal_max": 20,
                "default_value": 16,
                "ranges": [
                    {"min_val": 0, "max_val": 5, "color": "red", "priority": 3, "label": "Parada/Bradipnea Extrema"},
                    {"min_val": 6, "max_val": 7, "color": "orange", "priority": 2, "label": "Bradipnea Severa"},
                    {"min_val": 8, "max_val": 11, "color": "yellow", "priority": 1, "label": "Bradipnea"},
                    {"min_val": 12, "max_val": 20, "color": "green", "priority": 0, "label": "Normal"},
                    {"min_val": 21, "max_val": 24, "color": "yellow", "priority": 1, "label": "Taquipnea Leve"},
                    {"min_val": 25, "max_val": 29, "color": "orange", "priority": 2, "label": "Taquipnea Moderada"},
                    {"min_val": 30, "max_val": 100, "color": "red", "priority": 3, "label": "Taquipnea Severa"}
                ]
            }]
        },
        {
            "key": "gcs",
            "name": "Escala Glasgow",
            "unit": "pts",
            "configs": [{
                "min_age": 0, "max_age": 150,
                "val_min": 3, "val_max": 15,
                "normal_min": 15, "normal_max": 15,
                "default_value": 15,
                "ranges": [
                    {"min_val": 3, "max_val": 8, "color": "red", "priority": 3, "label": "Coma (Grave)"},
                    {"min_val": 9, "max_val": 12, "color": "orange", "priority": 2, "label": "Moderado"},
                    {"min_val": 13, "max_val": 14, "color": "yellow", "priority": 1, "label": "Leve"},
                    {"min_val": 15, "max_val": 15, "color": "green", "priority": 0, "label": "Consciente"}
                ]
            }]
        },
        {
            "key": "eva", # NUEVO: Escala de Dolor
            "name": "Escala de Dolor (EVA)",
            "unit": "pts",
            "configs": [{
                "min_age": 0, "max_age": 150,
                "val_min": 0, "val_max": 10,
                "normal_min": 0, "normal_max": 3,
                "default_value": 0,
                "ranges": [
                    {"min_val": 0, "max_val": 3, "color": "green", "priority": 0, "label": "Leve"},
                    {"min_val": 4, "max_val": 6, "color": "yellow", "priority": 1, "label": "Moderado"},
                    {"min_val": 7, "max_val": 8, "color": "orange", "priority": 2, "label": "Severo"},
                    {"min_val": 9, "max_val": 10, "color": "red", "priority": 3, "label": "Insoportable"}
                ]
            }]
        }
    ]

    for config in configs:
        vs_collection.update_one(
            {"key": config["key"]},
            {"$set": config},
            upsert=True
        )
        print(f"  ✅ {config['name']} actualizado.")

    # --- 2. PTR CONFIGS ---
    print("\n🧮 Actualizando Configuración PTR...")
    ptr_collection = db["ptr_configs"]
    
    # Multiplicadores y Reglas
    # Reglas: {min, max, points} -> Puntos base por gravedad
    # Multiplicadores: Factor por el que se multiplica los puntos base
    
    ptr_data = [
        {
            "metric_key": "gcs",
            "name": "Glasgow",
            "base_multiplier": 4.0,
            "rules": [ # Puntos base según valor (invertido: menos es peor)
                {"min": 3, "max": 8, "points": 3},
                {"min": 9, "max": 12, "points": 2},
                {"min": 13, "max": 14, "points": 1},
                {"min": 15, "max": 15, "points": 0}
            ]
        },
        {
            "metric_key": "spo2",
            "name": "Saturación O2",
            "base_multiplier": 3.0,
            "rules": [
                {"min": 0, "max": 89, "points": 3},
                {"min": 90, "max": 92, "points": 2},
                {"min": 93, "max": 94, "points": 1},
                {"min": 95, "max": 100, "points": 0}
            ]
        },
        {
            "metric_key": "pas",
            "name": "Presión Sistólica",
            "base_multiplier": 3.0,
            "rules": [
                {"min": 0, "max": 79, "points": 3},
                {"min": 180, "max": 300, "points": 3},
                {"min": 80, "max": 89, "points": 2},
                {"min": 160, "max": 179, "points": 2},
                {"min": 90, "max": 99, "points": 1},
                {"min": 130, "max": 159, "points": 1},
                {"min": 100, "max": 129, "points": 0}
            ]
        },
        {
            "metric_key": "fr",
            "name": "Frecuencia Respiratoria",
            "base_multiplier": 2.0,
            "rules": [
                {"min": 0, "max": 5, "points": 3},
                {"min": 30, "max": 100, "points": 3},
                {"min": 6, "max": 7, "points": 2},
                {"min": 25, "max": 29, "points": 2},
                {"min": 8, "max": 11, "points": 1},
                {"min": 21, "max": 24, "points": 1},
                {"min": 12, "max": 20, "points": 0}
            ]
        },
        {
            "metric_key": "fc",
            "name": "Frecuencia Cardíaca",
            "base_multiplier": 1.0,
            "geriatric_multiplier": 2.0, # Modificador Geriátrico
            "rules": [
                {"min": 0, "max": 39, "points": 3},
                {"min": 141, "max": 300, "points": 3},
                {"min": 40, "max": 49, "points": 2},
                {"min": 121, "max": 140, "points": 2},
                {"min": 50, "max": 59, "points": 1},
                {"min": 101, "max": 120, "points": 1},
                {"min": 60, "max": 100, "points": 0}
            ]
        },
        {
            "metric_key": "temp",
            "name": "Temperatura",
            "base_multiplier": 1.0,
            "immuno_multiplier": 3.0, # Modificador Inmuno
            "rules": [
                {"min": 0, "max": 34.0, "points": 3},
                {"min": 40.0, "max": 50.0, "points": 3},
                {"min": 34.1, "max": 34.9, "points": 2},
                {"min": 38.0, "max": 39.9, "points": 2},
                {"min": 35.0, "max": 36.4, "points": 1},
                {"min": 37.6, "max": 37.9, "points": 1},
                {"min": 36.5, "max": 37.5, "points": 0}
            ]
        },
        {
            "metric_key": "dolor", # Mapeado a EVA
            "name": "Dolor",
            "base_multiplier": 1.0,
            "rules": [
                {"min": 9, "max": 10, "points": 3},
                {"min": 7, "max": 8, "points": 2},
                {"min": 4, "max": 6, "points": 1},
                {"min": 0, "max": 3, "points": 0}
            ]
        }
    ]

    for ptr in ptr_data:
        ptr_collection.update_one(
            {"metric_key": ptr["metric_key"]},
            {"$set": ptr},
            upsert=True
        )
        print(f"  ✅ PTR: {ptr['name']} actualizado.")

    print("\n✨ Actualización completada con éxito.")

if __name__ == "__main__":
    update_triage_data()
