# path: src/services/notification_service.py
# Creado: 2025-11-25
"""
Servicio de notificaciones flexible y modular.
Soporta múltiples canales: in-app, email, webhook, etc.
Principios: DRY, Modularidad, Extensibilidad
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from db import get_database
import streamlit as st


class NotificationChannel(Enum):
    """Canales de notificación disponibles."""
    IN_APP = "in_app"           # Notificaciones dentro de la aplicación
    EMAIL = "email"              # Correo electrónico
    WEBHOOK = "webhook"          # Webhook HTTP
    LOG = "log"                  # Registro en base de datos solamente


class NotificationPriority(Enum):
    """Niveles de prioridad."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationCategory(Enum):
    """Categorías de notificaciones."""
    ROOM_ERROR = "room_error"
    PATIENT_UPDATE = "patient_update"
    SYSTEM_ALERT = "system_alert"
    AUDIT = "audit"
    GENERAL = "general"
    SHIFT_ASSIGNMENT = "shift_assignment"


# ---------------------------------------------------------------------------
# Base de Datos - Gestión de Notificaciones
# ---------------------------------------------------------------------------

def create_notification(
    title: str,
    message: str,
    category: NotificationCategory = NotificationCategory.GENERAL,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    channels: List[NotificationChannel] = None,
    recipients: List[str] = None,
    metadata: Dict[str, Any] = None,
    action_url: Optional[str] = None
) -> str:
    """
    Crea una nueva notificación en el sistema.
    
    Args:
        title: Título de la notificación
        message: Mensaje detallado
        category: Categoría (room_error, patient_update, etc.)
        priority: Nivel de prioridad
        channels: Lista de canales por los que enviar (default: IN_APP)
        recipients: Lista de IDs de destinatarios (default: todos los admins)
        metadata: Datos adicionales contextuales
        action_url: URL de acción (ej: para "ir a resolver")
    
    Returns:
        str: ID de la notificación creada
    """
    db = get_database()
    collection = db["notifications"]
    
    if channels is None:
        channels = [NotificationChannel.IN_APP]
    
    if recipients is None:
        recipients = ["admin"]  # Por defecto a todos los admins
    
    notification_doc = {
        "title": title,
        "message": message,
        "category": category.value,
        "priority": priority.value,
        "channels": [ch.value for ch in channels],
        "recipients": recipients,
        "metadata": metadata or {},
        "action_url": action_url,
        "created_at": datetime.now(),
        "read_by": [],
        "dismissed_by": [],
        "sent_status": {
            "in_app": True,  # Siempre se registra en BD
            "email": None,
            "webhook": None
        }
    }
    
    result = collection.insert_one(notification_doc)
    notification_id = str(result.inserted_id)
    
    # Procesar envío por cada canal
    for channel in channels:
        _send_via_channel(channel, notification_doc, notification_id)
    
    return notification_id


def _send_via_channel(
    channel: NotificationChannel,
    notification: Dict[str, Any],
    notification_id: str
):
    """
    Envía notificación por un canal específico.
    
    Args:
        channel: Canal de envío
        notification: Documento de notificación
        notification_id: ID de la notificación
    """
    db = get_database()
    collection = db["notifications"]
    
    try:
        if channel == NotificationChannel.EMAIL:
            success = _send_email(notification)
            collection.update_one(
                {"_id": notification_id},
                {"$set": {"sent_status.email": success}}
            )
        
        elif channel == NotificationChannel.WEBHOOK:
            success = _send_webhook(notification)
            collection.update_one(
                {"_id": notification_id},
                {"$set": {"sent_status.webhook": success}}
            )
        
        # IN_APP y LOG no requieren envío externo
        
    except Exception as e:
        # Log error pero no fallar
        print(f"Error sending via {channel.value}: {e}")


def _send_email(notification: Dict[str, Any]) -> bool:
    """
    Envía notificación por email usando configuración SMTP.
    
    Args:
        notification: Datos de la notificación
    
    Returns:
        bool: True si se envió correctamente
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from db.repositories.notification_config import get_smtp_config
    from templates.email_templates import render_email_template, get_recipient_emails
    
    # Obtener configuración SMTP
    smtp_config = get_smtp_config()
    
    if not smtp_config.get('enabled', False):
        print("SMTP no está habilitado")
        return False
    
    # Validar campos requeridos
    required_fields = ['host', 'port', 'username', 'password', 'from_email']
    for field in required_fields:
        if not smtp_config.get(field):
            print(f"Campo SMTP requerido faltante: {field}")
            return False
    
    try:
        # Obtener emails de destinatarios
        recipient_emails = get_recipient_emails(notification.get('recipients', []))
        
        if not recipient_emails:
            print("No hay destinatarios de email")
            return False
        
        # Crear mensaje
        msg = MIMEMultipart("alternative")
        msg["Subject"] = notification['title']
        msg["From"] = smtp_config['from_email']
        msg["To"] = ", ".join(recipient_emails)
        
        # Generar HTML desde template
        html_content = render_email_template(notification)
        
        # Adjuntar HTML
        msg.attach(MIMEText(html_content, "html", "utf-8"))
        
        # Conectar y enviar
        if smtp_config.get('use_tls', True):
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=30)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'], timeout=30)
        
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
        
        print(f"Email enviado exitosamente a {len(recipient_emails)} destinatario(s)")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"Error de autenticación SMTP: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"Error SMTP: {e}")
        return False
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


def send_email_with_attachment(
    recipients: List[str],
    subject: str,
    body: str,
    attachment_data: bytes,
    attachment_name: str
) -> bool:
    """
    Envía un email con un archivo adjunto.
    
    Args:
        recipients: Lista de emails destinatarios
        subject: Asunto del email
        body: Cuerpo del email (texto plano o HTML)
        attachment_data: Contenido del archivo en bytes
        attachment_name: Nombre del archivo adjunto
        
    Returns:
        bool: True si se envió correctamente
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    from db.repositories.notification_config import get_smtp_config
    
    smtp_config = get_smtp_config()
    
    if not smtp_config.get('enabled', False):
        print("SMTP no está habilitado")
        return False
        
    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = smtp_config['from_email']
        msg["To"] = ", ".join(recipients)
        
        # Cuerpo
        msg.attach(MIMEText(body, "html"))
        
        # Adjunto
        part = MIMEApplication(attachment_data, Name=attachment_name)
        part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
        msg.attach(part)
        
        # Enviar
        if smtp_config.get('use_tls', True):
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=30)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'], timeout=30)
            
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error enviando email con adjunto: {e}")
        return False


def _send_webhook(notification: Dict[str, Any]) -> bool:
    """
    Envía notificación vía webhook HTTP (Slack, Teams, etc.).
    
    Args:
        notification: Datos de la notificación
    
    Returns:
        bool: True si se envió correctamente
    """
    import requests
    from db.repositories.notification_config import get_webhook_config
    
    # Obtener configuración webhook
    webhook_config = get_webhook_config()
    
    if not webhook_config.get('enabled', False):
        print("Webhook no está habilitado")
        return False
    
    webhook_url = webhook_config.get('url', '')
    if not webhook_url:
        print("URL de webhook no configurada")
        return False
    
    webhook_type = webhook_config.get('type', 'slack')
    
    try:
        # Color según prioridad
        priority_colors = {
            'critical': '#DC3545',  # Rojo
            'high': '#FFC107',      # Amarillo
            'medium': '#17A2B8',    # Azul
            'low': '#6C757D'        # Gris
        }
        color = priority_colors.get(notification.get('priority', 'medium'), '#17A2B8')
        
        # Payload según tipo de webhook
        if webhook_type == 'slack':
            payload = {
                "text": f"*{notification['title']}*",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {
                                "title": "Mensaje",
                                "value": notification['message'],
                                "short": False
                            },
                            {
                                "title": "Prioridad",
                                "value": notification.get('priority', 'medium').upper(),
                                "short": True
                            },
                            {
                                "title": "Categoría",
                                "value": notification.get('category', 'general'),
                                "short": True
                            }
                        ],
                        "footer": "Sistema de Triaje IA",
                        "ts": int(notification.get('created_at', datetime.now()).timestamp())
                    }
                ]
            }
        
        elif webhook_type == 'teams':
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "summary": notification['title'],
                "themeColor": color.replace('#', ''),
                "title": notification['title'],
                "sections": [
                    {
                        "activityTitle": "Sistema de Triaje IA",
                        "activitySubtitle": notification.get('created_at', datetime.now()).strftime('%d/%m/%Y %H:%M:%S'),
                        "facts": [
                            {"name": "Mensaje", "value": notification['message']},
                            {"name": "Prioridad", "value": notification.get('priority', 'medium').upper()},
                            {"name": "Categoría", "value": notification.get('category', 'general')}
                        ],
                        "markdown": True
                    }
                ]
            }
        
        else:  # generic webhook
            payload = {
                "title": notification['title'],
                "message": notification['message'],
                "category": notification.get('category', 'general'),
                "priority": notification.get('priority', 'medium'),
                "timestamp": notification.get('created_at', datetime.now()).isoformat(),
                "metadata": notification.get('metadata', {})
            }
        
        # Enviar POST request
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print(f"Webhook enviado exitosamente ({webhook_type})")
            return True
        else:
            print(f"Error en webhook: HTTP {response.status_code} - {response.text[:100]}")
            return False
    
    except requests.exceptions.Timeout:
        print("Timeout al enviar webhook")
        return False
    except requests.exceptions.ConnectionError:
        print("Error de conexión al enviar webhook")
        return False
    except Exception as e:
        print(f"Error enviando webhook: {e}")
        return False


# ---------------------------------------------------------------------------
# Consultas de Notificaciones
# ---------------------------------------------------------------------------

def get_user_notifications(
    user_id: str = "admin",
    unread_only: bool = False,
    category: Optional[NotificationCategory] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Obtiene notificaciones para un usuario.
    
    Args:
        user_id: ID del usuario
        unread_only: Si True, solo devuelve no leídas
        category: Filtrar por categoría específica
        limit: Número máximo de notificaciones
    
    Returns:
        Lista de notificaciones ordenadas por fecha (más recientes primero)
    """
    db = get_database()
    collection = db["notifications"]
    
    query = {"recipients": user_id}
    
    if unread_only:
        query["read_by"] = {"$ne": user_id}
    
    if category:
        query["category"] = category.value
    
    notifications = list(
        collection.find(query)
        .sort("created_at", -1)
        .limit(limit)
    )
    
    # Convertir ObjectId a string
    for notif in notifications:
        if '_id' in notif:
            notif['_id'] = str(notif['_id'])
    
    return notifications


def mark_as_read(notification_id: str, user_id: str = "admin") -> bool:
    """
    Marca una notificación como leída.
    
    Args:
        notification_id: ID de la notificación
        user_id: ID del usuario que la leyó
    
    Returns:
        bool: True si se marcó correctamente
    """
    db = get_database()
    collection = db["notifications"]
    
    try:
        result = collection.update_one(
            {"_id": notification_id},
            {"$addToSet": {"read_by": user_id}}
        )
        return result.modified_count > 0
    except Exception:
        return False


def dismiss_notification(notification_id: str, user_id: str = "admin") -> bool:
    """
    Descarta/elimina una notificación para un usuario.
    
    Args:
        notification_id: ID de la notificación
        user_id: ID del usuario
    
    Returns:
        bool: True si se descartó correctamente
    """
    db = get_database()
    collection = db["notifications"]
    
    try:
        result = collection.update_one(
            {"_id": notification_id},
            {"$addToSet": {"dismissed_by": user_id}}
        )
        return result.modified_count > 0
    except Exception:
        return False


def get_unread_count(user_id: str = "admin") -> int:
    """
    Obtiene el número de notificaciones no leídas.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        int: Número de notificaciones no leídas
    """
    db = get_database()
    collection = db["notifications"]
    
    return collection.count_documents({
        "recipients": user_id,
        "read_by": {"$ne": user_id},
        "dismissed_by": {"$ne": user_id}
    })


# ---------------------------------------------------------------------------
# Notificaciones Específicas del Dominio (Helpers)
# ---------------------------------------------------------------------------

def notify_room_error_detected(
    patient_code: str,
    patient_name: str,
    sala_erronea: str,
    motivo: str,
    priority: NotificationPriority = NotificationPriority.HIGH
) -> str:
    """
    Notifica sobre un error de asignación de sala detectado.
    Usa automáticamente los canales configurados en el sistema.
    
    Args:
        patient_code: Código del paciente
        patient_name: Nombre completo del paciente
        sala_erronea: Código de la sala con error
        motivo: Motivo del error
        priority: Prioridad de la notificación
    
    Returns:
        str: ID de la notificación creada
    """
    from services.notification_helpers import get_channels_for_priority
    
    icon = "🚫" if motivo == "Sala inexistente" else "⚠️"
    
    # Determina crítica si es sala inexistente
    if motivo == "Sala inexistente":
        priority = NotificationPriority.CRITICAL
    
    return create_notification(
        title=f"{icon} Error de Asignación - Sala {sala_erronea}",
        message=f"El paciente {patient_name} ({patient_code}) está asignado a una sala inválida: {sala_erronea}. Motivo: {motivo}",
        category=NotificationCategory.ROOM_ERROR,
        priority=priority,
        channels=get_channels_for_priority(priority.value),  # Canales dinámicos
        metadata={
            "patient_code": patient_code,
            "patient_name": patient_name,
            "sala_erronea": sala_erronea,
            "motivo": motivo
        },
        action_url="/gestor_salas"  # URL para ir a resolver
    )


def notify_room_error_resolved(
    patient_code: str,
    patient_name: str,
    sala_antigua: str,
    sala_nueva: str
) -> str:
    """
    Notifica que un error de sala fue resuelto.
    
    Args:
        patient_code: Código del paciente
        patient_name: Nombre del paciente
        sala_antigua: Sala con error
        sala_nueva: Nueva sala asignada
    
    Returns:
        str: ID de la notificación creada
    """
    return create_notification(
        title=f"✅ Error Resuelto - Paciente {patient_code}",
        message=f"El paciente {patient_name} fue reasignado de {sala_antigua} a {sala_nueva}.",
        category=NotificationCategory.ROOM_ERROR,
        priority=NotificationPriority.LOW,
        channels=[NotificationChannel.IN_APP],
        metadata={
            "patient_code": patient_code,
            "patient_name": patient_name,
            "sala_antigua": sala_antigua,
            "sala_nueva": sala_nueva
        }
    )


def notify_shift_created(
    user_name: str,
    sala_code: str,
    fecha_desde: datetime,
    fecha_hasta: datetime,
    horario: str
) -> str:
    """
    Notifica la creación de un nuevo turno.
    
    Args:
        user_name: Nombre del usuario asignado
        sala_code: Código de la sala
        fecha_desde: Fecha inicio
        fecha_hasta: Fecha fin
        horario: String de horario (ej: "08:00 - 15:00")
    
    Returns:
        str: ID de la notificación
    """
    return create_notification(
        title=f"📅 Nuevo Turno Asignado - {user_name}",
        message=f"Se ha asignado un turno a {user_name} en sala {sala_code}. Fecha: {fecha_desde.strftime('%d/%m')} al {fecha_hasta.strftime('%d/%m')}. Horario: {horario}",
        category=NotificationCategory.SHIFT_ASSIGNMENT,
        priority=NotificationPriority.MEDIUM,
        channels=[NotificationChannel.IN_APP], # Podría incluir EMAIL en futuro
        metadata={
            "user_name": user_name,
            "sala_code": sala_code,
            "fecha_desde": fecha_desde.isoformat(),
            "fecha_hasta": fecha_hasta.isoformat()
        }
    )


# ---------------------------------------------------------------------------
# UI Component - Notification Bell
# ---------------------------------------------------------------------------

def render_notification_bell():
    """
    Renderiza un icono de campana con badge de notificaciones no leídas.
    Clicking abre un modal con las notificaciones.
    """
    unread_count = get_unread_count()
    
    # Badge con número
    if unread_count > 0:
        badge_html = f"""
        <div style="position: relative; display: inline-block;">
            <span style="font-size: 24px;">🔔</span>
            <span style="position: absolute; top: -5px; right: -10px; background: red; color: white; 
                         border-radius: 50%; padding: 2px 6px; font-size: 12px; font-weight: bold;">
                {unread_count}
            </span>
        </div>
        """
        st.markdown(badge_html, unsafe_allow_html=True)
    else:
        st.markdown("🔔", unsafe_allow_html=False)


def render_notifications_panel(user_id: str = "admin"):
    """
    Renderiza el panel completo de notificaciones.
    
    Args:
        user_id: ID del usuario actual
    """
    st.markdown("### 🔔 Notificaciones")
    
    # Filtros
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        show_unread_only = st.checkbox("Solo no leídas", value=True)
    with col_filter2:
        category_filter = st.selectbox(
            "Categoría",
            options=["Todas"] + [cat.value for cat in NotificationCategory],
            index=0
        )
    
    # Obtener notificaciones
    category_enum = None if category_filter == "Todas" else NotificationCategory(category_filter)
    notifications = get_user_notifications(
        user_id=user_id,
        unread_only=show_unread_only,
        category=category_enum
    )
    
    if not notifications:
        st.info("No hay notificaciones")
        return
    
    # Renderizar cada notificación
    for notif in notifications:
        is_unread = user_id not in notif.get('read_by', [])
        priority = notif.get('priority', 'medium')
        
        # Color según prioridad
        border_color = {
            'critical': '#DC3545',
            'high': '#FFC107',
            'medium': '#17A2B8',
            'low': '#6C757D'
        }.get(priority, '#6C757D')
        
        with st.container(border=True):
            # Header con título y timestamp
            col_notif_header, col_notif_actions = st.columns([4, 1])
            
            with col_notif_header:
                unread_badge = "🔴 " if is_unread else ""
                st.markdown(f"{unread_badge}**{notif['title']}**")
                created_at = notif.get('created_at', datetime.now())
                st.caption(created_at.strftime("%d/%m/%Y %H:%M"))
            
            with col_notif_actions:
                if is_unread:
                    if st.button("✓", key=f"read_{notif['_id']}", help="Marcar como leída"):
                        mark_as_read(notif['_id'], user_id)
                        st.rerun()
                
                if st.button("✕", key=f"dismiss_{notif['_id']}", help="Descartar"):
                    dismiss_notification(notif['_id'], user_id)
                    st.rerun()
            
            # Mensaje
            st.markdown(notif['message'])
            
            # Botón de acción si hay
            if notif.get('action_url'):
                st.button("Ir a resolver →", key=f"action_{notif['_id']}")
