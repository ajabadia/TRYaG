# path: src/ui/config/__init__.py
# Creado: 2025-11-25
"""
Módulo de componentes de configuración.
Contiene UI para diferentes secciones de configuración del sistema.
"""
from .notification_config_ui import (
    render_smtp_config,
    render_webhook_config,
    render_notification_config_panel
)

__all__ = [
    'render_smtp_config',
    'render_webhook_config',
    'render_notification_config_panel'
]
