# Configuración de Notificaciones - Guía Completa

**Fecha:** 2025-12-05  
**Versión:** 1.1  
**Estado:** ✅ Implementado

---

## 📋 Resumen

El sistema de notificaciones soporta múltiples canales de envío:
- **IN_APP:** Notificaciones dentro de la aplicación (siempre activo)
- **EMAIL:** Envío vía SMTP
- **WEBHOOK:** Integración con Slack, Microsoft Teams o webhooks genéricos

Los canales se activan/desactivan dinámicamente según la configuración del sistema.

---

## 🚀 Configuración Rápida

### 1. Acceder a Configuración
1. Ir a **Configuración** → pestaña **Notificaciones**
2. Seleccionar sub-pestaña **Email (SMTP)** o **Webhooks**

### 2. Configurar SMTP (Gmail Ejemplo)

```
✅ Activar envío de emails

Servidor SMTP: smtp.gmail.com
Puerto: 587
Usuario SMTP: tu-email@gmail.com
Password: [App Password de Gmail]
Email remitente: tu-email@gmail.com
☑ Usar TLS
```

**Crear App Password en Gmail:**
1. Ir a [myaccount.google.com/security](https://myaccount.google.com/security)
2. Activar verificación en 2 pasos (si no está)
3. Buscar "App passwords" (Contraseñas de aplicaciones)
4. Generar nueva password para "Mail"
5. Copiar el código de 16 caracteres
6. Usarlo en "Password" (no tu contraseña normal)

### 3. Configurar Slack Webhook

```
✅ Activar webhooks

Tipo: 💬 Slack
URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Obtener Webhook URL:**
1. Ir a [api.slack.com/apps](https://api.slack.com/apps)
2. Crear app o seleccionar existente
3. Activar "Incoming Webhooks"
4. "Add New Webhook to Workspace"
5. Seleccionar canal
6. Copiar Webhook URL

### 4. Probar Configuración

Usar botones "🧪 Probar Conexión" / "🧪 Enviar Mensaje de Prueba"

---

## 📧 Configuración SMTP por Proveedor

### Gmail
```
Host: smtp.gmail.com
Puerto: 587
TLS: ✅ Activado
Autenticación: Requiere App Password
```

### Outlook / Office 365
```
Host: smtp.office365.com
Puerto: 587
TLS: ✅ Activado
Autenticación: Email y contraseña normal
```

### Yahoo
```
Host: smtp.mail.yahoo.com
Puerto: 587
TLS: ✅ Activado
Autenticación: Requiere App Password
```

### SMTP Personalizado
```
Host: [Tu servidor SMTP]
Puerto: 587 (TLS) o 465 (SSL)
TLS: Según tu configuración
```

---

## 🔗 Configuración de Webhooks

### Slack
- **Tipo:** `slack`
- **Formato:** Mensaje con attachments coloreados
- **Documentación:** [api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks)

### Microsoft Teams
- **Tipo:** `teams`
- **Formato:** MessageCard
- **Documentación:** [docs.microsoft.com/connectors](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using)

### Webhook Genérico
- **Tipo:** `generic`
- **Formato:** JSON POST request
- **Headers:** `Content-Type: application/json`

**Ejemplo de payload genérico:**
```json
{
  "title": "Error de Asignación - Sala SALA_X",
  "message": "El paciente Juan Pérez (PAT_001) está asignado...",
  "category": "room_error",
  "priority": "critical",
  "timestamp": "2025-11-25T19:30:00",
  "metadata": {
    "patient_code": "PAT_001",
    "patient_name": "Juan Pérez",
    "sala_erronea": "SALA_X",
    "motivo": "Sala inexistente"
  }
}
```

---

## 🎯 Canales Dinámicos por Prioridad

El sistema determina automáticamente qué canales usar:

| Prioridad | Canales Utilizados |
|-----------|-------------------|
| **CRITICAL** | IN_APP + EMAIL + WEBHOOK<br>(todos los configurados) |
| **HIGH** | IN_APP + EMAIL + WEBHOOK<br>(todos los configurados) |
| **MEDIUM** | IN_APP + EMAIL<br>(si está configurado) |
| **LOW** | IN_APP solamente |

**Ejemplo:**
- Error de "Sala inexistente" → CRITICAL → se envía por todos los canales
- Error de "Sala inactiva" → HIGH → se envía por todos los canales
- Resolución de error → LOW → solo IN_APP

---

## 🔧 Personalizar Notificaciones

### Cambiar Canales para una Notificación Específica

**Archivo:** `src/services/notification_service.py`

```python
# Ubicar la función helper (ej: notify_room_error_detected)

return create_notification(
    title=...,
    message=...,
    priority=...,
    # En lugar de:
    # channels=get_channels_for_priority(priority.value),
    
    # Usar canales específicos:
    channels=[
        NotificationChannel.IN_APP,
        NotificationChannel.EMAIL,
        NotificationChannel.WEBHOOK
    ],
    ...
)
```

### Forzar Canal Específico

```python
# Solo email
channels=[NotificationChannel.EMAIL]

# Solo webhook
channels=[NotificationChannel.WEBHOOK]

# IN_APP + Email
channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL]
```

---

## 📨 Templates de Email

Los emails utilizan templates HTML responsivos con diseño profesional.

**Ubicación:** `src/templates/email_templates.py`

**Templates disponibles:**
- `render_room_error_email()` - Errores de sala
- `render_patient_update_email()` - Actualizaciones de paciente
- `render_system_alert_email()` - Alertas del sistema
- `render_generic_email()` - Genérico para cualquier categoría

### Personalizar Templates

Editar archivos en `src/templates/email_templates.py`:

```python
def render_room_error_email(notification: Dict) -> str:
    # Modificar HTML aquí
    return f"""
    <!DOCTYPE html>
    <html>
    ...
    </html>
    """
```

---

## 🛠️ Solución de Problemas

### Email no se envía

**1. Verificar configuración:**
- ✅ "Activar envío de emails" está marcado
- ✅ Todos los campos están completados
- ✅ Password es correcto (App Password para Gmail)

**2. Probar conexión:**
- Usar botón "🧪 Probar Conexión"
- Revisar mensaje de error

**Errores comunes:**
- `SMTPAuthenticationError`: Contraseña incorrecta o falta App Password
- `SMTPConnectError`: Host o puerto incorrecto
- `Timeout`: Firewall bloqueando puerto

**3. Verificar logs:**
- Los errores se imprimen en consola
- Buscar mensajes que empiecen con "Error enviando email:"

### Webhook no funciona

**1. Verificar URL:**
- Copiar URL completa desde Slack/Teams
- Incluir `https://`

**2. Probar con mensaje de prueba:**
- Botón "🧪 Enviar Mensaje de Prueba"
- Verificar que llega al canal correcto

**3. Revisar tipo:**
- Slack requiere tipo "slack"
- Teams requiere tipo "teams"

### Notificaciones no aparecen en IN_APP

- El canal IN_APP está siempre activo
- Verificar pestaña "Notificaciones" en Control de Salas
- Revisar filtros (Solo no leídas, Categoría)

---

## 📊 Monitoreo

### Ver Estado de Envío

**Colección MongoDB:** `notifications`

**Campo:** `sent_status`

```javascript
{
  "sent_status": {
    "in_app": true,      // Siempre true
    "email": true/false/null,  // true: enviado, false: error, null: no intentado
    "webhook": true/false/null
  }
}
```

### Query para Ver Fallos

```javascript
// Emails fallidos
db.notifications.find({
  "sent_status.email": false
})

// Webhooks fallidos
db.notifications.find({
  "sent_status.webhook": false
})
```

---

## 🔐 Seguridad

### Almacenamiento de Passwords

**Actual:** Passwords se guardan en texto plano en MongoDB (colección `system_config`)

**⚠️ Recomendación para Producción:**
1. Usar variables de entorno en lugar de BD
2. Encriptar passwords antes de guardar
3. Usar servicios de gestión de secretos (AWS Secrets Manager, Azure Key Vault)

**Ejemplo con variables de entorno:**

```python
import os

smtp_config = {
    'username': os.getenv('SMTP_USERNAME'),
    'password': os.getenv('SMTP_PASSWORD'),
    ...
}
```

### Webhooks

- Las URLs de webhook incluyen tokens secretos
- No compartir públicamente
- Regenerar periódicamente en Slack/Teams
- Para webhooks genéricos, usar autenticación adicional (campo `secret`)

---

## 📚 Referencia API

### Crear Notificación Manual

```python
from services.notification_service import (
    create_notification,
    NotificationChannel,
    NotificationPriority,
    NotificationCategory
)

notification_id = create_notification(
    title="Título de la Notificación",
    message="Mensaje detallado...",
    category=NotificationCategory.SYSTEM_ALERT,
    priority=NotificationPriority.HIGH,
    channels=[
        NotificationChannel.IN_APP,
        NotificationChannel.EMAIL
    ],
    recipients=["admin", "user_123"],
    metadata={"custom_field": "value"}
)
```

### Helpers Disponibles

```python
from services.notification_service import (
    notify_room_error_detected,
    notify_room_error_resolved
)

# Notificar error (canales automáticos según prioridad)
notify_room_error_detected(
    patient_code="PAT_001",
    patient_name="Juan Pérez",
    sala_erronea="SALA_X",
    motivo="Sala inexistente"
)

# Notificar resolución
notify_room_error_resolved(
    patient_code="PAT_001",
    patient_name="Juan Pérez",
    sala_antigua="SALA_X",
    sala_nueva="SALA_Y"
)

# Notificar nuevo turno
notify_shift_created(
    user_name="Dr. García",
    sala_code="BOX-01",
    fecha_desde=datetime(2025, 12, 1),
    fecha_hasta=datetime(2025, 12, 1),
    horario="08:00 - 15:00"
)
```

---

## ✅ Checklist de Implementación

- [x] Repositorio de configuración
- [x]Templates HTML para emails
- [x] Funciones de envío SMTP
- [x] Funciones de envío Webhook
- [x] UI de configuración
- [x] Testing integrado
- [x] Canales dinámicos
- [x] Helpers para errores de sala
- [x] Documentación completa

### Pendientes (Opcional)
- [ ] Encriptación de passwords
- [ ] Variables de entorno
- [ ] Tests unitarios
- [ ] Retry automático en fallos
- [ ] Queue de envío asíncrono
- [ ] Dashboard de métricas de notificaciones

---

**Autor:** Sistema de Triaje IA  
**Última actualización:** 2025-11-25
