# Sistema de Indicadores de Carga para Operaciones de Base de Datos

## Resumen
Se ha implementado un sistema centralizado de indicadores de carga para mejorar la experiencia del usuario durante las operaciones de base de datos, que pueden ser lentas.

## Componentes Creados

### 1. `src/ui/loading_indicator.py`
Componente centralizado que proporciona:
- **`render_loading_container()`**: Renderiza el contenedor de loading en la interfaz
- **`loading_data(message)`**: Context manager para envolver operaciones de BD
- **`show_loading(message)`** y **`hide_loading()`**: Control manual del indicador

### Uso del Context Manager
```python
from ui.loading_indicator import loading_data

# Envolver operaciones de BD con el indicador
with loading_data("Cargando datos de auditoría..."):
    audit_records = audit_repo.get_recent(limit=1000)
    files_records = files_repo.get_recent(limit=1000)
```

## Archivos Modificados

### 1. `src/app.py`
- ✅ Añadido import de `render_loading_container`
- ✅ Renderizado del contenedor justo después del header (línea 151)
- El contenedor se muestra en una posición fija, visible desde todas las pestañas

### 2. `src/ui/audit_panel/main_panel.py`
- ✅ Integrado `loading_data` al cargar datos de auditoría
- Muestra "Cargando datos de auditoría desde la base de datos..." mientras se recuperan:
  - audit_records
  - files_records  
  - trans_records

### 3. `src/components/audit/prompt_log.py`
- ✅ Integrado `loading_data` en `load_prompts_dataframe()`
- Muestra "Cargando historial de prompts..." durante la carga

### 4. `src/components/analytics/prompt_analysis.py`
- ✅ Integrado `loading_data` en `load_prompts_data()`
- Muestra "Cargando datos de prompts para análisis..." durante la carga

## Características

### Ventajas del Diseño
1. **Centralizado**: Un solo contenedor en la parte superior, visible desde cualquier pestaña
2. **No invasivo**: No requiere modificar mucho código existente
3. **Fácil de usar**: Context manager simple (`with loading_data(...)`)
4. **Consistente**: Mismo estilo y posición en toda la aplicación
5. **Automático**: Se oculta automáticamente al finalizar la operación

### Apariencia
- Icono de sincronización animado (`:material/sync:`)
- Mensaje personalizable
- Estilo `st.info()` para buena visibilidad sin ser intrusivo

## Próximos Pasos (Opcional)

Si se desea extender el sistema, se puede añadir a:
- Carga de configuración del centro
- Operaciones de guardado en BD
- Carga de datos en gestión de salas
- Cualquier otra operación que acceda a MongoDB

## Ejemplo de Integración Futura

```python
# En cualquier archivo que haga operaciones de BD:
from ui.loading_indicator import loading_data

def mi_funcion_que_carga_datos():
    with loading_data("Cargando datos del centro..."):
        # Operaciones de BD aquí
        datos = repositorio.get_all()
    
    # Procesar datos (el indicador ya se ocultó automáticamente)
    return procesar(datos)
```

---
**Fecha de implementación**: 2025-11-25
**Autor**: Sistema de IA Antigravity
