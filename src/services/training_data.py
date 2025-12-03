# path: src/services/training_data.py
"""
Datos de casos clínicos para el Modo Formación.
"""

CLINICAL_CASES = [
  {
    "id": "case_001",
    "title": "Dolor Torácico en Varón de 55 años",
    "description": "Paciente acude por dolor opresivo en el pecho irradiado a brazo izquierdo.",
    "patient_data": {
      "name": "Juan Ejemplo Formación",
      "age": 55,
      "gender": "Masculino",
      "identification": "TRNG-001"
    },
    "clinical_data": {
      "motivo_consulta": "Dolor en el pecho desde hace 30 minutos.",
      "vital_signs": {
        "sistolica": 160,
        "diastolica": 95,
        "frecuencia_cardiaca": 110,
        "saturacion": 96,
        "temperatura": 36.5,
        "nivel_dolor": 8
      },
      "symptoms": [
        "Dolor torácico opresivo",
        "Irradiación a brazo izquierdo",
        "Sudoración profusa",
        "Náuseas"
      ]
    },
    "gold_standard": {
      "triage_level": 2,
      "reason": "Dolor torácico sugestivo de isquemia miocárdica (SCA). Requiere atención inmediata (Nivel 2) para realizar ECG y enzimas cardiacas.",
      "destination": "Box de Parada / Críticos"
    }
  },
  {
    "id": "case_002",
    "title": "Esguince de Tobillo",
    "description": "Mujer de 25 años con torcedura de tobillo derecho tras caída.",
    "patient_data": {
      "name": "Maria Test Formación",
      "age": 25,
      "gender": "Femenino",
      "identification": "TRNG-002"
    },
    "clinical_data": {
      "motivo_consulta": "Dolor e inflamación en tobillo derecho.",
      "vital_signs": {
        "sistolica": 120,
        "diastolica": 70,
        "frecuencia_cardiaca": 78,
        "saturacion": 99,
        "temperatura": 36.2,
        "nivel_dolor": 4
      },
      "symptoms": [
        "Dolor en tobillo derecho",
        "Edema moderado",
        "Dificultad para la marcha"
      ]
    },
    "gold_standard": {
      "triage_level": 4,
      "reason": "Traumatismo menor sin signos de compromiso neurovascular. Urgencia menor (Nivel 4).",
      "destination": "Traumatología"
    }
  },
  {
    "id": "case_003",
    "title": "Fiebre en Niño de 4 años",
    "description": "Niño traído por sus padres por fiebre de 39°C y malestar general.",
    "patient_data": {
      "name": "Pedrito Demo Formación",
      "age": 4,
      "gender": "Masculino",
      "identification": "TRNG-003"
    },
    "clinical_data": {
      "motivo_consulta": "Fiebre alta y decaimiento.",
      "vital_signs": {
        "sistolica": 100,
        "diastolica": 60,
        "frecuencia_cardiaca": 120,
        "saturacion": 98,
        "temperatura": 39.2,
        "nivel_dolor": 3
      },
      "symptoms": [
        "Fiebre",
        "Rinorrea",
        "Tos leve",
        "Decaimiento"
      ]
    },
    "gold_standard": {
      "triage_level": 3,
      "reason": "Fiebre alta en paciente pediátrico con buen estado general aparente, pero requiere valoración para descartar foco infeccioso grave. Nivel 3.",
      "destination": "Pediatría"
    }
  }
]
