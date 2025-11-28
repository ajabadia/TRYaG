# Documentación Funcional - Asistente de Triaje IA

Este documento describe las funcionalidades, roles y flujos de trabajo del sistema de Asistente de Triaje Inteligente.

## 👥 Roles de Usuario y Permisos

El sistema gestiona el acceso mediante roles definidos en la configuración del centro.

| Rol | Descripción | Permisos Principales |
| :--- | :--- | :--- |
| **Admin** | Administrador del sistema | Acceso total, configuración del centro, gestión de usuarios y roles. |
| **Admisión** | Personal administrativo | Registro de pacientes, búsqueda, gestión de la cola de admisión. |
| **Enfermería** | Enfermeros/as de triaje | Realización de triajes, validación de IA, derivación a salas. |
| **Médico** | Doctores/as | Atención en box, visualización de historial, alta de pacientes. |
| **Gestor** | Supervisor de flujo | Control de salas (Orquestador), reasignación de pacientes. |
| **Auditor** | Auditor de calidad | Acceso al panel de auditoría y análisis de datos. |

## 🔄 Flujos de Trabajo Principales

### 1. Recepción y Admisión
*   **Objetivo:** Identificar al paciente y registrar su llegada.
*   **Proceso:**
    1.  El paciente llega al centro.
    2.  El personal de **Admisión** busca al paciente por DNI/Nombre o crea uno nuevo.
    3.  Se asigna el paciente a la **Sala de Espera de Triaje**.

### 2. Triaje Inteligente (Enfermería)
*   **Objetivo:** Clasificar la urgencia y especialidad del paciente con apoyo de IA.
*   **Proceso:**
    1.  El enfermero/a selecciona un paciente de la lista de espera.
    2.  **Entrada de Datos:**
        *   **Texto:** Motivo de consulta y antecedentes.
        *   **Audio:** Dictado de voz (transcrito automáticamente por Gemini).
        *   **Archivos:** Subida de informes PDF o imágenes.
    3.  **Análisis IA:** El sistema envía los datos a Google Gemini, que devuelve:
        *   Nivel de Urgencia (1-5).
        *   Especialidad sugerida (Traumatología, Medicina General, etc.).
        *   Signos vitales extraídos.
        *   Resumen clínico.
    4.  **Validación:** El enfermero/a revisa la propuesta de la IA. Puede aceptar o modificar el nivel y la especialidad.
    5.  **Derivación:** El paciente es enviado a una **Sala de Espera de Consulta** (Traumatología, etc.) o derivado a otro centro/alta.

### 3. Atención Médica (Box)
*   **Objetivo:** Atender al paciente clasificado.
*   **Proceso:**
    1.  El médico llama al siguiente paciente de su especialidad.
    2.  Visualiza el informe de triaje (motivo, constantes, clasificación).
    3.  Registra la atención y finaliza el proceso (Alta).

### 4. Gestión de Salas (Orquestador)
*   **Objetivo:** Visión global y control del flujo.
*   **Funcionalidades:**
    *   **Mapa de Salas:** Visualización en tiempo real de la ocupación de salas (Espera, Triaje, Boxes).
    *   **Drag & Drop:** Reasignación rápida de pacientes entre salas.
    *   **Alertas:** Detección de cuellos de botella o salas inhabilitadas.

## 📊 Panel de Auditoría y Análisis

Herramienta para la mejora continua y supervisión del sistema IA.

*   **Dashboard:** KPIs de tiempos de espera, distribución de urgencias, concordancia Humano-IA.
*   **Registros:** Tabla detallada de todos los triajes realizados con filtros avanzados.
*   **Feedback:** Sistema para revisar casos donde hubo discrepancia entre la IA y el profesional.
*   **Logs Técnicos:** Monitorización de transcripciones y uso de prompts.

## ⚙️ Configuración

Panel centralizado para adaptar el comportamiento del sistema:
*   **Centro:** Datos del hospital, logo, gestión de salas y usuarios.
*   **IA:** Selección de modelos (Gemini Pro/Flash), edición de Prompts del sistema.
*   **Reglas:** Configuración de umbrales y validaciones.
