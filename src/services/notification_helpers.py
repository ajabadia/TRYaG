# path: src/services/notification_helpers.py
# Creado: 2025-11-25
"""
Helpers para facilitar la creación de notificaciones con configuración dinámica.
Determina automáticamente qué canales usar según la configuración del sistema.
"""
from typing import List
from services.notification_service import NotificationChannel
from db.repositories.notification_config import get_smtp_config, get_webhook_config


def get_active_channels() -> List[NotificationChannel]:
    """
    Obtiene los canales de notificación activos según la configuración.
    
    Returns:
        Lista de canales activos (siempre incluye IN_APP)
    """
    channels = [NotificationChannel.IN_APP]  # Siempre activo
    
    # Verificar si SMTP está activado
    smtp_config = get_smtp_config()
    if smtp_config.get('enabled', False):
        channels.append(NotificationChannel.EMAIL)
    
    # Verificar si Webhook está activado
    webhook_config = get_webhook_config()
    if webhook_config.get('enabled', False):
        channels.append(NotificationChannel.WEBHOOK)
    
    return channels


def get_channels_for_priority(priority: str) -> List[NotificationChannel]:
    """
    Obtiene canales según prioridad de la notificación.
    
    Args:
        priority: "critical", "high", "medium", "low"
    
    Returns:
        Lista de canales apropiados para esa prioridad
    """
    channels = [NotificationChannel.IN_APP]  # Siempre activo
    
    # Critical y High: usar todos los canales disponibles
    if priority in ['critical', 'high']:
        return get_active_channels()
    
    # Medium: IN_APP + EMAIL (si está activo)
    elif priority == 'medium':
        smtp_config = get_smtp_config()
        if smtp_config.get('enabled', False):
            channels.append(NotificationChannel.EMAIL)
    
    # Low: solo IN_APP
    
    return channels
