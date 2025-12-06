# Directivas de Codificación del Usuario

## Idioma

- Todas las comunicaciones y comentarios en el código deben ser en **Español (Castellano)**.

## Cabeceras de Archivo

Todos los archivos creados o modificados deben incluir obligatoriamente las siguientes líneas al principio (ajustando el formato de comentario según el lenguaje):

```python
# path: <ruta/relativa/del/archivo>
# Creado: <YYYY-MM-DD>
# Última modificación: <YYYY-MM-DD>
```

## Comentarios

- Se deben comentar todos los archivos creados y modificados para explicar su propósito y funcionalidad.

## Estilo de Iconos

- Los iconos deben seguir el estilo **Material Design** (similar a Angular Material).
- Se debe priorizar el uso de iconos SVG o la sintaxis `:material/...:` de Streamlit frente a emojis genéricos, para mantener una apariencia profesional y consistente.
- Evitar el uso de emojis si existe una alternativa clara en Material Design.

## Organización de Documentación

- **Documentación finalizada:** Guardar en la carpeta `docs/`
- **Documentos de trabajo en progreso:** Guardar en `docs/inProgress/`
- **Documentos finalizados/archivados:** Mover a `docs/finished/`
- Los documentos deben tener nombres descriptivos y seguir la convención: `NOMBRE_EN_MAYUSCULAS.md`

## Filosofía de Código

- **Preferencia por archivos pequeños y modulares:** Dividir la funcionalidad en archivos separados pequeños en lugar de archivos grandes monolíticos.
- **Reutilización (DRY - Don't Repeat Yourself):** Crear componentes reutilizables que puedan importarse desde múltiples lugares.
- **Un archivo = Una responsabilidad:** Cada archivo debe tener una responsabilidad clara y bien definida.
- **Máximo recomendado:** ~300-400 líneas por archivo. Si se excede, considerar dividir en módulos.
- **Estructura modular:** Agrupar archivos relacionados en carpetas/módulos con `__init__.py` apropiados.

**Ejemplos de buena modularidad:**

```
✅ BIEN:
src/ui/config/
  ├── __init__.py
  ├── datos_generales.py  (150 líneas)
  ├── salas_manager.py    (200 líneas)
  └── usuarios_manager.py (180 líneas)

❌ MAL:
src/ui/
  └── config_panel.py     (800 líneas con todo mezclado)
```

## Copias de Seguridad y Recuperación de Código

- El usuario **realiza copias de seguridad recurrentes** del proyecto completo.
- Si se produce algún error de corrupción de archivos o pérdida de código durante la sesión:
  - **Se puede solicitar al usuario el código original** de cualquier archivo para restaurarlo.
  - El usuario puede proporcionar el contenido actualizado desde su última copia de seguridad.
- Esto permite recuperarse rápidamente de errores sin pérdida de trabajo previo.

## Etiquetas de Depuración en Componentes

- **Requisito:** Cada componente visual principal (función `render_...`) debe incluir al final de su ejecución una etiqueta discreta que indique la ruta del archivo fuente.
- **Propósito:** Facilitar la identificación rápida del archivo que genera cada parte de la UI durante el desarrollo y mantenimiento.
- **Formato:** Texto gris, tamaño pequeño, alineado a la derecha.
- **Snippet de código:**

```python
st.markdown('<div class="debug-footer">src/components/ruta/al/componente.py</div>', unsafe_allow_html=True)
```

- **Ubicación:** Justo antes de terminar la función de renderizado del componente.
- **Nota:** Asegurarse de no duplicar esta etiqueta si ya existe.

---

# Patrones de Diseño y Soluciones Estandarizadas (Nuevos)

## 1. Descargas de Archivos Fiables (Server-Side Fix)

**Problema:** `st.download_button` de Streamlit puede fallar en ciertos navegadores (especialmente Chrome) o entornos embebidos si el archivo es grande o si hay problemas con el manejo de Data URIs / Blobs en el cliente. También puede fallar el nombrado del archivo (`file_name`).

**Solución Estandarizada:** Servir el archivo estáticamente desde el servidor usando **Tornado** (el servidor subyacente de Streamlit) y enlazarlo con una etiqueta HTML `<a>` estándar.

### Implementación

#### Backend (`src/utils/tornado_server.py`)
Existe un helper que inyecta rutas personalizadas en la instancia de Tornado de Streamlit.

```python
# src/utils/tornado_server.py
from utils.tornado_server import mount_video_upload_route

# Llamar esto al inicio de app.py (fuera del loop principal si es posible, o cacheado)
mount_video_upload_route(route_download="/download_file_v7")
```

El handler `FileDownloadHandler` sirve archivos desde el directorio `temp/` validando que no haya *path traversal*.

#### Frontend (Componente UI)
En lugar de `st.download_button`:

1. Guárdalo en el directorio temporal:
   ```python
   import os
   temp_dir = 'temp'
   os.makedirs(temp_dir, exist_ok=True)
   temp_path = os.path.join(temp_dir, filename)
   with open(temp_path, "wb") as f:
       f.write(file_bytes)
   ```

2. Genera el enlace de descarga:
   ```python
   download_url = f"/download_file_v7?filename={filename}"
   
   st.markdown(f'''
       <a href="{download_url}" target="_blank" style="text-decoration:none;">
           <div style="
               display: inline-flex;
               align-items: center;
               justify-content: center;
               padding: 0.25rem 0.75rem;
               border-radius: 0.5rem;
               background-color: #ff4b4b; /* Color primario */
               color: white;
               cursor: pointer;
           ">
               ⬇️ Descargar (Server)
           </div>
       </a>
   ''', unsafe_allow_html=True)
   ```

---

## 2. Manejo de Contexto Híbrido (Streamlit vs FastAPI)

**Problema:** El código compartido (como modelos de Pydantic o utilidades de DB) puede fallar si intenta importar `streamlit` cuando es ejecutado desde FastAPI (donde no existe el contexto de Streamlit).

**Solución:**
- Evitar imporar `streamlit` en el nivel superior de módulos de servicio (`src/services`).
- Usar imports locales dentro de funciones si se necesita `st.session_state` o `st.secrets`.
- Para configuración, usar repositorios (`src/db/repositories/config.py`) que abstraen la fuente (DB, JSON, o Secrets).

---

## 3. Integración de IA Generativa

- **Prompt Management:** NUNCA hardcodear prompts en el código. Usar `src/services/db/repositories/prompt_repository.py` para cargarlos de BD.
- **Failover:** Si la BD falla, tener un fallback básico (simple string) en el código, pero logueando el error.
- **Auditoría:** TODAS las llamadas a la IA deben pasar por `GeminiService.generate_content`, que maneja el log en `ia_audit_logs`.
