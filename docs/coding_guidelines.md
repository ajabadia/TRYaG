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
(Contenido existente...)

## Etiquetas de Depuración en Componentes
- **Requisito:** Cada componente visual principal (función `render_...`) debe incluir al final de su ejecución una etiqueta discreta que indique la ruta del archivo fuente.
- **Propósito:** Facilitar la identificación rápida del archivo que genera cada parte de la UI durante el desarrollo y mantenimiento.
- **Formato:** Texto gris, tamaño pequeño, alineado a la derecha.
- **Snippet de código:**
```python
st.markdown('<div style="color: #888; font-size: 0.7em; text-align: right; margin-top: 5px;">src/components/ruta/al/componente.py</div>', unsafe_allow_html=True)
```
- **Ubicación:** Justo antes de terminar la función de renderizado del componente.
- **Nota:** Asegurarse de no duplicar esta etiqueta si ya existe.
- El usuario **realiza copias de seguridad recurrentes** del proyecto completo.
- Si se produce algún error de corrupción de archivos o pérdida de código durante la sesión:
  - **Se puede solicitar al usuario el código original** de cualquier archivo para restaurarlo.
  - El usuario puede proporcionar el contenido actualizado desde su última copia de seguridad.
- Esto permite recuperarse rápidamente de errores sin pérdida de trabajo previo.
