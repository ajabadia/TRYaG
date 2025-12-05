# Plan de Pruebas - Sistema de Triaje IA

Este documento define la estrategia de pruebas para asegurar la calidad y robustez del sistema antes de su paso a producción real.

## 🎯 Objetivos
1.  **Verificar la lógica de negocio core:** Asegurar que los servicios críticos (asignación, triaje, permisos) funcionan como se espera.
2.  **Garantizar la integridad de datos:** Validar que las operaciones de base de datos (MongoDB) son correctas y manejan errores.
3.  **Asegurar la estabilidad de la UI:** Comprobar que los flujos principales de usuario no tienen errores bloqueantes.

## 🛠️ Stack Tecnológico de Pruebas
*   **Framework Principal:** `pytest` (Estándar en Python, flexible y potente).
*   **Mocking:** `unittest.mock` (Nativo) y `mongomock` (Para simular MongoDB sin base de datos real).
*   **Cobertura:** `pytest-cov` (Para medir qué porcentaje del código está testado).

## 📂 Estructura de Directorios Propuesta
```
tests/
├── unit/                   # Pruebas unitarias (rápidas, sin dependencias externas)
│   ├── services/           # Tests de lógica de negocio
│   ├── repositories/       # Tests de acceso a datos (usando mongomock)
│   └── utils/              # Tests de funciones de utilidad
├── integration/            # Pruebas de integración (componentes interactuando)
├── conftest.py             # Configuración global de pytest y fixtures
└── data/                   # Datos de prueba (fixtures JSON/Dicts)

src/scripts/                # Scripts de verificación manual y utilidades (Legacy/Integration)
```

## 🗓️ Fases de Implementación

### Fase 1: Configuración y Unit Testing (✅ Completada)
Configurar el entorno y cubrir la lógica más crítica y propensa a errores.

1.  **Setup:**
    *   Instalar `pytest`, `pytest-cov`, `mongomock`.
    *   Configurar `conftest.py` con fixtures para MongoDB simulado.

2.  **Servicios Críticos:**
    *   `patient_service.py`: Creación, búsqueda y actualización de pacientes.
    *   `triage_service.py`: Algoritmos de clasificación y cálculo de prioridad.
    *   `staff_assignment_service.py`: Lógica de resolución de conflictos de turnos.
    *   `permissions_service.py`: Validación de roles y accesos.

### Fase 2: Integration Testing (✅ Completada)
Verificar que los repositorios y servicios hablan correctamente con la base de datos (simulada o test DB).

1.  **Repositorios:**
    *   Tests CRUD para `users.py`, `people.py`, `triage_records.py`.
    *   Validación de modelos Pydantic.

### Fase 3: PWA & Offline Testing (✅ Completada)
Verificar la resiliencia del sistema ante fallos de red.

1.  **Service Worker:**
    *   Caché de assets estáticos (CSS, JS, Iconos).
    *   Fallback a `offline.html` en desconexión.

2.  **Sincronización:**
    *   Almacenamiento en `IndexedDB` al crear registros offline.
    *   Evento `window.online` dispara alerta de sincronización.
    *   Carga correcta de datos desde JSON local.

### Fase 4: Advanced Testing (E2E & Load) (✅ Completada)
Simular el comportamiento real del usuario y la carga del sistema.

1.  **End-to-End (E2E) con Playwright:**
    *   **Propósito:** Validar flujos críticos completos (Login -> Triaje -> Alta) en un navegador real.
    *   **Frecuencia:** Ejecutar antes de cada deploy a producción o cambios mayores en UI.
    *   **Comando:** `pytest tests/e2e`

2.  **Pruebas de Carga con Locust:**
    *   **Propósito:** Asegurar que el sistema soporta concurrencia (ej: 50 enfermeros simultáneos).
    *   **Frecuencia:** Ejecutar antes de campañas de despliegue masivo.
    *   **Comando:** `locust -f tests/load/locustfile.py`

## 🚀 Ejecución
Comando estándar:
```bash
$env:PYTHONPATH='src'; pytest tests/ -v
```
