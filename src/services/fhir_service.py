from typing import Dict, Any, List
from datetime import datetime
import uuid

class FHIRService:
    """
    Servicio para convertir modelos internos a recursos FHIR (R4).
    Referencias:
    - HL7 FHIR Release 4: http://hl7.org/fhir/R4/
    """

    @staticmethod
    def create_patient_resource(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un recurso FHIR Patient a partir de los datos del paciente.
        Ref: http://hl7.org/fhir/R4/patient.html
        """
        # Identificadores
        identifiers = []
        if "identification_number" in patient_data:
            identifiers.append({
                "use": "official",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "NN",
                        "display": "National Person Identifier"
                    }]
                },
                "system": "urn:oid:2.16.840.1.113883.2.4.6.3", # OID de ejemplo para DNI/NIF
                "value": patient_data["identification_number"]
            })

        # Nombre
        name = []
        if "nombre" in patient_data:
            # Asumimos que el nombre viene completo, intentamos separar (simplificado)
            parts = patient_data["nombre"].split(" ")
            family = parts[-1] if len(parts) > 1 else ""
            given = parts[:-1] if len(parts) > 1 else [patient_data["nombre"]]
            
            name.append({
                "use": "official",
                "family": family,
                "given": given
            })

        # Género
        gender_map = {
            "Masculino": "male",
            "Femenino": "female",
            "Otro": "other",
            "Desconocido": "unknown"
        }
        gender = gender_map.get(patient_data.get("genero", "Desconocido"), "unknown")

        resource = {
            "resourceType": "Patient",
            "id": str(uuid.uuid4()), # ID temporal para el recurso exportado
            "identifier": identifiers,
            "active": True,
            "name": name,
            "gender": gender,
        }

        if "fecha_nacimiento" in patient_data:
            # Asegurar formato YYYY-MM-DD
            try:
                birth_date = patient_data["fecha_nacimiento"]
                if isinstance(birth_date, datetime):
                    resource["birthDate"] = birth_date.strftime("%Y-%m-%d")
                else:
                    resource["birthDate"] = str(birth_date).split("T")[0]
            except:
                pass

        return resource

    @staticmethod
    def create_encounter_resource(triage_record: Dict[str, Any], patient_fhir_id: str) -> Dict[str, Any]:
        """
        Crea un recurso FHIR Encounter a partir del registro de triaje.
        Ref: http://hl7.org/fhir/R4/encounter.html
        """
        resource = {
            "resourceType": "Encounter",
            "id": str(uuid.uuid4()),
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "EMER",
                "display": "emergency"
            },
            "subject": {
                "reference": f"Patient/{patient_fhir_id}"
            },
            "period": {
                "start": triage_record.get("fecha_hora", datetime.now()).isoformat()
            },
            "reasonCode": []
        }

        # Motivo de consulta (Presenting Problem)
        if "motivo_consulta" in triage_record:
            resource["reasonCode"].append({
                "text": triage_record["motivo_consulta"]
            })

        # Prioridad (basada en nivel de triaje)
        if "nivel_prioridad" in triage_record:
            priority_code = str(triage_record["nivel_prioridad"])
            resource["priority"] = {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                    "code": f"L{priority_code}", # Mapping simplificado
                    "display": f"Level {priority_code}"
                }]
            }

        return resource

    @staticmethod
    def create_observation_resources(vital_signs: Dict[str, Any], patient_fhir_id: str, encounter_fhir_id: str) -> List[Dict[str, Any]]:
        """
        Crea una lista de recursos FHIR Observation para los signos vitales.
        Ref: http://hl7.org/fhir/R4/observation.html
        Usando códigos LOINC estándar.
        """
        observations = []
        timestamp = datetime.now().isoformat()

        # Mapeo de campos internos a códigos LOINC
        loinc_map = {
            "sistolica": {"code": "8480-6", "display": "Systolic blood pressure", "unit": "mmHg"},
            "diastolica": {"code": "8462-4", "display": "Diastolic blood pressure", "unit": "mmHg"},
            "frecuencia_cardiaca": {"code": "8867-4", "display": "Heart rate", "unit": "/min"},
            "frecuencia_respiratoria": {"code": "9279-1", "display": "Respiratory rate", "unit": "/min"},
            "temperatura": {"code": "8310-5", "display": "Body temperature", "unit": "Cel"},
            "saturacion_oxigeno": {"code": "2708-6", "display": "Oxygen saturation in Arterial blood", "unit": "%"},
            "glucemia": {"code": "2339-0", "display": "Glucose [Mass/volume] in Blood", "unit": "mg/dL"},
            "glasgow": {"code": "9269-2", "display": "Glasgow coma score total", "unit": "{score}"}
        }

        for key, value in vital_signs.items():
            if key in loinc_map and value is not None:
                meta = loinc_map[key]
                obs = {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": meta["code"],
                            "display": meta["display"]
                        }]
                    },
                    "subject": {
                        "reference": f"Patient/{patient_fhir_id}"
                    },
                    "encounter": {
                        "reference": f"Encounter/{encounter_fhir_id}"
                    },
                    "effectiveDateTime": timestamp,
                    "valueQuantity": {
                        "value": float(value),
                        "unit": meta["unit"],
                        "system": "http://unitsofmeasure.org",
                        "code": meta["unit"]
                    }
                }
                observations.append(obs)

        return observations

    @staticmethod
    def create_bundle(patient_data: Dict[str, Any], triage_record: Dict[str, Any], vital_signs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Empaqueta todos los recursos en un FHIR Bundle tipo 'document' o 'collection'.
        Ref: http://hl7.org/fhir/R4/bundle.html
        """
        patient = FHIRService.create_patient_resource(patient_data)
        encounter = FHIRService.create_encounter_resource(triage_record, patient["id"])
        observations = FHIRService.create_observation_resources(vital_signs, patient["id"], encounter["id"])

        entries = [
            {"resource": patient},
            {"resource": encounter}
        ]
        for obs in observations:
            entries.append({"resource": obs})

        bundle = {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()),
            "type": "collection",
            "timestamp": datetime.now().isoformat(),
            "entry": entries
        }
        return bundle
