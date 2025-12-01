# path: src/components/triage/vital_signs/utils.py
from typing import Dict, Any
from db.repositories.vital_signs_repo import VitalSignsRepository

def get_all_configs(age: int) -> Dict[str, Any]:
    """Carga todas las configuraciones de signos vitales para la edad dada."""
    repo = VitalSignsRepository()
    configs = {}
    for metric in ["fc", "spo2", "temp", "pas", "pad", "fr", "gcs"]:
        configs[metric] = repo.get_config(metric, age)
    return configs
