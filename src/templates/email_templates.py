# path: src/templates/email_templates.py
# Creado: 2025-11-25
"""
Templates HTML profesionales para emails de notificaciones.
"""
from typing import Dict, Any
from datetime import datetime


def render_email_template(notification: Dict[str, Any]) -> str:
    """
    Genera HTML para email basado en tipo de notificación.
    
    Args:
        notification: Dict con datos de la notificación
    
    Returns:
        str: HTML del email
    """
    category = notification.get('category', 'general')
    
    if category == 'room_error':
        return render_room_error_email(notification)
    elif category == 'patient_update':
        return render_patient_update_email(notification)
    elif category == 'system_alert':
        return render_system_alert_email(notification)
    else:
        return render_generic_email(notification)


def get_priority_config(priority: str) -> Dict[str, str]:
    """Configuración visual por prioridad."""
    configs = {
        'critical': {
            'color': '#DC3545',
            'icon': '🚨',
            'label': 'CRÍTICO'
        },
        'high': {
            'color': '#FFC107',
            'icon': '⚠️',
            'label': 'ALTA'
        },
        'medium': {
            'color': '#17A2B8',
            'icon': 'ℹ️',
            'label': 'MEDIA'
        },
        'low': {
            'color': '#6C757D',
            'icon': '📝',
            'label': 'BAJA'
        }
    }
    return configs.get(priority, configs['medium'])


def render_room_error_email(notification: Dict[str, Any]) -> str:
    """Template específico para errores de sala."""
    priority_config = get_priority_config(notification.get('priority', 'high'))
    metadata = notification.get('metadata', {})
    
    patient_code = metadata.get('patient_code', 'N/A')
    patient_name = metadata.get('patient_name', 'N/A')
    sala_erronea = metadata.get('sala_erronea', 'N/A')
    motivo = metadata.get('motivo', 'N/A')
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{notification['title']}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                background-color: #ffffff;
                margin: 20px auto;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background-color: {priority_config['color']};
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }}
            .priority-badge {{
                display: inline-block;
                background-color: rgba(255,255,255,0.2);
                padding: 5px 15px;
                border-radius: 20px;
                margin-top: 10px;
                font-size: 12px;
                font-weight: bold;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .alert-box {{
                background-color: #fff3cd;
                border-left: 4px solid {priority_config['color']};
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .info-grid {{
                display: table;
                width: 100%;
                margin: 20px 0;
            }}
            .info-row {{
                display: table-row;
            }}
            .info-label {{
                display: table-cell;
                padding: 10px;
                font-weight: bold;
                background-color: #f8f9fa;
                width: 40%;
            }}
            .info-value {{
                display: table-cell;
                padding: 10px;
                border-bottom: 1px solid #dee2e6;
            }}
            .button {{
                display: inline-block;
                background-color: #28a745;
                color: white !important;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
                text-align: center;
            }}
            .button:hover {{
                background-color: #218838;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #6c757d;
                border-top: 1px solid #dee2e6;
            }}
            .icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="icon">{priority_config['icon']}</div>
                <h1>{notification['title']}</h1>
                <div class="priority-badge">
                    PRIORIDAD: {priority_config['label']}
                </div>
            </div>
            
            <div class="content">
                <div class="alert-box">
                    <strong>Descripción:</strong><br>
                    {notification['message']}
                </div>
                
                <h3>📋 Detalles del Error</h3>
                <div class="info-grid">
                    <div class="info-row">
                        <div class="info-label">👤 Paciente:</div>
                        <div class="info-value">{patient_name}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">🆔 Código:</div>
                        <div class="info-value">{patient_code}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">🏥 Sala Errónea:</div>
                        <div class="info-value"><strong>{sala_erronea}</strong></div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">⚠️ Motivo:</div>
                        <div class="info-value">{motivo}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">🕐 Detectado:</div>
                        <div class="info-value">{notification.get('created_at', datetime.now()).strftime('%d/%m/%Y %H:%M:%S')}</div>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <a href="#" class="button">
                        🔧 Ir al Sistema para Resolver
                    </a>
                </div>
                
                <p style="margin-top: 30px; padding: 15px; background-color: #e7f3ff; border-radius: 4px; font-size: 14px;">
                    💡 <strong>Acción Requerida:</strong> Este error requiere atención inmediata. 
                    Accede al sistema para reasignar al paciente a una sala válida.
                </p>
            </div>
            
            <div class="footer">
                <p><strong>Sistema de Triaje IA - Gestión de Urgencias</strong></p>
                <p>Este es un mensaje automatizado. Por favor no responder a este email.</p>
                <p style="color: #adb5bd; margin-top: 10px;">
                    Powered by Sistema de Triaje IA © 2025
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def render_patient_update_email(notification: Dict[str, Any]) -> str:
    """Template para actualizaciones de paciente."""
    priority_config = get_priority_config(notification.get('priority', 'medium'))
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 20px auto; background: white; }}
            .header {{ background-color: {priority_config['color']}; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{priority_config['icon']} {notification['title']}</h1>
            </div>
            <div class="content">
                <p>{notification['message']}</p>
                <p><small>Fecha: {notification.get('created_at', datetime.now()).strftime('%d/%m/%Y %H:%M:%S')}</small></p>
            </div>
            <div class="footer">
                <p>Sistema de Triaje IA</p>
            </div>
        </div>
    </body>
    </html>
    """


def render_system_alert_email(notification: Dict[str, Any]) -> str:
    """Template para alertas del sistema."""
    priority_config = get_priority_config(notification.get('priority', 'medium'))
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 8px; overflow: hidden; }}
            .header {{ background-color: {priority_config['color']}; color: white; padding: 25px; text-align: center; }}
            .content {{ padding: 25px; }}
            .alert {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid {priority_config['color']}; margin: 15px 0; }}
            .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{priority_config['icon']} Alerta del Sistema</h1>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Prioridad: {priority_config['label']}</p>
            </div>
            <div class="content">
                <h2>{notification['title']}</h2>
                <div class="alert">
                    {notification['message']}
                </div>
                <p><strong>Timestamp:</strong> {notification.get('created_at', datetime.now()).strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
            <div class="footer">
                <p>Sistema de Triaje IA - Monitoreo Automático</p>
            </div>
        </div>
    </body>
    </html>
    """


def render_generic_email(notification: Dict[str, Any]) -> str:
    """Template genérico para cualquier tipo de notificación."""
    priority_config = get_priority_config(notification.get('priority', 'medium'))
    
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f4f4f4; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .header {{ background-color: {priority_config['color']}; color: white; padding: 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 22px; }}
            .content {{ padding: 25px; }}
            .content p {{ margin: 15px 0; }}
            .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; border-top: 1px solid #dee2e6; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{priority_config['icon']} {notification['title']}</h1>
            </div>
            <div class="content">
                <p>{notification['message']}</p>
                <p style="font-size: 13px; color: #6c757d; margin-top: 20px;">
                    <strong>Categoría:</strong> {notification.get('category', 'general')}<br>
                    <strong>Prioridad:</strong> {priority_config['label']}<br>
                    <strong>Fecha:</strong> {notification.get('created_at', datetime.now()).strftime('%d/%m/%Y %H:%M:%S')}
                </p>
            </div>
            <div class="footer">
                <p><strong>Sistema de Triaje IA</strong></p>
                <p>Mensaje automatizado - No responder</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_recipient_emails(recipients: list) -> list:
    """
    Obtiene emails de usuarios desde BD, resolviendo IDs y Roles.
    
    Args:
        recipients: Lista de IDs de usuarios o Códigos de Rol (ej: "admin", "medico")
    
    Returns:
        List de emails únicos y válidos
    """
    if not recipients:
        return []

    from db.repositories.users import get_users_repository
    
    repo = get_users_repository()
    emails = set()
    
    # Obtener todos los usuarios activos una sola vez para filtrar en memoria (más eficiente para pocos usuarios)
    all_users = repo.get_all_users(active_only=True)
    
    for recipient in recipients:
        # Caso 1: Es un Rol (ej: "administrador", "medico")
        # Buscamos usuarios que tengan este rol
        users_by_role = [u for u in all_users if u.get("rol") == recipient]
        if users_by_role:
            for user in users_by_role:
                if user.get("email"):
                    emails.add(user["email"])
            continue
            
        # Caso 2: Es un ID de usuario específico
        # Buscamos por _id
        user_by_id = next((u for u in all_users if str(u["_id"]) == recipient), None)
        if user_by_id and user_by_id.get("email"):
            emails.add(user_by_id["email"])
            continue
            
        # Caso 3: Es directamente un email (fallback)
        if "@" in recipient and "." in recipient:
            emails.add(recipient)

    return list(emails)
