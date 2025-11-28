# Sistema de Usuarios y Permisos (RBAC)

## 1. Descripción General
El sistema implementa un control de acceso basado en roles (RBAC) que permite gestionar la seguridad y la visibilidad de las diferentes secciones de la aplicación. Se distingue entre la identidad física de la persona (`people`) y su cuenta de usuario en el sistema (`users`).

## 2. Modelo de Datos

### 2.1 Personas (`people`)
Representa a una entidad física real. Puede ser un paciente, un empleado o ambos.
- **Colección:** `people` (anteriormente `patients`)
- **Campos Clave:**
  - `_id`: Identificador único.
  - `identification_number`: DNI, NIE o Pasaporte (Indexado).
  - `internal_id`: ID de empleado (opcional).
  - `nombre`, `apellido1`, `apellido2`.
  - `contact_info`: Array de métodos de contacto.

### 2.2 Usuarios (`users`)
Representa la cuenta de acceso al sistema.
- **Colección:** `users`
- **Campos Clave:**
  - `username`: Login único.
  - `person_id`: Referencia a `people`.
  - `rol`: Código del rol asignado (ej. `medico`, `administrativo`).
  - `funciones`: Lista de funciones laborales (ej. `medico`, `enfermero`).
  - `sala_asignada`: Código de la sala donde está trabajando actualmente (opcional).
  - `activo`: Booleano para soft-delete.

## 3. Roles y Permisos
Los roles son estáticos y se definen en `src/db/repositories/roles.py`.

| Rol | Código | Nivel | Descripción |
|-----|--------|-------|-------------|
| **Super Admin** | `superadministrador` | 100 | Acceso total al sistema y configuración avanzada. |
| **Administrador** | `administrador` | 80 | Gestión del centro y usuarios. Sin acceso a auditoría técnica profunda. |
| **Usuario Clínico** | `usuario` | 50 | Personal sanitario (Médicos, Enfermeros). Acceso a flujo de pacientes. |
| **Auditor** | `auditor` | 20 | Solo lectura de datos y métricas. Sin interacción con pacientes. |

### Estructura de Permisos
Cada rol tiene un diccionario de `permissions` que define qué módulos puede ver o editar:
```python
"permissions": {
    "admision": {"view": True, "create": True, ...},
    "auditoria": {"view": False},
    "configuracion": {
        "general": True,
        "usuarios": False
    }
}
```

## 4. Funciones del Personal
Definen el "puesto de trabajo" y se usan para la UI (badges, colores) y lógica de asignación. Definidas en `src/db/repositories/funciones.py`.

- **Médico** (`medico`): Color Verde. Icono `health_and_safety`.
- **Enfermero** (`enfermero`): Color Azul. Icono `medical_services`.
- **Administrativo** (`administrativo`): Color Gris. Icono `badge`.
- **Analista** (`analista_datos`): Color Amarillo. Icono `analytics`.

## 5. Implementación Técnica

### 5.1 Servicio de Permisos (`src/services/permissions_service.py`)
Es el middleware encargado de verificar accesos.
- `get_current_user()`: Obtiene el usuario de `st.session_state`.
- `has_permission(module, action)`: Verifica si el usuario actual puede realizar una acción.
- `get_available_tabs()`: Retorna las pestañas visibles para el usuario.

### 5.2 Selector de Usuario (Dev/Testing)
Componente `src/components/common/user_selector.py` ubicado en la barra lateral. Permite cambiar la identidad del usuario en tiempo real para probar diferentes perfiles sin necesidad de logout/login.

### 5.3 Gestión de Usuarios
Interfaz gráfica en `Configuración > Usuarios` (`src/ui/config/usuarios_manager.py`). Permite:
- Crear nuevos usuarios (vinculándolos automáticamente a `people`).
- Editar roles y funciones.
- Activar/Desactivar acceso.

## 6. Guía de Uso para Desarrolladores

### Proteger una nueva funcionalidad
Para ocultar un botón o sección basado en permisos:

```python
from services.permissions_service import has_permission

if has_permission("configuracion", "usuarios"):
    st.button("Borrar Usuario")
```

### Obtener usuario actual
```python
from services.permissions_service import get_current_user

user = get_current_user()
print(f"Hola {user['nombre_completo']}")
```
