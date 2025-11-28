# path: src/db/repositories/report_config.py
# Creado: 2025-11-26
"""
Repositorio para la configuración de reportes programados.
"""
from db.connection import get_database

def get_report_config():
    """Obtiene la configuración del reporte semanal."""
    db = get_database()
    config = db.report_config.find_one({"type": "weekly_metrics"})
    if not config:
        return {
            "recipients": [],
            "day_of_week": "monday",
            "time": "08:00",
            "enabled": False
        }
    return config

def save_report_config(recipients, day_of_week, time_str, enabled):
    """Guarda la configuración del reporte semanal."""
    db = get_database()
    db.report_config.update_one(
        {"type": "weekly_metrics"},
        {"$set": {
            "recipients": recipients,
            "day_of_week": day_of_week,
            "time": time_str,
            "enabled": enabled
        }},
        upsert=True
    )
