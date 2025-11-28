# path: src/db/repositories/notification_config.py
# Creado: 2025-11-25
"""
Repositorio para gestión de configuración de notificaciones (SMTP, Webhooks).
"""
from typing import Dict, Any, Optional, Tuple
from db.connection import get_database
from datetime import datetime


def save_smtp_config(config: Dict[str, Any]) -> bool:
    """
    Guarda configuración SMTP en MongoDB.
    
    Args:
        config: Dict con configuración SMTP
            - enabled: bool
            - host: str (smtp.gmail.com, etc.)
            - port: int (587, 465, etc.)
            - username: str
            - password: str (almacenar encriptado en producción)
            - from_email: str
            - use_tls: bool
    
    Returns:
        bool: True si se guardó correctamente
    """
    db = get_database()
    collection = db["system_config"]
    
    try:
        config['updated_at'] = datetime.now()
        
        result = collection.update_one(
            {"type": "smtp_config"},
            {"$set": {
                "type": "smtp_config",
                "config": config,
                "updated_at": config['updated_at']
            }},
            upsert=True
        )
        
        return result.acknowledged
    except Exception as e:
        print(f"Error guardando config SMTP: {e}")
        return False


def get_smtp_config() -> Dict[str, Any]:
    """
    Obtiene configuración SMTP desde MongoDB.
    
    Returns:
        Dict con configuración, o valores por defecto si no existe
    """
    db = get_database()
    collection = db["system_config"]
    
    try:
        doc = collection.find_one({"type": "smtp_config"})
        
        if doc and 'config' in doc:
            return doc['config']
        
        # Valores por defecto
        return {
            'enabled': False,
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': '',
            'password': '',
            'from_email': '',
            'use_tls': True
        }
    except Exception as e:
        print(f"Error obteniendo config SMTP: {e}")
        return {'enabled': False}


def test_smtp_connection(config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Prueba la conexión SMTP con la configuración proporcionada.
    
    Args:
        config: Configuración SMTP a probar
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    import smtplib
    
    try:
        # Intentar conectar
        if config.get('use_tls', True):
            server = smtplib.SMTP(config['host'], config['port'], timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config['host'], config['port'], timeout=10)
        
        # Intentar login
        if config.get('username') and config.get('password'):
            server.login(config['username'], config['password'])
        
        server.quit()
        
        return True, "✅ Conexión exitosa. Configuración SMTP válida."
    
    except smtplib.SMTPAuthenticationError:
        return False, "❌ Error de autenticación. Verifica usuario y contraseña."
    except smtplib.SMTPConnectError:
        return False, "❌ No se pudo conectar al servidor SMTP."
    except TimeoutError:
        return False, "❌ Timeout al conectar. Verifica host y puerto."
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def save_webhook_config(config: Dict[str, Any]) -> bool:
    """
    Guarda configuración de webhook en MongoDB.
    
    Args:
        config: Dict con configuración webhook
            - enabled: bool
            - url: str
            - type: str ("slack", "teams", "generic")
            - secret: str (opcional, para validación)
    
    Returns:
        bool: True si se guardó correctamente
    """
    db = get_database()
    collection = db["system_config"]
    
    try:
        config['updated_at'] = datetime.now()
        
        result = collection.update_one(
            {"type": "webhook_config"},
            {"$set": {
                "type": "webhook_config",
                "config": config,
                "updated_at": config['updated_at']
            }},
            upsert=True
        )
        
        return result.acknowledged
    except Exception as e:
        print(f"Error guardando config webhook: {e}")
        return False


def get_webhook_config() -> Dict[str, Any]:
    """
    Obtiene configuración de webhook desde MongoDB.
    
    Returns:
        Dict con configuración, o valores por defecto si no existe
    """
    db = get_database()
    collection = db["system_config"]
    
    try:
        doc = collection.find_one({"type": "webhook_config"})
        
        if doc and 'config' in doc:
            return doc['config']
        
        # Valores por defecto
        return {
            'enabled': False,
            'url': '',
            'type': 'slack',
            'secret': ''
        }
    except Exception as e:
        print(f"Error obteniendo config webhook: {e}")
        return {'enabled': False}


def test_webhook(url: str, webhook_type: str = 'slack') -> Tuple[bool, str]:
    """
    Envía mensaje de prueba al webhook.
    
    Args:
        url: URL del webhook
        webhook_type: Tipo ("slack", "teams", "generic")
    
    Returns:
        Tuple[bool, str]: (éxito, mensaje)
    """
    import requests
    
    try:
        # Payload según tipo
        if webhook_type == 'slack':
            payload = {
                "text": "🧪 Mensaje de prueba desde Sistema de Triaje IA",
                "attachments": [
                    {
                        "color": "#28a745",
                        "fields": [
                            {"title": "Estado", "value": "Configuración correcta", "short": True},
                            {"title": "Timestamp", "value": datetime.now().isoformat(), "short": True}
                        ]
                    }
                ]
            }
        elif webhook_type == 'teams':
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "summary": "Test de Webhook",
                "title": "🧪 Mensaje de Prueba",
                "text": "Sistema de Triaje IA - Configuración correcta",
                "themeColor": "28a745"
            }
        else:  # generic
            payload = {
                "message": "Test desde Sistema de Triaje IA",
                "timestamp": datetime.now().isoformat()
            }
        
        response = requests.post(
            url,
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return True, "✅ Webhook enviado correctamente. Revisa tu canal."
        else:
            return False, f"❌ Error HTTP {response.status_code}: {response.text[:100]}"
    
    except requests.exceptions.Timeout:
        return False, "❌ Timeout al enviar webhook. Verifica la URL."
    except requests.exceptions.ConnectionError:
        return False, "❌ Error de conexión. Verifica que la URL sea válida."
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
