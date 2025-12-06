
# ROADMAP 2 - Fase 7: Refactorización y Mejoras (2025-11-27)

> [!IMPORTANT]
> **PROTOCOLO DE CIERRE DE TAREAS (DEFINITION OF DONE)**
> Ningún desarrollo se considera "Completado" hasta que se hayan ejecutado los siguientes pasos:
> 1.  📚 **Documentación Funcional:** Actualizar `docs/FUNCTIONAL.md` con las nuevas características.
> 2.  ⚙️ **Documentación Técnica:** Actualizar `docs/TECHNICAL.md` con cambios de arquitectura/API.
> 3.  📖 **Manuales:** Actualizar `MANUAL_USUARIO.md` y `MANUAL_MANTENIMIENTO.md` si impacta al usuario final.
> 4.  🗺️ **Mapa de Archivos:** Ejecutar `scripts/update_file_map.py` o actualizar `docs/FILE_MAP.md` manualmente.
> 5.  ✅ **Cierre Roadmap:** Marcar la casilla `[x]` correspondiente en este documento.

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

        - [x] **Pendiente:** Revisar funcionalidad de ocultación CSS (actualmente no oculta correctamente en todos los casos) y verificar por qué no aplica `color: white` por defecto.

- [x] **Mejoras Módulo Webcam:**
    - [x] Permitir tomar múltiples fotos en una misma sesión.
    - [x] Añadir selector para cambiar de dispositivo de webcam (si es técnicamente viable en Streamlit/Browser).

### 7.8 Modularización Panel Auditoría (Completado)
**Objetivo:** Convertir el Panel de Auditoría en un sistema modular, desacoplado y reutilizable.


- [x] **Modularización "Análisis Gráfico":**
    - [x] Convertir "Análisis Gráfico" en un orquestador simple.

- [x] **Corrección de Pestañas Duplicadas:**
    - Unificar "Auditoría" y "Auditoría v2".
    - Eliminar entrada duplicada en `permissions_service.py`.
    - Ajustar lógica de coincidencia de pestañas en `app.py` para evitar conflictos de nombres.
- [x] **Estabilización de `app.py`:**
    - Corregir `ModuleNotFoundError` en importaciones.
    - Corregir `NameError` (cookies) y orden de inicialización.
    - Restaurar estructura de archivo corrupta.

### 7.10 Limpieza y Mantenimiento
**Objetivo:** Eliminar código muerto y dependencias obsoletas.

- [ ] **Revisión de Componentes UI:**
    - [x] Revisar necesidad de `src/ui/loading_indicator.py` y eliminar si es posible (queremos quitarlo).

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
- [x] **Fase 5: Roles y Configuración:**
    - [x] Pantalla de configuración de rangos.
    - [x] Gestión de Roles (Crear/Editar/Eliminar).
    - [x] Asignación de Roles a Usuarios.
- [x] **Fase 6: Integración IA:**
    - [x] Alertas predictivas.
    - [x] Optimización de análisis de riesgos (Botones y Lógica).
    - [x] Actualización de modelos (Gemini 2.5 Flash).
- [x] **Fase 7: Informes:**
    - [x] Hoja de triaje.
    - [x] Entrevista Guiada Inteligente (Symptomate-style).

## 🚀 FASE 8: Preparación para Producción (Futuro)
**Objetivo:** Reemplazar simulaciones con implementaciones reales y robustecer el sistema.

- [x] **8.1 Machine Learning Real:**
    - [x] Reemplazar `ml_predictive_service.py` simulado con modelos reales (Scikit-learn).
    - [x] Entrenar modelos con datos históricos de MongoDB (Implementado en `ml_training_service.py`).
- [x] **8.2 Dashboard Multi-Centro Real:**
    - [x] UI Implementada (`multi_center_dashboard.py`).
    - [x] Conectar dashboard a datos agregados reales (Implementado en `multi_center_service.py`).
    - [x] Implementar selectores de centros dinámicos.
    - [x] Conectar dashboard a datos agregados reales (Implementado en `multi_center_service.py`).
    - [x] Implementar selectores de centros dinámicos.
- [x] **8.3 Video Nativo:**
    - [x] Implementar grabación de video real usando MediaRecorder API (o alternativa robusta `st.file_uploader`).
    - [x] **FIX**: Revisar estabilidad y funcionamiento (Reemplazado por File Uploader robusto).
- [x] **8.4 Testing y Calidad:**
    - [x] Estructura de tests (`tests/` folder).
    - [x] Implementar cobertura de tests unitarios y de integración (PTR y ML Service).
    - [x] CI/CD pipelines básicos.

- [x] **8.5 Mejora de Simulación Offline (Contingencia):**
    - [x] Mejorar `src/services/simulated_ia.py` para usar reglas más complejas (Árbol de Decisión).
    - [x] Implementar lógica de discriminadores y modificadores.
    - JSON actual de referencia:
      ```json
      {
        "exclusion_keywords": ["pecho", "respirar", "fiebre", "mareo", "vomito", "abdomen", "desmayo"],
        "rules": [
          {"keywords": ["abierta", "hueso", "sangre"], "level": 2, "reason": "Posible fractura abierta o lesión vascular."},
          {"keywords": ["deformidad", "movilidad"], "level": 3, "reason": "Signos de fractura o luxación con compromiso funcional."}
        ],
        "pain_threshold": 8,
        "pain_level_cap": 3,
        "age_threshold": 75,
        "age_level_cap": 3,
        "default_level": 4,
        "default_reason": "Patología traumatológica sin signos de riesgo vital inmediato."
      }
      ```

- [x] **8.6 Modularización y Configuración de PTR:**
    - [x] Migrar multiplicadores hardcoded de `ptr_logic.py` a colección `ptr_config` en MongoDB.
    - [x] Crear interfaz de administración (`ptr_config_panel.py`) para modificar pesos y reglas.
    - [x] Implementar versionado de configuraciones PTR (vía `updated_at`/`updated_by`).
    - **Nota:** La sincronización offline (localStorage) se abordará en la fase de PWA/Offline completa.

- [x] **8.7 Versionado y Auditoría de Respuestas IA:**
    - [x] **Schema:** Migrar de `sugerencia_ia` (string único) a `ai_responses` (array de objetos) en `triage_records`.
    - [x] **UI:** Permitir "regenerar" respuesta en el asistente sin perder la anterior (botón "Regenerar").
    - [x] **Analytics:** Analizar "Tasa de Rechazo" y respuestas descartadas en el Panel de Auditoría.

- [x] **8.8 Reporte Clínico Integral (PDF):**
    - **Objetivo:** Generar un documento legal/clínico completo del episodio de triaje.
    - **Contenido Requerido:**
        - **Administrativo:** Datos paciente, hora llegada, centro.
        - **Clínico:** Signos vitales, PTR (detalle), Valoración enfermería.
        - **Entrevista:** Resumen entrevista guiada, Historia enfermedad actual.
        - **Antecedentes:** Historial clínico integral recuperado.
        - **Multimodal:** Referencia a imágenes/audios adjuntos (thumbnails si es posible).
        - **IA:** Análisis completo, justificación y sugerencia.
        - **Cierre:** Validación humana, destino, firma digital (timestamp/usuario).
    - **Requisitos Técnicos:**
        - **Fuente de Datos:** Recuperar toda la información directamente de la Base de Datos (MongoDB), no de la sesión volátil.
        - **Visualización:** Renderizar dinámicamente solo los campos informados (evitar mostrar campos vacíos o "N/A" para limpiar el reporte).
    - **Nota de Implementación:** Si es necesario modificar el esquema de BD (ej: convertir campos planos a arrays o reestructurar objetos) para facilitar esta tarea o la 8.11, **hacerlo sin miedo**. Estamos en fase de piloto con datos de prueba.

- [x] **8.11 Recuperación de Triaje Interrumpido:**
    - [x] **Schema:** Añadir estado `draft` y `timestamp_update` en `triage_records`.
    - [x] **Lógica:** Implementar auto-guardado en cada paso del formulario (sin bloquear UI).
    - [x] **UX:** Al seleccionar un paciente con triaje incompleto, ofrecer "Retomar Triaje" y restaurar estado.
    - [x] **Reset:** Añadir opción "Reiniciar Triaje" para descartar el borrador y empezar de cero.

- [x] **8.9 Integración IoT Dispositivos Médicos (Simulación):** (Verificar si requiere actualización en FUNCTIONAL.md)
    - **Objetivo:** Simular la conectividad con dispositivos de electromedicina en el box de triaje.
    - **Configuración de Sala:** Añadir selectores en `Configuración > Salas` para asignar dispositivos (Monitor Multiparamétrico, Tensiómetro BT, Pulsioxímetro).
    - **Interfaz de Triaje:** Botón "Capturar Signos Vitales" que simule la lectura automática.

- [x] **8.12 Refactorización de UI/UX (Menú de Usuario):**
    - **Objetivo:** Centralizar utilidades y gestión de usuario en un menú global.
    - **Cambio:** Mover `tools_panel.py` de los módulos individuales a un botón/menú en la cabecera (top-right).
    - **Futuro:** Este menú alojará Login, Logout, Perfil y Recuperación de Claves.
    - **Dispositivos a Simular:**
        - Monitor de Signos Vitales (Connex/Welch Allyn style) -> FC, SpO2, TA, Temp.
        - Pulsioxímetro de dedo (Bluetooth LE).
        - Termómetro digital.
    - **Implementación:** Mockup de "Conectando...", delay aleatorio, y relleno automático de campos en `input_form.py`.


        - [x] **Casos Clínicos:** Base de datos de casos predefinidos (JSON/DB) con "Gold Standard" (respuesta correcta esperada).
        - [x] **Evaluación:** Comparar decisión del usuario vs Gold Standard y mostrar feedback inmediato.

## 🚀 FASE 9: Producción y PWA (Completado)
**Objetivo:** Preparación para despliegue productivo, autenticación real y capacidades offline.

- [x] **9.1 PWA y Offline-First:**
    - [x] Service Workers (Básico implementado).
    - [x] IndexedDB (Implementado para contingencia).
    - [x] Página Offline (`offline.html`).
    - [x] Sincronización en segundo plano (Integrado).
- [x] **9.2 Autenticación Real:**
    - [x] (Descartado para Demo) Integración con Auth0/Firebase, JWT, Seguridad.
- [x] **9.3 Despliegue:**
    - [x] Dockerización (`Dockerfile`, `docker-compose.yml`).
    - [x] HTTPS, CI/CD completo.



## 🚀 FASE 10: Futuro e Innovación (Parcialmente Completado)
**Objetivo:** Llevar el piloto a un nivel de producto comercial con interoperabilidad, IA avanzada y experiencia móvil nativa.

- [x] **10.1 Interoperabilidad Clínica:**
    - [x] **Estándar HL7/FHIR:** Implementar exportación de episodios de triaje en formato JSON FHIR (Resources: Patient, Encounter, Observation).
    - [x] **Codificación Automática:** Integrar servicio para mapear síntomas/diagnósticos a códigos CIE-10 o SNOMED CT usando la IA.

- [x] **10.2 Calidad y Testing Profundo:**
    - [x] **Tests E2E:** Configurar suite con Playwright para simular flujos completos de usuario (Admisión -> Triaje -> Alta).
    - [x] **Tests de Carga:** Script con Locust para simular concurrencia y validar estabilidad.

- [/] **10.3 Experiencia Móvil (PWA Avanzada):**
    - [ ] **Notificaciones Push:** Integrar Firebase Cloud Messaging (FCM) para alertas de "Paciente en espera crítica" (Implementado, pendiente debugging final).
    - [x] **Geolocalización:** Capturar coordenadas GPS en triajes extrahospitalarios (si aplica).
    - [ ] **Flujo de Datos:**
        - El texto transcrito se debe volcar en tiempo real a un área de texto visible.
        - Al finalizar, guardar el texto crudo como archivo `.txt` adjunto al episodio (`evidence_files`).
    - [ ] **Documentación Requerida:**
        - `FUNCTIONAL.md`: Explicar cómo activar el modo escucha y su privacidad.
        - `TECHNICAL.md`: Detallar la API de voz utilizada y limitaciones de navegador.

- [ ] **11.2 Interfaz Contextual (Liquid UI):**
    - [ ] **Implementación Técnica:**
        - Refactorizar `input_form.py` para usar `st.empty()` y contenedores dinámicos.
        - Crear lógica de reglas en `src/services/ui_rules_engine.py` (ej: `if motivo == 'Trauma' -> show_body_map`).
    - [ ] **Input Híbrido:**
        - Crear componente `SpeechInput` que combine `st.text_input` con un botón de micro.
    - [ ] **Documentación Requerida:**
        - `FUNCTIONAL.md`: Listar las reglas de adaptación de la interfaz.
        - `TECHNICAL.md`: Explicar el motor de reglas de UI.

- [ ] **11.3 Copiloto RAG Proactivo:**
    - [ ] **Implementación Técnica:**
        - Implementar `st.toast` o `st.sidebar.info` para alertas no intrusivas.
        - Crear `ProactiveService` que analice el `session_state` en cada re-run.
        - Conectar con `RAGService` para búsquedas silenciosas en segundo plano.
    - [ ] **Documentación Requerida:**
        - `FUNCTIONAL.md`: Describir qué tipo de alertas puede esperar el usuario.
        - `TECHNICAL.md`: Explicar el impacto en rendimiento de las búsquedas en background.

- [ ] **11.4 Triaje Conversacional Dual:**
    - [ ] **Implementación Técnica:**
        - Crear nueva vista `ChatTriageView`.
        - Implementar parser de lenguaje natural (usando Gemini) para extraer JSON del chat.
        - Sincronizar el JSON extraído con `st.session_state.datos_paciente`.
    - [ ] **Soporte Multidioma (Babel Mode):**
        - Prompt Instruction: "Detecta el idioma del usuario y responde en ese mismo idioma."
        - Output Constraint: "El JSON extraído (`sintomas`, `resumen`) debe estar SIEMPRE en ESPAÑOL."
    - [ ] **Documentación Requerida:**
        - `MANUAL_USUARIO.md`: Guía de "Cómo realizar un triaje por chat".

## 🔌 FASE 12: API REST & Microservicios (Interoperabilidad)
**Objetivo:** Desacoplar la lógica de negocio de la UI (Streamlit) para permitir que terceros (HIS, Apps Móviles, CRMs) consuman nuestros servicios.
**Nota Importante:** Documentar cada endpoint en `docs/TECHNICAL.md` y actualizar `docs/FILE_MAP.md` con la nueva estructura `src/api/`.

- [ ] **12.1 Infraestructura API (FastAPI):**
    - [ ] **Setup:**
        - Instalar `fastapi`, `uvicorn`.
        - Crear estructura `src/api/` (`main.py`, `routers/`, `schemas/`).
        - Configurar ejecución paralela (Streamlit + FastAPI) en `docker-compose.yml`.
    - [ ] **Seguridad:**
        - Implementar `APIKeyHeader` para autenticación básica de clientes.

- [ ] **12.2 Endpoints Core (Triage as a Service):**
    - [ ] `POST /triage/analyze`:
        - Input: `PatientDataSchema` (Síntomas, Constantes).
        - Logic: Invocar `TriageService.analyze()`.
        - Output: `TriageResultSchema` (Nivel, Color, Razonamiento).
    - [ ] `POST /predict/risk`:
        - Input: `VitalSignsSchema`.
        - Logic: Invocar `PredictiveService.calculate_ptr()`.
        - Output: `RiskScoreSchema`.

- [ ] **12.3 Endpoints IA (Intelligence as a Service):**
    - [ ] `POST /rag/query`:
        - Input: `QuerySchema` (Texto).
        - Logic: Invocar `RAGService.search()`.
        - Output: `ContextSchema` (Fragmentos, Fuentes).

- [ ] **12.4 Integración HIS (Webhooks):**
    - [ ] **Implementación:**
        - Crear sistema de suscripción a eventos (simple observer pattern).
        - Enviar POST request a URL configurada cuando `TriageRecord` se guarda.
    - [ ] **Documentación:**
        - `TECHNICAL.md`: Especificar el formato del payload JSON de los webhooks.
