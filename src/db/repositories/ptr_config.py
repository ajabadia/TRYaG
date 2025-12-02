"""
Repositorio para la configuración de Puntuación Total de Riesgo (PTR).
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from db.repositories.base import BaseRepository
from db.models import PTRConfig, PTRRule

class PTRConfigRepository(BaseRepository[PTRConfig]):
    """
    Repositorio para gestionar la configuración de reglas y multiplicadores del PTR.
    """
    
    def __init__(self):
        super().__init__("ptr_config")
        self._ensure_indexes()
        self.initialize_defaults()
    
    def _ensure_indexes(self):
        """Crea índices necesarios."""
        self.create_index([("metric_key", 1)], unique=True)

    def get_config(self, metric_key: str) -> Optional[PTRConfig]:
        """Obtiene la configuración para una métrica específica."""
        doc = self.find_one({"metric_key": metric_key})
        if doc:
            return PTRConfig(**doc)
        return None
    
    def get_all_configs(self) -> List[PTRConfig]:
        """Obtiene todas las configuraciones."""
        docs = self.find_all(sort=[("metric_key", 1)])
        return [PTRConfig(**doc) for doc in docs]
    
    def save_config(self, config: PTRConfig) -> bool:
        """Guarda o actualiza una configuración."""
        config.updated_at = datetime.now()
        return self.collection.replace_one(
            {"metric_key": config.metric_key},
            config.model_dump(by_alias=True, exclude={"id"}),
            upsert=True
        ).acknowledged

    def initialize_defaults(self):
        """Inicializa la configuración por defecto si la colección está vacía."""
        if self.collection.count_documents({}) > 0:
            return

        defaults = [
            PTRConfig(
                metric_key="gcs",
                name="Nivel de Conciencia (GCS)",
                base_multiplier=4.0,
                rules=[
                    PTRRule(operator="<", value=9, points=3, description="GCS < 9 (Grave)"),
                    PTRRule(operator="<", value=13, points=2, description="GCS < 13 (Moderado)"),
                    PTRRule(operator="<", value=15, points=1, description="GCS < 15 (Leve)")
                ]
            ),
            PTRConfig(
                metric_key="spo2",
                name="Saturación de Oxígeno (SpO2)",
                base_multiplier=3.0,
                rules=[
                    PTRRule(operator="<", value=90, points=3, description="SpO2 < 90%"),
                    PTRRule(operator="<", value=94, points=2, description="SpO2 < 94%"),
                    PTRRule(operator="<", value=96, points=1, description="SpO2 < 96%")
                ]
            ),
            PTRConfig(
                metric_key="pas",
                name="Presión Arterial Sistólica (PAS)",
                base_multiplier=3.0,
                rules=[
                    PTRRule(operator="<", value=90, points=3, description="PAS < 90 (Hipotensión Severa)"),
                    PTRRule(operator=">", value=220, points=3, description="PAS > 220 (Crisis Hipertensiva)"),
                    PTRRule(operator="<", value=100, points=2, description="PAS < 100"),
                    PTRRule(operator=">", value=180, points=2, description="PAS > 180"),
                    PTRRule(operator="<", value=110, points=1, description="PAS < 110"),
                    PTRRule(operator=">", value=160, points=1, description="PAS > 160")
                ]
            ),
            PTRConfig(
                metric_key="fr",
                name="Frecuencia Respiratoria (FR)",
                base_multiplier=2.0,
                rules=[
                    PTRRule(operator="<", value=8, points=3, description="FR < 8 (Bradipnea Severa)"),
                    PTRRule(operator=">", value=30, points=3, description="FR > 30 (Taquipnea Severa)"),
                    PTRRule(operator="<", value=12, points=2, description="FR < 12"),
                    PTRRule(operator=">", value=24, points=2, description="FR > 24"),
                    PTRRule(operator=">", value=20, points=1, description="FR > 20")
                ]
            ),
            PTRConfig(
                metric_key="fc",
                name="Frecuencia Cardíaca (FC)",
                base_multiplier=1.0,
                geriatric_multiplier=2.0,
                rules=[
                    PTRRule(operator="<", value=40, points=3, description="FC < 40 (Bradicardia Severa)"),
                    PTRRule(operator=">", value=130, points=3, description="FC > 130 (Taquicardia Severa)"),
                    PTRRule(operator="<", value=50, points=2, description="FC < 50"),
                    PTRRule(operator=">", value=110, points=2, description="FC > 110"),
                    PTRRule(operator=">", value=100, points=1, description="FC > 100")
                ]
            ),
            PTRConfig(
                metric_key="temp",
                name="Temperatura",
                base_multiplier=1.0,
                immuno_multiplier=3.0,
                rules=[
                    PTRRule(operator="<", value=35, points=3, description="Temp < 35 (Hipotermia)"),
                    PTRRule(operator=">", value=40, points=3, description="Temp > 40 (Hiperpirexia)"),
                    PTRRule(operator=">", value=39, points=2, description="Temp > 39"),
                    PTRRule(operator=">", value=38, points=1, description="Temp > 38")
                ]
            ),
            PTRConfig(
                metric_key="dolor",
                name="Escala de Dolor (EVA)",
                base_multiplier=1.0,
                rules=[
                    PTRRule(operator=">=", value=9, points=3, description="EVA >= 9 (Insoportable)"),
                    PTRRule(operator=">=", value=7, points=2, description="EVA >= 7 (Severo)"),
                    PTRRule(operator=">=", value=4, points=1, description="EVA >= 4 (Moderado)")
                ]
            )
        ]

        for config in defaults:
            self.save_config(config)

# Instancia singleton
_ptr_config_repo: Optional[PTRConfigRepository] = None

def get_ptr_config_repository() -> PTRConfigRepository:
    """Obtiene la instancia singleton del repositorio."""
    global _ptr_config_repo
    if _ptr_config_repo is None:
        _ptr_config_repo = PTRConfigRepository()
    return _ptr_config_repo
