# ROADMAP 2 - Fase 7: Refactorización y Mejoras (2025-11-27)

Este documento detalla el plan de ejecución para la Fase 7 de mejoras y refactorización del sistema "Asistente de Triaje IA".

## 🎯 FASE 7: Refactorización y Mejoras UX/UI

### 7.1 Configuración y Orquestación
**Objetivo:** Reorganizar la gestión de salas y añadir configuración de hardware.

- [x] **Orquestador de Salas:**
    - Crear nueva pestaña "Salas" en `Configuración > Centro`.
    - Mover "Gestión de salas" (existente) a esta pestaña.
    - Mover "Asignación de salas (fija)" (existente) a esta pestaña.
    - Mover "Control de salas" (del menú principal) a esta pestaña.
- [x] **Configuración de Equipo:**
    - Crear nueva sección "Configuración equipo" en `Configuración`.
    - Selectores para dispositivo de entrada de audio (micrófono).
    - Selectores para dispositivo de entrada de video (cámara).
    - Selector de calidad de video (Baja/Media/Alta).
- [x] **Reorganización de Configuración:**
    - Mover "Notificaciones" a sub-pestaña en `Configuración > General`.
    - Mover "Prompts" a sub-pestaña en `Configuración > General`.

### 7.2 Gestión de Usuarios y Personas
**Objetivo:** Mejorar la gestión de identidades y permisos.

- [x] **Modal de Usuarios:**
    - Ajustar ancho al 75% del contenedor (`width="large"`).
    - Verificar responsividad.
    - Campo "Nombre completo" en modo solo lectura (derivado de `people`).
    - Eliminar duplicidad de datos de identificación (usar relación con `people`).
    - **Nueva Funcionalidad:** Crear funciones dinámicas desde el formulario.
- [x] **Modal de Salas:**
    - Ajustar ancho al 75% del contenedor (`width="large"`).
    - Campo "Subtipo" convertido a selector: ["atención", "espera"].
- [x] **Gestión de Personas (People):**
    - Crear módulo independiente para crear/editar personas (modal reutilizable).
    - Usar este módulo desde Admisión y Gestión de Usuarios.
- [x] **Árbol de Permisos:**
    - Implementar selector jerárquico de permisos (árbol de directorios).
    - Lógica de selección/deselección en cascada (padre <-> hijos).
    - Aplicar permisos a cada punto del menú de la aplicación.
    - Actualizar estructura visual en "Gestión de Roles" para reflejar cambios de menú.

### 7.3 Mejoras Flujo de Admisión
**Objetivo:** Optimizar la búsqueda y validación de pacientes.

- [ ] **Búsqueda de Pacientes:**
    - Corregir warning "No se encontró paciente" cuando sí existe (revisar consulta a `people`).
    - Añadir tipos de ID: "Número de la SS" (migrar dato actual), "Otro".
- [ ] **UX Paso 1 (Selección de Sala):**
    - Mover mensaje "📍 Sala seleccionada" y botón "Continuar" justo debajo del título.
    - Evitar scroll innecesario para navegar.
- [ ] **UX Paso 2 (Datos):**
    - **Refactorización de Identificación:** Eliminar campo específico "Número Seguridad Social". Tratarlo como un tipo más en `identificaciones`.
    - **Búsqueda Parcial:** Permitir búsqueda por DNI u otro tipo con datos incompletos (min 3 chars) o sin letras.
    - **Resultados de Búsqueda:**
        - Mostrar lista de candidatos (incluso si es solo 1).
        - Reemplazar componente actual "Información del Paciente" por esta lista/tarjeta de selección.
        - Campos no editables en la vista de lista.
    - **Edición y Creación:**
        - Botón "Editar" en cada resultado -> Abre modal de Persona (75% ancho).
        - Botón "Crear nuevo paciente" -> Abre misma modal de Persona.
        - Unificar lógica de creación/edición usando el componente `people_manager`.
    - **Bugfix Búsqueda:** Investigar por qué no encuentra pacientes existentes por DNI (revisar lógica de query vs estructura de datos `identificaciones`).

### 7.4 Mejoras Flujo Asistente Triaje
**Objetivo:** Enriquecer la entrada de datos y mejorar la gestión de pacientes.

- [x] **Paso 2 (Selección):**
    - Detectar paciente ya en sala (mostrar primero, fondo azul claro).
    - Bloquear atención de otros si hay paciente en sala.
    - Habilitar acciones "Rechazar" y "Reasignar" en la card del paciente.
- [x] **Paso 3 (Triaje - Input):**
    - **Nueva Sección Multimedia:** Insertar entre "Motivo" y "Confirmar".
        - Carga de archivos (Imagen, Audio, Video).
        - Grabación de Audio (componente actual).
        - Grabación de Video (placeholder/webcam).
        - Documentos historial (placeholder).
    - **Reordenamiento:** Mover selectores Edad y Dolor después de archivos.
    - **Lógica de UI:**
        - Transcripción obligatoria para Audio/Video antes de análisis.
        - Botón "Confirmar motivo" bloquea la sección y habilita análisis.
        - Botón "Confirmar motivo" bloquea la sección y habilita análisis.
        - Colapsar sección de input tras análisis, expandir resultados.
    - [x] **Modularización de Media Cards:**
        - Refactorización de `input_form.py` para extraer lógica de tarjetas.
        - Creación de `media_cards.py` con manejo robusto de archivos (TempFileWrapper).
        - Unificación de estilos y manejo de errores en reproducción/visualización.

### 7.5 Refactorización Final y UI (Triage & Personas)
**Objetivo:** Unificar estilos, corregir lógica de flujo y mejorar la experiencia de usuario.

- [x] **Gestión de Personas:**
    - Soporte para múltiples identificaciones (lista dinámica).
    - Soporte para múltiples formas de contacto (lista dinámica).
- [x] **UI Triaje Paso 1 (Sala):**
    - Unificar estilo con Admisión (info sala seleccionada arriba, botón cambiar).
- [x] **UI Triaje Paso 2/3 (Proceso):**
    - **Inputs Unificados:** Selector de tipo de entrada (Texto, Audio, Video, Archivo, Importar).
    - **Tarjeta Paciente:** Unificar diseño con Boxes/Consultas.
    - **Colapso Inteligente:** Plegar análisis tras completarse, destacar Nivel Sugerido en validación.
- [x] **Lógica de Flujo:**
    - **No Traumatología:** Permitir rechazo o derivación directa desde validación si el análisis es negativo.
    - **Bugfix Admisión:** Corregir disponibilidad de consultas en derivación.
- [x] **UI Triaje Paso 4 (Derivación):**
    - Unificar estilo de confirmación con Admisión (destino seleccionado arriba).

## 📝 Notas Técnicas
- **People vs Users:** La tabla `users` debe tener `person_id` y NO duplicar `identification_number` ni `nombre`. El nombre se muestra haciendo join/lookup.
- **Identificaciones:** Migrar campo plano `num_ss` a array `identificaciones` en `people` si no está hecho.
- **Componentes Reutilizables:** Asegurar que el modal de personas y el input multimedia sean componentes importables.

- **Video Recording:** La grabación de video directa desde el navegador requiere implementación custom (MediaRecorder API) ya que Streamlit nativo solo soporta foto. Tarea futura.

---
**Estado Actual:** En Progreso (Fase 7.1, 7.2, 7.4 y 7.5 completadas).

### 7.6 Nuevas Tareas (Pendientes de Ejecución)
**Objetivo:** Mejoras de usabilidad, estandarización y herramientas de feedback.

- [ ] **Refactor UI Input Form (`src/components/triage/input_form.py`):**
    - Mover botones "Confirmar motivo" y "Editar datos" justo antes del mensaje de "Aviso de Privacidad".
    - Implementar lógica de bloqueo: al pulsar "Confirmar motivo", deshabilitar/proteger todos los componentes superiores (texto, edad, dolor, archivos).
    - Al pulsar "Editar datos", volver a habilitar los componentes.

- [x] **Menú por Pasos en Atención:**
    - Implementar menú de navegación por pasos (similar a Admisión y Triaje) para los flujos de "Atención Box" y "Consulta".
# ROADMAP 2 - Fase 7: Refactorización y Mejoras (2025-11-27)

Este documento detalla el plan de ejecución para la Fase 7 de mejoras y refactorización del sistema "Asistente de Triaje IA".

## 🎯 FASE 7: Refactorización y Mejoras UX/UI

### 7.1 Configuración y Orquestación
**Objetivo:** Reorganizar la gestión de salas y añadir configuración de hardware.

- [x] **Orquestador de Salas:**
    - Crear nueva pestaña "Salas" en `Configuración > Centro`.
    - Mover "Gestión de salas" (existente) a esta pestaña.
    - Mover "Asignación de salas (fija)" (existente) a esta pestaña.
    - Mover "Control de salas" (del menú principal) a esta pestaña.
- [x] **Configuración de Equipo:**
    - Crear nueva sección "Configuración equipo" en `Configuración`.
    - Selectores para dispositivo de entrada de audio (micrófono).
    - Selectores para dispositivo de entrada de video (cámara).
    - Selector de calidad de video (Baja/Media/Alta).
- [x] **Reorganización de Configuración:**
    - Mover "Notificaciones" a sub-pestaña en `Configuración > General`.
    - Mover "Prompts" a sub-pestaña en `Configuración > General`.

### 7.2 Gestión de Usuarios y Personas
**Objetivo:** Mejorar la gestión de identidades y permisos.

- [x] **Modal de Usuarios:**
    - Ajustar ancho al 75% del contenedor (`width="large"`).
    - Verificar responsividad.
    - Campo "Nombre completo" en modo solo lectura (derivado de `people`).
    - Eliminar duplicidad de datos de identificación (usar relación con `people`).
    - **Nueva Funcionalidad:** Crear funciones dinámicas desde el formulario.
- [x] **Modal de Salas:**
    - Ajustar ancho al 75% del contenedor (`width="large"`).
    - Campo "Subtipo" convertido a selector: ["atención", "espera"].
- [x] **Gestión de Personas (People):**
    - Crear módulo independiente para crear/editar personas (modal reutilizable).
    - Usar este módulo desde Admisión y Gestión de Usuarios.
- [x] **Árbol de Permisos:**
    - Implementar selector jerárquico de permisos (árbol de directorios).
    - Lógica de selección/deselección en cascada (padre <-> hijos).
    - Aplicar permisos a cada punto del menú de la aplicación.
    - Actualizar estructura visual en "Gestión de Roles" para reflejar cambios de menú.

### 7.3 Mejoras Flujo de Admisión
**Objetivo:** Optimizar la búsqueda y validación de pacientes.

- [x] **Búsqueda de Pacientes:**
    - [x] Corregir warning "No se encontró paciente" cuando sí existe (revisar consulta a `people`).
    - [x] Añadir tipos de ID: "Número de la SS" (migrar dato actual), "Otro".
- [x] **UX Paso 1 (Selección de Sala):**
    - [x] Mover mensaje "📍 Sala seleccionada" y botón "Continuar" justo debajo del título.
    - [x] Evitar scroll innecesario para navegar.
- [x] **UX Paso 2 (Datos):**
    - [x] **Refactorización de Identificación:** Eliminar campo específico "Número Seguridad Social". Tratarlo como un tipo más en `identificaciones`.
    - [x] **Búsqueda Parcial:** Permitir búsqueda por DNI u otro tipo con datos incompletos (min 3 chars) o sin letras.
    - [x] **Resultados de Búsqueda:**
        - [x] Mostrar lista de candidatos (incluso si es solo 1).
        - [x] Reemplazar componente actual "Información del Paciente" por esta lista/tarjeta de selección.
        - [x] Campos no editables en la vista de lista.
    - [x] **Edición y Creación:**
        - [x] Botón "Editar" en cada resultado -> Abre modal de Persona (75% ancho).
        - [x] Botón "Crear nuevo paciente" -> Abre misma modal de Persona.
        - [x] Unificar lógica de creación/edición usando el componente `people_manager`.
    - [x] **Bugfix Búsqueda:** Investigar por qué no encuentra pacientes existentes por DNI (revisar lógica de query vs estructura de datos `identificaciones`).

### 7.4 Mejoras Flujo Asistente Triaje
**Objetivo:** Enriquecer la entrada de datos y mejorar la gestión de pacientes.

- [x] **Paso 2 (Selección):**
    - Detectar paciente ya en sala (mostrar primero, fondo azul claro).
    - Bloquear atención de otros si hay paciente en sala.
    - Habilitar acciones "Rechazar" y "Reasignar" en la card del paciente.
- [x] **Paso 3 (Triaje - Input):**
    - **Nueva Sección Multimedia:** Insertar entre "Motivo" y "Confirmar".
        - Carga de archivos (Imagen, Audio, Video).
        - Grabación de Audio (componente actual).
        - Grabación de Video (placeholder/webcam).
        - Documentos historial (placeholder).
    - **Reordenamiento:** Mover selectores Edad y Dolor después de archivos.
    - **Lógica de UI:**
        - Transcripción obligatoria para Audio/Video antes de análisis.
        - Botón "Confirmar motivo" bloquea la sección y habilita análisis.
        - Botón "Confirmar motivo" bloquea la sección y habilita análisis.
        - Colapsar sección de input tras análisis, expandir resultados.
    - [x] **Modularización de Media Cards:**
        - Refactorización de `input_form.py` para extraer lógica de tarjetas.
        - Creación de `media_cards.py` con manejo robusto de archivos (TempFileWrapper).
        - Unificación de estilos y manejo de errores en reproducción/visualización.

### 7.5 Refactorización Final y UI (Triage & Personas)
**Objetivo:** Unificar estilos, corregir lógica de flujo y mejorar la experiencia de usuario.

- [x] **Gestión de Personas:**
    - Soporte para múltiples identificaciones (lista dinámica).
    - Soporte para múltiples formas de contacto (lista dinámica).
- [x] **UI Triaje Paso 1 (Sala):**
    - Unificar estilo con Admisión (info sala seleccionada arriba, botón cambiar).
- [x] **UI Triaje Paso 2/3 (Proceso):**
    - **Inputs Unificados:** Selector de tipo de entrada (Texto, Audio, Video, Archivo, Importar).
    - **Tarjeta Paciente:** Unificar diseño con Boxes/Consultas.
    - **Colapso Inteligente:** Plegar análisis tras completarse, destacar Nivel Sugerido en validación.
- [x] **Lógica de Flujo:**
    - **No Traumatología:** Permitir rechazo o derivación directa desde validación si el análisis es negativo.
    - **Bugfix Admisión:** Corregir disponibilidad de consultas en derivación.
- [x] **UI Triaje Paso 4 (Derivación):**
    - Unificar estilo de confirmación con Admisión (destino seleccionado arriba).

## 📝 Notas Técnicas
- **People vs Users:** La tabla `users` debe tener `person_id` y NO duplicar `identification_number` ni `nombre`. El nombre se muestra haciendo join/lookup.
- **Identificaciones:** Migrar campo plano `num_ss` a array `identificaciones` en `people` si no está hecho.
- **Componentes Reutilizables:** Asegurar que el modal de personas y el input multimedia sean componentes importables.

- **Video Recording:** La grabación de video directa desde el navegador requiere implementación custom (MediaRecorder API) ya que Streamlit nativo solo soporta foto. Tarea futura.

---
**Estado Actual:** En Progreso (Fase 7 completada, Fase 8 en planificación). Implementadas mejoras de IA y UX (Entrevista Guiada).

### 7.6 Nuevas Tareas (Pendientes de Ejecución)
**Objetivo:** Mejoras de usabilidad, estandarización y herramientas de feedback.

- [x] **Refactor UI Input Form (`src/components/triage/input_form.py`):**
    - [x] Mover botones "Confirmar motivo" y "Editar datos" justo antes del mensaje de "Aviso de Privacidad".
    - [x] Implementar lógica de bloqueo: al pulsar "Confirmar motivo", deshabilitar/proteger todos los componentes superiores (texto, edad, dolor, archivos).
    - [x] Al pulsar "Editar datos", volver a habilitar los componentes.

- [x] **Menú por Pasos en Atención:**
    - [x] Implementar menú de navegación por pasos (similar a Admisión y Triaje) para los flujos de "Atención Box" y "Consulta".

- [x] **Módulo de Reporte de Feedback/Errores:**
    - **Backend:**
        - [x] Crear nueva colección/tabla en BD para reportes.
        - [x] Campos: `module_name`, `timestamp`, `user_id`, `report_type` (error, mejora, comentario), `subtype`, `title`, `body`.
    - **Frontend:**
        - [x] Crear componente reutilizable (botón icono sin texto) que abra una modal    - **Integración:**
        - [x] Añadir botón de prueba en Admisiones -> Paso 1 "Sala de admisión".
        - [x] Visualización en Panel de Auditoría (Debug Mongo) y Datos en Bruto (con card de detalles).
    - [x] **Mejora:** Permitir adjuntar archivos en el reporte (usando `src/components/common/file_importer.py`).

- [ ] **Documentación y Estandarización de Código:**
    - [x] **Etiquetas de Depuración:** Recorrer todos los archivos `.py` con interfaz gráfica y añadir al final un footer discreto con la ruta del archivo (ej: `src/ui/main_view.py`).
    - [x] **Mapa de Archivos (`FILE_MAP.md`):**
        - [x] Crear estructura inicial con archivos principales.
        - [x] **Pendiente:** Completar el mapa con **TODOS** los archivos del proyecto (no solo los principales), incluyendo utilidades, configuraciones y scripts.
        - Analizar dependencias de invocación antes de editar.
        - Marcar como "POSIBLE DEPRECADO" si un archivo no tiene invocaciones detectadas.

- [x] **Mejoras Módulo Webcam:**
    - [x] Permitir tomar múltiples fotos en una misma sesión.
    - [x] Añadir selector para cambiar de dispositivo de webcam (si es técnicamente viable en Streamlit/Browser).

### 7.8 Modularización Panel Auditoría (Completado)
**Objetivo:** Convertir el Panel de Auditoría en un sistema modular, desacoplado y reutilizable.

- [x] **Componentes Base Reutilizables:**
    - [x] **Selector de Fechas:** Crear módulo independiente para selección de rango de fechas (Desde/Hasta).
    - [x] **Barra de Acciones:** Crear módulo independiente para botones de acción (Refrescar, CSV, Excel, Compartir, PDF).

- [x] **Modularización "Datos en Bruto":**
    - [x] Convertir "Datos en Bruto" en un orquestador simple.
    - [x] **Sub-módulos Independientes:**
        - [x] Registros de Auditoría.
        - [x] Log de Ficheros Importados.
        - [x] Log de Transcripciones.
        - [x] Log de Prompts.
        - [x] Feedback & Errores.
    - [x] **Integración:** Cada sub-módulo debe implementar su propio Selector de Fechas y Barra de Acciones.
    - [x] **Filtros:** Cada sub-módulo mantiene sus filtros específicos.

- [x] **Modularización "Análisis Gráfico":**
    - [x] Convertir "Análisis Gráfico" en un orquestador simple.
    - [x] **Sub-módulos Independientes:**
        - [x] Resumen General.
        - [x] Evolución Temporal.
        - [x] Análisis de Triaje.
        - [x] Análisis de Archivos.
        - [x] Análisis de Transcripciones.
        - [x] Análisis Relacional.
        - [x] Análisis de Prompts.
        - [x] Análisis de Feedback.
    - [x] **Integración:** Cada sub-módulo debe implementar su propio Selector de Fechas y Barra de Acciones.
    - [ ] Añadir etiquetas de footer a todos los nuevos módulos.
    - [ ] Registrar nuevos módulos en `FILE_MAP.md`.
    - [x] **Estrategia de Migración:** Crear menú "Auditoría v2" para desarrollo paralelo sin romper la versión actual. (Fusionado: "Auditoría" ahora usa la implementación v2).

### 7.9 Correcciones y Estabilización
**Objetivo:** Resolver errores críticos de arranque y duplicidad de interfaz.

- [x] **Corrección de Pestañas Duplicadas:**
    - Unificar "Auditoría" y "Auditoría v2".
    - Eliminar entrada duplicada en `permissions_service.py`.
    - Ajustar lógica de coincidencia de pestañas en `app.py` para evitar conflictos de nombres.
- [x] **Estabilización de `app.py`:**
    - Corregir `ModuleNotFoundError` en importaciones.
    - Corregir `NameError` (cookies) y orden de inicialización.
    - Restaurar estructura de archivo corrupta.

## 🚀 TRYaGE 2.0: Advanced Triage System Implementation
**Objetivo:** Implementación del nuevo sistema de triaje clínico avanzado (Signos vitales, Reevaluación, IA).

- [x] **Fase 1: Base de Datos y Modelos:**
    - [x] Crear modelos Pydantic (`VitalSigns`, `TriageRangeConfig`).
    - [x] Actualizar `TriageRecord`.
    - [x] Actualizar repositorios y crear `TriageConfigRepository`.
- [x] **Fase 2: Interfaz de Triaje (Entrada):**
    - [x] Formulario de signos vitales.
    - [x] Feedback visual (colores).
- [x] **Fase 3: Lógica de Clasificación:**
    - [x] Algoritmo "Peor Caso".
    - [x] Cálculo de prioridad.
- [x] **Fase 4: Gestión de Cola y Reevaluación:**
    - [x] Panel de espera dinámico.
    - [x] Flujo de re-triaje.
- [ ] **Fase 5: Roles y Configuración:**
    - [ ] Pantalla de configuración de rangos.
- [x] **Fase 6: Integración IA:**
    - [x] Alertas predictivas.
    - [x] Optimización de análisis de riesgos (Botones y Lógica).
    - [x] Actualización de modelos (Gemini 2.5 Flash).
- [x] **Fase 7: Informes:**
    - [x] Hoja de triaje.
    - [x] Entrevista Guiada Inteligente (Symptomate-style).

## 🚀 FASE 8: Preparación para Producción (Futuro)
**Objetivo:** Reemplazar simulaciones con implementaciones reales y robustecer el sistema.

- [ ] **8.1 Machine Learning Real:**
    - Reemplazar `ml_predictive_service.py` simulado con modelos reales (Scikit-learn).
    - Entrenar modelos con datos históricos de MongoDB.
- [ ] **8.2 Dashboard Multi-Centro Real:**
    - Conectar dashboard a datos agregados reales.
    - Implementar selectores de centros dinámicos.
- [ ] **8.3 Video Nativo:**
    - Implementar grabación de video real usando MediaRecorder API (Custom Component).
- [ ] **8.4 Testing y Calidad:**
    - Implementar tests unitarios y de integración.
    - CI/CD pipelines básicos.


