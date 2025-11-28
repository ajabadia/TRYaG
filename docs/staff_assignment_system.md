# Sistema Unificado de Asignación de Personal

**Fecha:** 2025-11-26  
**Versión:** 1.0

## 📋 Resumen

Este documento describe cómo funciona el sistema unificado de asignación de personal que resuelve el conflicto entre **asignaciones fijas** y **turnos temporales**.

---

## 🎯 Problema Resuelto

Anteriormente existían dos sistemas independientes para asignar personal a salas:

1. **Asignación Fija** (`sala_asignada` en colección `users`)
   - Permanente
   - Un usuario tiene una sala "por defecto"
   - Ejemplo: Dr. García → BOX-01

2. **Gestión de Turnos** (colección `turnos`)
   - Temporal por fecha y horario
   - Un usuario puede tener turnos en diferentes salas
   - Ejemplo: Dr. García → TRIAJE-01 (Hoy 08:00-15:00)

**Conflicto:** ¿Qué sala prevalece cuando un usuario tiene ambas?

---

## ✅ Solución Implementada

### Regla de Prioridad

```
SI existe turno activo AHORA
    → Usar sala del turno
SINO
    → Usar sala_asignada (asignación fija)
```

### Componentes

#### 1. Servicio Unificado
**Archivo:** `src/services/staff_assignment_service.py`

**Funciones principales:**

- `get_current_user_assignment(user_id, reference_datetime)` 
  - Retorna la sala actual de un usuario considerando turnos y asignación fija

- `get_room_staff(sala_code, reference_datetime)`
  - Retorna el personal asignado a una sala en un momento dado

- `get_user_assignment_info(user_id, reference_datetime)`
  - Información detallada de asignación de un usuario

- `validate_shift_assignment(...)`
  - Valida si se puede crear un turno (detecta conflictos de horario)

- `get_assignment_conflicts_report()`
  - Genera reporte de conflictos entre asignación fija y turnos

#### 2. UI de Visualización
**Archivo:** `src/ui/config/staff_conflicts_viewer.py`

Permite visualizar:
- Conflictos detectados
- Línea de tiempo de asignación por hora
- Detalles de cada usuario

#### 3. Room Cards Actualizadas
**Archivo:** `src/components/common/room_card.py`

Ahora muestra:
- Personal asignado con indicador de tipo:
  - 📌 = Asignación Fija
  - 🕐 = Turno Temporal

---

## 📊 Ejemplos de Uso

### Ejemplo 1: Usuario con Asignación Fija

```python
# Usuario: Dr. García
# sala_asignada: "BOX-01"
# Turnos: Ninguno

# A cualquier hora del día:
get_current_user_assignment("dr_garcia_id")
# → "BOX-01" (asignación fija)
```

### Ejemplo 2: Usuario con Turno Activo

```python
# Usuario: Dr. García
# sala_asignada: "BOX-01"
# Turnos: TRIAJE-01 (08:00-15:00)

# A las 10:00:
get_current_user_assignment("dr_garcia_id", datetime(2025, 11, 26, 10, 0))
# → "TRIAJE-01" (turno activo)

# A las 17:00:
get_current_user_assignment("dr_garcia_id", datetime(2025, 11, 26, 17, 0))
# → "BOX-01" (asignación fija, turno ya terminó)
```

### Ejemplo 3: Obtener Personal de una Sala

```python
# Sala: TRIAJE-01
# Hora: 10:00

staff = get_room_staff("TRIAJE-01", datetime(2025, 11, 26, 10, 0))
# Retorna lista de usuarios con:
# - Datos del usuario
# - assignment_type: "turno" o "fija"
# - sala_actual: código de sala efectiva
```

---

## 🔍 Validaciones

### Validación de Turnos

Al crear un turno, se valida:

1. **No solapamiento de horarios**
   - Un usuario no puede tener dos turnos simultáneos

2. **Advertencia de conflicto con asignación fija**
   - Si el turno es en una sala diferente a `sala_asignada`
   - No bloquea la creación, solo advierte

```python
valid, message = validate_shift_assignment(
    user_id="dr_garcia_id",
    sala_code="TRIAJE-01",
    fecha=date(2025, 11, 26),
    horario_inicio=time(8, 0),
    horario_fin=time(15, 0)
)

if not valid:
    print(f"Error: {message}")
elif message:
    print(f"Advertencia: {message}")
```

---

## 📈 Reporte de Conflictos

El sistema genera automáticamente un reporte de conflictos:

```python
conflicts = get_assignment_conflicts_report()

# Ejemplo de conflicto:
{
    "user_id": "dr_garcia_id",
    "nombre_completo": "Dr. García",
    "fixed_sala": "BOX-01",
    "shift_sala": "TRIAJE-01",
    "fecha": date(2025, 11, 26),
    "horario": "08:00-15:00",
    "severity": "warning"
}
```

**Interpretación:**
- El usuario tiene asignación fija en BOX-01
- Pero tiene turno en TRIAJE-01 hoy de 08:00 a 15:00
- Durante ese horario estará en TRIAJE-01
- Fuera de ese horario estará en BOX-01

---

## 🎨 Visualización en UI

### Room Cards

Las tarjetas de sala ahora muestran el personal con indicadores:

```
👥 Personal Asignado:
● Dr. García (Médico) 🕐
● Enf. López (Enfermero) 📌
```

- 🕐 = Usuario asignado por turno temporal
- 📌 = Usuario asignado de forma fija

### Visor de Conflictos

Accesible desde: **Configuración > Gestión de Personal > Conflictos de Asignación**

Muestra:
- Número total de conflictos
- Usuarios afectados
- Detalle de cada conflicto
- Línea de tiempo por hora

---

## 🔧 Mantenimiento

### Añadir Nuevo Tipo de Asignación

Si en el futuro se añade un tercer tipo de asignación:

1. Actualizar `staff_assignment_service.py`:
   - Modificar `get_current_user_assignment()`
   - Añadir nueva lógica de prioridad

2. Actualizar `room_card.py`:
   - Añadir nuevo icono/badge

3. Actualizar `staff_conflicts_viewer.py`:
   - Incluir nuevo tipo en reportes

### Cambiar Regla de Prioridad

Si se necesita cambiar la regla (ej: asignación fija prevalece):

Modificar en `staff_assignment_service.py`:

```python
def get_current_user_assignment(user_id, reference_datetime):
    # ... código existente ...
    
    # CAMBIAR ORDEN AQUÍ:
    # Opción 1: Turno prevalece (actual)
    if current_shift:
        return current_shift.sala_code
    return user.get("sala_asignada")
    
    # Opción 2: Asignación fija prevalece
    if user.get("sala_asignada"):
        return user.get("sala_asignada")
    if current_shift:
        return current_shift.sala_code
```

---

## 📚 Referencias

- **Servicio:** `src/services/staff_assignment_service.py`
- **UI Conflictos:** `src/ui/config/staff_conflicts_viewer.py`
- **Room Cards:** `src/components/common/room_card.py`
- **Repositorio Turnos:** `src/db/repositories/turnos.py`
- **Repositorio Users:** `src/db/repositories/users.py`

---

## ✅ Estado

- **Implementado:** 2025-11-26
- **Versión:** 1.0
- **Estado:** Producción
- **Próximas mejoras:** Ninguna pendiente
