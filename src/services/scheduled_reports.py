# path: src/services/scheduled_reports.py
# Creado: 2025-11-26
"""
Servicio para la programación y envío de reportes automáticos.
"""
import threading
import time
import schedule
from datetime import datetime
from typing import List
from services.export_service import generate_metrics_pdf
from services.notification_service import send_email_with_attachment
from db.repositories.report_config import get_report_config

def run_scheduler():
    """Ejecuta el loop del planificador en un hilo separado."""
    while True:
        schedule.run_pending()
        time.sleep(60)

def start_scheduler():
    """Inicia el planificador en segundo plano."""
    # Cargar configuración inicial
    reload_scheduler()
    
    t = threading.Thread(target=run_scheduler, daemon=True)
    t.start()

def reload_scheduler():
    """Recarga la configuración del planificador desde la BD."""
    schedule.clear()
    config = get_report_config()
    
    if config.get("enabled") and config.get("recipients"):
        day = config.get("day_of_week", "monday")
        time_str = config.get("time", "08:00")
        recipients = config.get("recipients")
        
        # Programar
        try:
            job_creator = getattr(schedule.every(), day)
            job_creator.at(time_str).do(
                send_weekly_report, recipients=recipients
            )
            print(f"Scheduler: Reporte programado para {day} a las {time_str}")
        except Exception as e:
            print(f"Error programando reporte: {e}")

def schedule_weekly_report(recipients: List[str], day_of_week: str = "monday", time_str: str = "08:00"):
    """
    (Deprecado - usar save_report_config + reload_scheduler)
    Mantiene compatibilidad o para uso manual.
    """
    pass

def send_weekly_report(recipients: List[str]):
    """Genera y envía el reporte semanal."""
    print(f"Generando reporte semanal para: {recipients}")
    try:
        pdf_bytes = generate_metrics_pdf(periodo_dias=7)
        
        filename = f"reporte_semanal_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        success = send_email_with_attachment(
            recipients=recipients,
            subject="📊 Reporte Semanal de Gestión de Salas",
            body="Adjunto encontrará el reporte semanal de errores y métricas de gestión de salas.",
            attachment_data=pdf_bytes,
            attachment_name=filename
        )
        
        if success:
            print("Reporte semanal enviado correctamente")
        else:
            print("Error al enviar reporte semanal")
            
    except Exception as e:
        print(f"Error generando/enviando reporte: {e}")
