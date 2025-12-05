# PWA - Progressive Web App

## 📱 Configuración Completada

La aplicación ahora es una **Progressive Web App** instalable en dispositivos móviles y de escritorio.

### Archivos Creados

1. **`static/manifest.json`** - Manifiesto de la PWA
2. **`static/sw.js`** - Service Worker con caché offline
3. **`static/offline.html`** - Página de fallback sin conexión
4. **`src/components/common/pwa_installer.py`** - Componente de instalación

### Funcionalidades Implementadas

✅ **Instalación en dispositivos**
- Botón de instalación personalizado
- Compatible con Android, iOS, Windows, macOS

✅ **Funcionalidad Offline**
- Caché de recursos estáticos
- Estrategia Network First con fallback
- Página offline personalizada

✅ **Optimizaciones**
- Service Worker con caché inteligente
- Sincronización en background (preparado)
- Push notifications (preparado para futuro)

✅ **Shortcuts**
- Acceso rápido a Admisión
- Acceso rápido a Triaje
- Acceso rápido a Triaje
- Acceso rápido a Boxes

✅ **Sincronización Automática**
- Detección de recuperación de red (`window.online`)
- Alerta visual "Conexión restaurada"
- Subida de datos desde IndexedDB

✅ **Simulación Offline**
- Toggle "Simular Modo Offline" en panel lateral
- Permite probar flujos de contingencia sin desconexión física

✅ **Geolocalización (GPS)**
- Captura de coordenadas nativas del dispositivo
- Integración en formulario de triaje (Contexto Clínico)
- Requiere permiso del navegador

---

## 🎨 Generar Iconos

Los iconos de la PWA deben estar en `static/icons/`. Se necesitan los siguientes tamaños:

### Tamaños Requeridos
- 72x72
- 96x96
- 128x128
- 144x144
- 152x152
- 192x192
- 384x384
- 512x512

### Opción 1: Usar un Generador Online

1. Ir a [https://www.pwabuilder.com/imageGenerator](https://www.pwabuilder.com/imageGenerator)
2. Subir un logo cuadrado (mínimo 512x512)
3. Descargar el paquete de iconos
4. Colocar en `static/icons/`

### Opción 2: Usar ImageMagick (CLI)

```bash
# Instalar ImageMagick
# Windows: choco install imagemagick
# Mac: brew install imagemagick
# Linux: apt-get install imagemagick

# Generar todos los tamaños desde un logo base
convert logo.png -resize 72x72 static/icons/icon-72x72.png
convert logo.png -resize 96x96 static/icons/icon-96x96.png
convert logo.png -resize 128x128 static/icons/icon-128x128.png
convert logo.png -resize 144x144 static/icons/icon-144x144.png
convert logo.png -resize 152x152 static/icons/icon-152x152.png
convert logo.png -resize 192x192 static/icons/icon-192x192.png
convert logo.png -resize 384x384 static/icons/icon-384x384.png
convert logo.png -resize 512x512 static/icons/icon-512x512.png
```

### Opción 3: Usar Python (Pillow)

```python
from PIL import Image
import os

sizes = [72, 96, 128, 144, 152, 192, 384, 512]
logo = Image.open('logo.png')

os.makedirs('static/icons', exist_ok=True)

for size in sizes:
    resized = logo.resize((size, size), Image.LANCZOS)
    resized.save(f'static/icons/icon-{size}x{size}.png')
```

---

## 🚀 Activar PWA en la Aplicación

### Integrar en `app.py`

Añadir al inicio de la función principal:

```python
from components.common.pwa_installer import render_pwa_installer

def main():
    # Activar PWA
    render_pwa_installer()
    
    # ... resto del código
```

### Mostrar Estado PWA (Opcional)

En el panel de configuración o ayuda:

```python
from components.common.pwa_installer import show_pwa_status

# En alguna sección de la UI
show_pwa_status()
```

---

## 📱 Cómo Instalar la App

### En Android (Chrome/Edge)
1. Abrir la app en el navegador
2. Tocar el menú (⋮)
3. Seleccionar "Añadir a pantalla de inicio" o "Instalar app"
4. Confirmar

### En iOS (Safari)
1. Abrir la app en Safari
2. Tocar el botón de compartir (□↑)
3. Seleccionar "Añadir a pantalla de inicio"
4. Confirmar

### En Windows/Mac (Chrome/Edge)
1. Abrir la app en el navegador
2. Buscar el icono de instalación en la barra de direcciones (+)
3. Click en "Instalar"
4. La app se abrirá en una ventana independiente

---

## 🔧 Configuración Avanzada

### Personalizar Colores

Editar `static/manifest.json`:

```json
{
  "theme_color": "#1f77b4",  // Color de la barra de estado
  "background_color": "#ffffff"  // Color de fondo al cargar
}
```

### Añadir Más Shortcuts

Editar `static/manifest.json` sección `shortcuts`:

```json
{
  "name": "Nuevo Módulo",
  "url": "/?tab=modulo",
  "icons": [{"src": "/static/icons/shortcut-modulo.png", "sizes": "96x96"}]
}
```

### Modificar Estrategia de Caché

Editar `static/sw.js` función `fetch`:

- **Network First:** Intenta red primero, fallback a caché (actual)
- **Cache First:** Intenta caché primero, fallback a red
- **Stale While Revalidate:** Devuelve caché y actualiza en background

---

## ✅ Verificar Instalación

### Chrome DevTools

1. Abrir DevTools (F12)
2. Ir a pestaña "Application"
3. Verificar:
   - **Manifest:** Debe mostrar el manifest.json
   - **Service Workers:** Debe estar "activated and running"
   - **Cache Storage:** Debe mostrar las cachés creadas

### Lighthouse Audit

1. Abrir DevTools (F12)
2. Ir a pestaña "Lighthouse"
3. Seleccionar "Progressive Web App"
4. Click en "Generate report"
5. Verificar que pase los criterios PWA

---

## 🎯 Próximos Pasos (Opcional)

- [x] Sincronización en background de datos (Implementado con Auto-Sync)
- [x] Modo offline completo con base de datos local (Implementado con IndexedDB)
- [ ] Actualización automática de la app

---

## 🔔 Notificaciones Push (VAPID)

Para habilitar las notificaciones push nativas, se requieren claves VAPID.

### Claves Generadas (Entorno Piloto)

> [!IMPORTANT]
> Estas claves deben configurarse en las variables de entorno o `st.secrets`.

*   **VAPID_PRIVATE_KEY:** `----83r3FwayUAJCog-Th_40mO`
*   **VAPID_PUBLIC_KEY:** `BM-83r3FwayUAJCog-Th_40mO...` (Truncado por seguridad, ver output de generación)
*   **VAPID_SUBJECT:** `mailto:admin@tryag.com`

### Generación de Nuevas Claves

Si necesitas rotar las claves, ejecuta el script incluido:

```bash
python scripts/generate_vapid.py
```

### Configuración en `st.secrets`

```toml
[vapid]
private_key = "..."
public_key = "..."
subject = "mailto:admin@tryag.com"
```

---

## 📚 Referencias
- [PWA Builder](https://www.pwabuilder.com/)
- [MDN - Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Google - PWA Checklist](https://web.dev/pwa-checklist/)
- [Web Push Protocol](https://tools.ietf.org/html/rfc8030)
