# path: src/ui/config/notification_config_ui.py
# Creado: 2025-11-25
"""
UI para configuración de notificaciones (SMTP y Webhooks).
Componente modular y reutilizable.
"""
import streamlit as st
from db.repositories.notification_config import (
    get_smtp_config,
    save_smtp_config,
    test_smtp_connection,
    get_webhook_config,
    save_webhook_config,
    test_webhook
)


def render_smtp_config():
    """Renderiza sección de configuración SMTP."""
    
    st.markdown("### 📧 Configuración de Email (SMTP)")
    st.markdown("Configura el servidor SMTP para enviar notificaciones por email.")
    
    # Cargar config actual
    smtp_config = get_smtp_config()
    
    with st.container(border=True):
        # Toggle activar/desactivar
        smtp_enabled = st.toggle(
            "Activar envío de emails",
            value=smtp_config.get('enabled', False),
            help="Habilita o deshabilita el envío de notificaciones por email"
        )
        
        if smtp_enabled:
            st.markdown("---")
            
            # Servidor y puerto
            col1, col2 = st.columns(2)
            with col1:
                smtp_host = st.text_input(
                    "Servidor SMTP",
                    value=smtp_config.get('host', 'smtp.gmail.com'),
                    help="Ejemplo: smtp.gmail.com, smtp.office365.com"
                )
            with col2:
                smtp_port = st.number_input(
                    "Puerto",
                    min_value=1,
                    max_value=65535,
                    value=smtp_config.get('port', 587),
                    help="587 (TLS) o 465 (SSL)"
                )
            
            # Credenciales
            col3, col4 = st.columns(2)
            with col3:
                smtp_username = st.text_input(
                    "Usuario SMTP",
                    value=smtp_config.get('username', ''),
                    help="Usualmente tu dirección de email completa"
                )
            with col4:
                smtp_password = st.text_input(
                    "Contraseña",
                    value=smtp_config.get('password', ''),
                    type="password",
                    help="Contraseña de la cuenta o App Password"
                )
            
            # Email remitente
            smtp_from_email = st.text_input(
                "Email remitente",
                value=smtp_config.get('from_email', ''),
                help="Dirección de email que aparecerá como remitente"
            )
            
            # TLS/SSL
            use_tls = st.checkbox(
                "Usar TLS (recomendado para puerto 587)",
                value=smtp_config.get('use_tls', True)
            )
            
            st.markdown("---")
            
            # Botones de acción
            col_save, col_test = st.columns(2)
            
            with col_save:
                if st.button("💾 Guardar Configuración SMTP", type="primary", use_container_width=True):
                    new_config = {
                        'enabled': smtp_enabled,
                        'host': smtp_host,
                        'port': smtp_port,
                        'username': smtp_username,
                        'password': smtp_password,
                        'from_email': smtp_from_email,
                        'use_tls': use_tls
                    }
                    
                    if save_smtp_config(new_config):
                        st.success("✅ Configuración SMTP guardada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar configuración")
            
            with col_test:
                if st.button("🧪 Probar Conexión", use_container_width=True):
                    test_config = {
                        'host': smtp_host,
                        'port': smtp_port,
                        'username': smtp_username,
                        'password': smtp_password,
                        'from_email': smtp_from_email,
                        'use_tls': use_tls
                    }
                    
                    with st.spinner("Probando conexión SMTP..."):
                        success, message = test_smtp_connection(test_config)
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            
            # Ayuda
            with st.expander("💡 Ayuda - Configuración SMTP"):
                st.markdown("""
                **Servidores SMTP comunes:**
                - **Gmail:** smtp.gmail.com, puerto 587 (TLS)
                  - Requiere "App Password" si tienes 2FA activado
                  - [Crear App Password](https://support.google.com/accounts/answer/185833)
                
                - **Outlook/Office365:** smtp.office365.com, puerto 587 (TLS)
                
                - **Yahoo:** smtp.mail.yahoo.com, puerto 587 (TLS)
                
                **Solución de problemas:**
                - Verifica que el puerto esté correcto
                - Para Gmail, usa una "App Password" en lugar de tu contraseña normal
                - Asegúrate de que "Acceso de apps menos seguras" esté habilitado (si aplica)
                """)
        
        else:
            st.info("📧 El envío de emails está desactivado. Activa el toggle para configurar.")
            
            # Guardar estado desactivado
            if st.button("💾 Guardar (Desactivado)", type="secondary"):
                if save_smtp_config({'enabled': False}):
                    st.success("✅ Guardado")
                    st.rerun()


def render_webhook_config():
    """Renderiza sección de configuración de Webhooks."""
    
    st.markdown("### 🔗 Configuración de Webhooks")
    st.markdown("Envía notificaciones a Slack, Microsoft Teams u otros servicios vía webhook.")
    
    # Cargar config actual
    webhook_config = get_webhook_config()
    
    with st.container(border=True):
        # Toggle activar/desactivar
        webhook_enabled = st.toggle(
            "Activar webhooks",
            value=webhook_config.get('enabled', False),
            help="Habilita o deshabilita el envío de notificaciones vía webhook"
        )
        
        if webhook_enabled:
            st.markdown("---")
            
            # Tipo de webhook
            webhook_type = st.selectbox(
                "Tipo de Webhook",
                options=['slack', 'teams', 'generic'],
                index=['slack', 'teams', 'generic'].index(webhook_config.get('type', 'slack')),
                format_func=lambda x: {
                    'slack': '💬 Slack',
                    'teams': '👥 Microsoft Teams',
                    'generic': '🔗 Webhook Genérico'
                }[x],
                help="El formato del mensaje se adaptará al tipo seleccionado"
            )
            
            # URL del webhook
            webhook_url = st.text_input(
                "URL del Webhook",
                value=webhook_config.get('url', ''),
                help="Copia la URL de tu Incoming Webhook desde Slack o Teams",
                placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
            )
            
            # Secret (opcional)
            webhook_secret = st.text_input(
                "Secret (opcional)",
                value=webhook_config.get('secret', ''),
                type="password",
                help="Token de seguridad si tu webhook lo requiere"
            )
            
            st.markdown("---")
            
            # Botones de acción
            col_save, col_test = st.columns(2)
            
            with col_save:
                if st.button("💾 Guardar Configuración Webhook", type="primary", use_container_width=True):
                    new_config = {
                        'enabled': webhook_enabled,
                        'url': webhook_url,
                        'type': webhook_type,
                        'secret': webhook_secret
                    }
                    
                    if save_webhook_config(new_config):
                        st.success("✅ Configuración de webhook guardada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar configuración")
            
            with col_test:
                if st.button("🧪 Enviar Mensaje de Prueba", use_container_width=True, disabled=not webhook_url):
                    with st.spinner(f"Enviando mensaje de prueba a {webhook_type}..."):
                        success, message = test_webhook(webhook_url, webhook_type)
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            
            # Ayuda según tipo
            with st.expander(f"💡 Ayuda - Configurar {webhook_type.title()}"):
                if webhook_type == 'slack':
                    st.markdown("""
                    **Cómo configurar Slack Webhook:**
                    
                    1. Ve a [api.slack.com/apps](https://api.slack.com/apps)
                    2. Crea una nueva app o selecciona una existente
                    3. Activa "Incoming Webhooks"
                    4. Haz click en "Add New Webhook to Workspace"
                    5. Selecciona el canal donde quieres recibir notificaciones
                    6. Copia la Webhook URL y pégala arriba
                    
                    **Formato del mensaje:**
                    Las notificaciones se enviarán con attachments coloreados según prioridad
                    y campos estructurados.
                    """)
                
                elif webhook_type == 'teams':
                    st.markdown("""
                    **Cómo configurar Microsoft Teams Webhook:**
                    
                    1. Abre Microsoft Teams y ve al canal deseado
                    2. Click en "..." → "Connectors"
                    3. Busca "Incoming Webhook" y configura
                    4. Dale un nombre (ej: "Sistema de Triaje IA")
                    5. Copia la URL proporcionada y pégala arriba
                    
                    **Formato del mensaje:**
                    Las notificaciones se enviarán como MessageCard con el formato
                    estándar de Teams.
                    """)
                
                else:  # generic
                    st.markdown("""
                    **Webhook Genérico:**
                    
                    Se enviará un POST request con JSON en este formato:
                    ```json
                    {
                      "title": "Título de la notificación",
                      "message": "Mensaje detallado",
                      "category": "room_error",
                      "priority": "high",
                      "timestamp": "2025-11-25T19:30:00",
                      "metadata": {...}
                    }
                    ```
                    
                    Tu endpoint debe aceptar POST requests con Content-Type: application/json
                    y retornar HTTP 200 para indicar éxito.
                    """)
        
        else:
            st.info("🔗 Los webhooks están desactivados. Activa el toggle para configurar.")
            
            # Guardar estado desactivado
            if st.button("💾 Guardar (Desactivado)", type="secondary", key="save_webhook_disabled"):
                if save_webhook_config({'enabled': False}):
                    st.success("✅ Guardado")
                    st.rerun()


def render_notification_config_panel():
    """
    Renderiza el panel completo de configuración de notificaciones.
    Combina SMTP y Webhooks.
    """
    st.header("🔔 Configuración de Notificaciones")
    st.markdown("Configura cómo el sistema enviará notificaciones automáticas.")
    
    # Tabs para separar SMTP y Webhook
    tab_smtp, tab_webhook = st.tabs(["📧 Email (SMTP)", "🔗 Webhooks"])
    
    with tab_smtp:
        render_smtp_config()
    
    with tab_webhook:
        render_webhook_config()
    
    # Información adicional
    st.markdown("---")
    with st.expander("ℹ️ Información sobre Notificaciones"):
        st.markdown("""
        ### ¿Cuándo se envían notificaciones?
        
        El sistema puede enviar notificaciones automáticas en los siguientes casos:
        
        - **Errores de Sala (CRITICAL/HIGH):** Cuando se detecta un paciente en una sala inválida
        - **Actualizaciones de Paciente (MEDIUM):** Cambios importantes en el estado de pacientes
        - **Alertas del Sistema (VARIABLE):** Problemas técnicos o administrativos
        
        ### Canales de Notificación
        
        - **IN_APP:** Siempre activo. Las notificaciones aparecen en el panel del sistema
        - **EMAIL:** Si está configurado, se envían emails a los usuarios relevantes
        - **WEBHOOK:** Si está configurado, se envían mensajes a Slack/Teams
        
        ### Configuración por Defecto
        
        Actualmente, todas las notificaciones se crean con canal IN_APP por defecto.
        Para activar EMAIL o WEBHOOK en notificaciones específicas, edita el código
        en los helpers de notificación (ej: `notify_room_error_detected`).
        
        **Ejemplo:**
        ```python
        notify_room_error_detected(
            ...,
            channels=[
                NotificationChannel.IN_APP,
                NotificationChannel.EMAIL,      # Añade email
                NotificationChannel.WEBHOOK     # Añade webhook
            ]
        )
        ```
        """)

    st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/ui/config/notification_config_ui.py</div>', unsafe_allow_html=True)
