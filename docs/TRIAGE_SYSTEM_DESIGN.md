# Diseño del Sistema de Triaje Avanzado (TRYaGE 2.0)

Este documento consolida los requisitos y el diseño para la actualización mayor del sistema de triaje, basado en el estudio proporcionado.

## 1. Visión General
El objetivo es transformar la aplicación actual en un sistema de triaje clínico completo, que incluya monitorización detallada de signos vitales, lógica de priorización basada en reglas ("peor caso"), gestión dinámica de colas, roles de usuario, auditoría y asistencia avanzada por IA (Gemini).

## 2. Modelo de Datos Clínicos

### 2.1 Signos Vitales y Parámetros
Se monitorizarán los siguientes 7 pilares, con sus respectivos rangos de clasificación (Verde, Amarillo, Naranja, Rojo).

| Métrica | Unidad | Rango Normal (🟢) | Amarillo (🟡) | Naranja (🟠) | Rojo (🔴) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Frecuencia Cardíaca (FC)** | ppm | 60-100 | 50-59 / 101-120 | 40-49 / 121-140 | <40 / >140 |
| **Presión Arterial (PAS)** | mmHg | 100-129 | 90-99 / 130-159 | 80-89 / 160-179 | <80 / >180 |
| **Saturación O2 (SpO2)** | % | 95-100 | 93-94 | 90-92 | <90 |
| **Temperatura (T)** | °C | 36.5-37.5 | 35.0-36.4 / 37.6-37.9 | <35.0 / 38.0-39.9 | <34.0 / >40.0 |
| **Frecuencia Resp. (FR)** | rpm | 12-20 | 8-11 / 21-24 | 6-7 / 25-29 | <6 / >30 |
| **Glasgow (GCS)** | pts | 15 | 13-14 | 9-12 | 3-8 |
| **Dolor (EVA)** | 0-10 | 0-3 | 4-6 | 7-8 | 9-10 |

**Adicionales:**
*   **Reacción Pupilar:** Normal (🟢), Lenta (🟡), Fijas (🟠), Anisocoria/Puntiformes (🔴).
*   **Oxígeno Suplementario:** Booleano (Sí/No).
*   **Datos Administrativos:** Nombre, Edad, ID, Alergias (Crítico), Antecedentes, Motivo Consulta.

### 2.2 Lógica de Clasificación ("Peor Caso")
El color final del triaje se determina por la métrica con mayor gravedad presente.
*   Jerarquía: 🔴 Rojo > 🟠 Naranja > 🟡 Amarillo > 🟢 Verde.
*   Ejemplo: Si todo es Verde pero SpO2 es Rojo -> Resultado Final: **ROJO**.

## 3. Funcionalidades Clave

### 3.1 Gestión de Fila de Espera Dinámica
*   **Priorización:** 1º Por Color (Gravedad), 2º Por Tiempo de Espera.
*   **Alertas de Tiempo:**
    *   🔴 Rojo: Inmediato (0-10 min)
    *   🟠 Naranja: 10-30 min
    *   🟡 Amarillo: 30-90 min
    *   🟢 Verde: 90-120 min
*   **Visualización:** Panel en tiempo real con contadores. Alerta visual (parpadeo/color) si se excede el tiempo máximo.

### 3.2 Reevaluación (Re-triage)
*   Capacidad de volver a evaluar a un paciente en espera.
*   El sistema debe mantener el historial pero usar el último registro para la prioridad en la cola.
*   Permite simular deterioro o mejora (ej. tras oxígeno).

### 3.3 Roles y Auditoría
*   **Roles:**
    *   **Enfermera:** Crear triaje, Reevaluar.
    *   **Supervisor/Médico:** Ver historial completo, Atender (sacar de cola), Configurar rangos.
*   **Auditoría:** Registro de quién (ID_Usuario) realizó cada acción (creación, reevaluación, atención).

### 3.4 Configuración de Rangos
*   Pantalla exclusiva para Supervisores.
*   Permite ajustar los umbrales numéricos de los colores para FC, PA, SpO2, etc.
*   Validación lógica (ej. umbral bajo < umbral alto).

### 3.5 Informes
*   Generación de "Hoja de Triaje" (PDF/HTML).
*   Incluye: Datos paciente, Clasificación Final (Color + Motivo), Tabla de signos vitales, Usuario evaluador.

## 4. Integración de IA (Gemini)

### 4.1 Alerta Predictiva (Reglas + IA)
*   **Factor de Riesgo Predictivo (FR-P):** Si hay 2+ signos vitales en Amarillo -> Sugerir subir prioridad (ej. Verde -> Amarillo).
*   **Análisis Multimodal:**
    *   **Imágenes:** Análisis de heridas/erupciones para ajustar gravedad.
    *   **Texto (NLP):** Análisis de transcripciones para detectar palabras clave de riesgo (dolor "insoportable", ansiedad) y extraer síntomas.
    *   **Razonamiento Avanzado:** Gemini como motor de decisión final para casos complejos, integrando datos numéricos, visuales y textuales.

## 5. Estructura de Base de Datos Propuesta

### Tablas Nuevas/Modificadas
1.  **Pacientes:** (Maestro) ID, Nombre, FechaNac, Alergias, Antecedentes, Estado_Actual.
2.  **Historial_Triaje:** (Eventos) ID_Registro, ID_Paciente, Fecha, Signos Vitales (FC, PA, etc.), Color_Final, Motivo_Urgencia, Es_Reevaluacion, ID_Usuario_Evaluador.
3.  **Usuarios:** ID, Nombre, Rol, Hash.
4.  **Roles:** ID, Nombre, Permisos.
5.  **Configuracion_Rangos:** ID, Métrica, Umbrales (Rojo_Min, Naranja_Min, etc.).

## 6. Plan de Implementación (Fases)

1.  **Fase 1: Base de Datos y Modelos:** Crear tablas y clases Python para el nuevo modelo de datos.
2.  **Fase 2: Interfaz de Triaje (Entrada):** Crear el formulario de signos vitales con feedback visual inmediato (colores).
3.  **Fase 3: Lógica de Clasificación:** Implementar el algoritmo del "peor caso" y cálculo de prioridad.
4.  **Fase 4: Gestión de Cola y Reevaluación:** Panel de espera dinámico y flujo de re-triaje.
5.  **Fase 5: Roles y Configuración:** Login simulado, permisos y pantalla de configuración de rangos.
6.  **Fase 6: Integración IA:** Alertas predictivas y análisis con Gemini.
7.  **Fase 7: Informes:** Generación de la hoja de triaje.
