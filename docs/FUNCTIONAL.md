# Documentación Funcional - Asistente de Triaje IA

## 1. Introducción

El **Asistente de Triaje IA** es una aplicación web diseñada para optimizar el proceso de clasificación de pacientes en servicios de urgencias de Traumatología. Utiliza inteligencia artificial generativa (Google Gemini) para analizar datos clínicos, transcripciones de voz e imágenes, sugiriendo niveles de prioridad y especialidades médicas.

El sistema está construido sobre **Streamlit** y utiliza **MongoDB** como base de datos, garantizando una interfaz ágil y persistencia de datos robusta.

---

## 2. Roles de Usuario y Permisos

El acceso a las funcionalidades del sistema está segmentado por roles, definidos en la configuración del centro.

| Rol | Descripción | Acceso a Módulos |
| :--- | :--- | :--- |
| **Admin** | Administrador del sistema | Acceso total, configuración del centro, gestión de usuarios y roles. |
| **Admisión** | Personal administrativo | Registro de pacientes, búsqueda, gestión de la cola de admisión. |
| **Enfermería** | Enfermeros/as de triaje | Realización de triajes, validación de IA, derivación a salas. |
| **Médico** | Doctores/as | Atención en box, visualización de historial, alta de pacientes. |
| **Gestor** | Supervisor de flujo | Control de salas (Orquestador), reasignación de pacientes. |
| **Auditor** | Auditor de calidad | Acceso al panel de auditoría y análisis de datos. |

> [!NOTE]
> Los roles son configurables en la colección `users`. Actualmente no se han detectado roles personalizados en la base de datos.

### 2.1 Menú de Usuario Global
Se ha implementado un punto de acceso unificado en la cabecera de la aplicación (esquina superior derecha) para gestionar la sesión y utilidades:
*   **Acceso:** Botón con icono de usuario y nombre del usuario actual.
*   **Funcionalidades:**
    *   **Feedback:** Reporte rápido de errores o sugerencias.
    *   **Modo Contingencia:** Activación manual del modo offline.
    *   **Modo Formación:** Activación del modo de entrenamiento.
    *   **Cerrar Sesión:** (Placeholder) Salida segura del sistema.

---

## 3. Ciclo de Vida del Flujo de Paciente

El sistema implementa un modelo de flujo de pacientes basado en estados ("Log-based"), donde cada movimiento entre salas o cambio de estado queda registrado para una trazabilidad completa.

### Estados del Flujo (Valores en BD)
1.  **EN_ADMISION**: El paciente está siendo registrado o sus datos actualizados en recepción.
2.  **EN_ESPERA_TRIAJE**: El paciente ha sido admitido y espera ser llamado por enfermería.
3.  **EN_TRIAJE**: El paciente está siendo evaluado en un box de triaje (subtipo sala: `atencion`).
4.  **DERIVADO**: El triaje ha finalizado y el paciente espera atención médica (equivale a "Espera de Consulta/Box").
5.  **FINALIZADO**: El paciente ha sido dado de alta o derivado a otro centro.
6.  **RECHAZADO**: El paciente no ha sido admitido (ej. error administrativo o derivación inmediata).

> [!INFO]
> Estos estados corresponden al campo `estado` en la colección `patient_flow`.

---

## 4. Inteligencia Artificial y Machine Learning (Marco Teórico)

El sistema integra capacidades avanzadas de IA tanto generativa como predictiva.

### 4.1 Modelos Predictivos (Real ML)
El sistema utiliza algoritmos de **Random Forest** (Bosques Aleatorios) implementados con Scikit-learn para realizar predicciones operativas. La arquitectura se divide en dos servicios principales:

1.  **Servicio de Entrenamiento (`MLTrainingService`):**
    *   Ejecuta procesos offline para entrenar modelos utilizando datos históricos almacenados en MongoDB (`triage_records`).
    *   Genera y serializa modelos (`.joblib`) para:
        *   **Predicción de Demanda:** Basado en hora del día y día de la semana.
        *   **Tiempo de Espera:** Basado en carga actual y nivel de triaje.

2.  **Servicio Predictivo (`MLPredictiveService`):**
    *   Carga los modelos serializados en memoria para realizar inferencias en tiempo real.
    *   Provee estimaciones de tiempo de espera para pacientes y recomendaciones de staffing para gestores.

Además, el sistema integra capacidades de IA Generativa para:
*   **Procesamiento de Lenguaje Natural (NLP):** Analiza la entrevista clínica transcrita y el texto libre.
*   **Reconocimiento Automático del Habla (ASR):** Transcribe en tiempo real la interacción verbal.
*   **Visión Computacional:** Analiza imágenes de lesiones para evaluar gravedad visual.

### 4.2 Lógica de Puntuación de Riesgo (PTR) - Dinámica
El sistema implementa un modelo de **Puntuación Total de Riesgo (PTR)** totalmente configurable y almacenado en base de datos. Esto permite a los administradores clínicos ajustar los pesos, umbrales y multiplicadores sin necesidad de intervención técnica.

La configuración se gestiona desde el panel de administración (`Configuración > Triaje (PTR)`), permitiendo definir:
*   **Multiplicador Base:** Peso general de la métrica.
*   **Reglas:** Umbrales específicos (ej: `< 90`) y los puntos base que otorgan (0-3).
*   **Modificadores de Contexto:** Multiplicadores alternativos para poblaciones especiales (Geriátrico, Inmunodeprimido).

#### 4.2.1 Lógica de Puntuación (Legacy/Ejemplo de Configuración por Defecto)
A continuación se detalla la configuración inicial por defecto del sistema (equivalente a la lógica hardcoded anterior):

#### Tabla de Multiplicadores y Pesos (Default)
| Parámetro | Multiplicador Base | Ajuste Contextual |
| :--- | :---: | :--- |
| **GCS (Conciencia)** | **x4** | - |
| **SpO2 (Saturación)** | **x3** | - |
| **Tensión Arterial** | **x3** | - |
| **Frecuencia Respiratoria** | **x2** | - |
| **Frecuencia Cardíaca** | **x1** | **x2** si paciente Geriátrico (>75 años) |
| **Temperatura** | **x1** | **x3** si Inmunodeprimido/Oncológico |
| **Dolor (EVA)** | **x1** | - |

#### Interpretación del Score
La suma total de puntos determina el nivel de riesgo sugerido y el código de color:
*   **> 15 puntos:** Nivel I/II (Rojo/Naranja) - Riesgo Vital Inmediato.
*   **8 - 15 puntos:** Nivel II/III (Naranja/Amarillo) - Urgencia.
*   **3 - 7 puntos:** Nivel III/IV (Amarillo/Verde) - Urgencia Menor.
*   **< 3 puntos:** Nivel IV/V (Verde/Azul) - No Urgente.

### 4.3 Alertas Predictivas
Mediante el análisis de patrones en los datos históricos y clínicos, el sistema genera alertas proactivas:
*   **Detección de Sepsis:** Combinación de fiebre, taquicardia y alteración del estado mental.
*   **Riesgo de Caídas:** Basado en edad, medicación y antecedentes.
*   **Violencia/Abuso:** Detección de inconsistencias entre el relato y las lesiones visibles.

### 4.4 Versionado de Respuestas IA
El sistema mantiene un historial completo de todas las interacciones con la IA para un mismo episodio de triaje. Esto permite:
*   **Regeneración:** Si el usuario no está satisfecho con la primera sugerencia, puede solicitar una nueva ("Regenerar Respuesta").
*   **Trazabilidad:** La respuesta anterior no se borra, sino que se marca como `discarded` (descartada) y se archiva en el historial del registro (`ai_responses`).
*   **Auditoría:** Se puede analizar posteriormente cuántas veces se regeneró una respuesta y si la segunda opción fue finalmente aceptada o rechazada.

---

## 5. Detalle de Módulos

### 5.1 Módulo de Admisión
**Objetivo:** Identificación unívoca y registro de llegada del paciente.

*   **Búsqueda de Pacientes:** Permite localizar pacientes por DNI, Nombre o Apellidos en la base de datos `people`.
*   **Registro de Nuevos Pacientes:** Formulario para crear fichas de pacientes inexistentes.
*   **Gestión de Flujo Activo:** Si un paciente ya tiene un proceso abierto, el sistema alerta y ofrece opciones:
    *   *Continuar:* Ir al paso actual del paciente.
    *   *Reasignar:* Mover al paciente a otra sala (ej. de vuelta a espera).
    *   *Rechazar/Cancelar:* Cerrar el flujo actual.

#### 5.1.1 Recuperación de Sesiones (Borradores)
El sistema implementa un mecanismo de **auto-guardado y recuperación** para evitar la pérdida de datos ante interrupciones (ej. cierre accidental del navegador, recarga de página).

*   **Auto-Guardado:** Durante el proceso de triaje, cada cambio en los campos clave (motivo, dolor, signos vitales, antecedentes) se guarda automáticamente en un registro con estado `draft`.
*   **Recuperación:** Al volver a seleccionar al mismo paciente desde la cola de espera, el sistema detecta si existe un borrador activo y restaura automáticamente el estado anterior, notificando al usuario.
*   **Reinicio:** Si el usuario desea descartar el trabajo previo, puede utilizar la opción **"Reiniciar"** (icono papelera) en la tarjeta del paciente, lo que eliminará el borrador y comenzará un triaje limpio.
*   **Finalización:** Al validar el triaje, el borrador pasa a estado `completed` y deja de ser recuperable como borrador.

### 5.2 Módulo de Triaje Inteligente (Core)
**Objetivo:** Evaluación clínica asistida por IA para determinar urgencia y especialidad.

#### A. Selección de Paciente
*   Visualización de la **Cola de Espera** ordenada por tiempo de llegada.
*   Indicadores de tiempo de espera (colores semafóricos).

#### B. Entrevista y Toma de Datos (Módulos de Recolección)
El sistema dispone de una arquitectura modular para la captura exhaustiva de datos clínicos. Cada módulo se centra en un aspecto específico de la anamnesis:

**1. Datos Administrativos y Logística (`admin_data_form`)**
*   **Fuente de Información:** Identifica quién aporta los datos (Paciente, Familiar, EMS, Testigos).
*   **Referencia:** Médico o centro que deriva al paciente.
*   **Cobertura Sanitaria:** Selección de aseguradora/mutua (con visualización de logos) o paciente privado.

**2. Entrada Multimodal (`input_form`)**
*   **Texto Libre:** Campo principal para el "Motivo de Consulta".
*   **Captura Multimedia:**
    *   🎤 **Audio:** Grabación de voz para dictado de anamnesis (transcripción automática).
    *   📷 **Foto:** Captura directa desde webcam (ej. lesiones cutáneas).
    *   🎥 **Video:** Grabación de video corto (ej. marcha, movilidad).
    *   📁 **Archivos:** Subida de PDFs o imágenes externas.
*   **Importación HCE:** Simulación de conexión para traer informes previos.

**3. Entrevista Guiada Inteligente (`guided_interview`)**
Asistente tipo "acordeón" para estructurar síntomas comunes:
*   **Traumatismo:** Mecanismo, localización, sangrado activo.
*   **Dolor:** Mapa corporal interactivo, nivel (EVA), tipo, duración.
*   **Infección:** Fiebre (termómetro), síntomas asociados.
*   **Respiratorio:** Disnea (esfuerzo/reposo), tos.

**4. Historia de la Enfermedad Actual - HDA (`hda_form`)**
Desglose detallado del síntoma principal (Mnemotecnia ALICIA):
*   **Aparición:** Tiempo de inicio.
*   **Localización:** Zona específica e irradiación.
*   **Intensidad:** Escala EVA (1-10).
*   **Características:** Tipo de dolor (punzante, opresivo, etc.).
*   **Agravantes/Atenuantes:** Qué lo mejora o empeora.
*   **Tratamiento Domiciliario:** Medicación tomada antes de acudir.

**5. Antecedentes Clínicos (`patient_background_form`)**
Recopilación del historial médico del paciente:
*   **Alergias:** Medicamentosas, alimentarias, ambientales.
*   **Medicación:** Lista de fármacos activos (alerta de anticoagulantes).
*   **Patologías:** Enfermedades crónicas.
*   **Quirúrgicos:** Intervenciones previas, complicaciones anestesia.
*   **Gineco-Obstétrico:** Embarazo, FUR.
*   **Social:** Hábitos (tabaco/alcohol), situación funcional.

**6. Historia Clínica Integral (`extended_history`)**
Módulos especializados para casos complejos:
*   **Familiares:** Antecedentes hereditarios (Cardio, Cáncer).
*   **Psiquiatría:** Diagnósticos, riesgo suicida.
*   **Nutrición:** Dieta, disfagia, pérdida de peso.
*   **Viajes/Exposición:** Viajes recientes, contacto con animales.
*   **Sensorial:** Déficits visuales/auditivos, barrera idiomática.
*   **Forense:** Indicadores de violencia, abuso o negligencia.

**7. Valoración de Enfermería (`nursing_form`)**
Evaluación objetiva de cuidados y riesgos:
*   **Piel:** Integridad (úlceras, heridas), color, temperatura, edema.
*   **Riesgo de Caídas:** Historial previo, necesidad de ayuda.
*   **Riesgo de Aspiración:** Disfagia, orden de NPO.
*   **Seguridad:** Pulsera identificativa, inventario de pertenencias.

**8. Signos Vitales (`vital_signs/form`)**
Monitorización fisiológica con cálculo automático de scores:
*   **Parámetros:** FC, TA (Sistólica/Diastólica), SatO2, FR, Temperatura, Glucemia.
*   **Neurológico:** Escala Glasgow (GCS), reactividad pupilar.
*   **Hidratación:** Estado de mucosas y turgencia.
*   **Resultados en Tiempo Real:**
    *   *Triaje Vital:* Nivel de urgencia basado solo en constantes (Peor Caso).
    *   *NEWS2:* Score de alerta temprana para deterioro clínico.

#### C. Análisis IA (Gemini)
Al pulsar "Analizar con IA", el sistema compila toda la información (texto, vitales, transcripciones, imágenes) y la envía al modelo configurado.
*   **Salidas de la IA:**
    *   **Nivel de Triaje (1-5):** Escala Manchester/SET.
    *   **Especialidad Sugerida:** Traumatología, Medicina General, etc.
    *   **Resumen Clínico:** Síntesis del caso.
    *   **Signos Vitales Extraídos:** Si se mencionaron en el audio/texto y no se introdujeron manualmente.
    *   **Recomendaciones de Autocuidado:** Consejos para el paciente mientras espera.

#### D. Validación y Derivación
*   **Revisión Humana:** El profesional revisa la propuesta de la IA. Es obligatorio confirmar o modificar el Nivel y la Especialidad.
*   **Destino:** Selección de la sala de espera o box de destino (ej. "Espera Traumatología").

### 5.3 Módulo de Atención (Box)
**Objetivo:** Consulta médica y resolución del caso.

*   **Llamada a Paciente:** Selección de pacientes desde la lista de "Derivados" (Espera de Consulta).
*   **Visor de Triaje:** El médico visualiza el informe completo generado en triaje (motivo, vitales, clasificación, adjuntos).
*   **Finalización:** Registro del alta, ingreso o traslado, cerrando el flujo del paciente.

### 5.4 Gestión de Salas (Orquestador)
**Objetivo:** Visión global y control operativo del servicio de urgencias.

*   **Mapa de Salas:** Representación visual de todas las ubicaciones (Admisión, Esperas, Boxes).
*   **Drag & Drop:** Funcionalidad para mover pacientes entre salas arrastrando sus tarjetas. Útil para corregir errores de asignación o gestionar movimientos físicos no procedimentados.
*   **Métricas en Tiempo Real:** Ocupación por sala, tiempos de estancia.
*   **Detección de Anomalías:** Alertas sobre pacientes en salas "fantasma" o inactivas.

### 5.5 Gestión de Turnos
**Objetivo:** Planificación y control del personal en las distintas áreas.

*   **Calendario Semanal:** Vista visual de la cobertura de personal por días.
*   **Asignación de Turnos:** Creación de turnos temporales asociados a una sala específica.
*   **Resolución de Conflictos:** El sistema detecta automáticamente solapamientos de horarios o conflictos con asignaciones fijas ("Sala Base").
    *   *Prioridad:* Un turno activo temporal prevalece sobre la asignación fija del usuario.

### 5.6 Auditoría y Análisis (Control y Calidad)
**Objetivo:** Supervisión de calidad y mejora continua del modelo IA.

*   **Dashboard Principal:** KPIs de actividad (total triajes, tiempos medios, distribución por niveles).
*   **Validación Científica (Concordancia):**
    *   Análisis comparativo entre la decisión de la IA y la decisión final del humano.
    *   **Matriz de Confusión:** Visualización de discrepancias.
    *   **Métricas de Calidad:**
        *   *Sobre-Triaje:* Pacientes leves clasificados como graves (Riesgo de ineficiencia).
        *   *Sub-Triaje:* Pacientes graves clasificados como leves (Riesgo de seguridad clínica).
    *   **Análisis de Regeneración:**
        *   Tasa de regeneración de respuestas IA.
        *   Comparativa entre respuestas descartadas y la decisión final.
*   **Registro de Auditoría:** Tabla detallada con todos los eventos de triaje, permitiendo filtrar por fecha, nivel, usuario, etc.
*   **Logs Técnicos:**
    *   *Log de Transcripciones:* Revisión de audios y textos generados.
    *   *Log de Prompts:* Inspección de las instrucciones enviadas a la IA (para depuración).
    *   *Log de Archivos:* Histórico de ficheros procesados.

### 5.7 Reporte de Errores y Feedback
**Objetivo:** Canal de comunicación directo para mejora continua.

*   **Reporte Contextual:** Los usuarios pueden reportar errores o sugerencias desde cualquier punto de la aplicación.
*   **Captura de Contexto:** El sistema adjunta automáticamente información relevante (módulo, usuario, timestamp) al reporte.
*   **Gestión:** Los administradores pueden revisar, clasificar y gestionar estos reportes desde el panel de auditoría.

### 5.8 Configuración
**Objetivo:** Personalización del sistema sin tocar código.

*   **Información del Centro:** Nombre, Logo, Mensajes de cabecera.
*   **Gestión de Salas:** Creación y edición de salas.
    *   **Tipos de Sala:** `admision`, `triaje`, `box`, `consulta_ingreso`.
    *   **Subtipos:** `espera`, `atención` (o `atencion`).
*   **Gestión de Usuarios:** Alta/Baja de usuarios y asignación de roles.
*   **Configuración Médica (IA):**
    *   Configuración de valores predeterminados para signos vitales.

### 5.9 Administración de IA y Pruebas de Prompts
**Objetivo:** Gestión centralizada y segura del comportamiento de los modelos de IA.

El sistema incorpora un **Gestor de Prompts** (`PromptManager`) que permite iterar sobre la lógica clínica sin necesidad de despliegues de código.

#### A. Tipos de Prompts Gestionados
1.  **Gemini (IA Generativa):** Instrucciones base, rol ("Actúa como experto..."), y ejemplos *few-shot* para el triaje principal.
2.  **Simulación (Reglas):** Definición de palabras clave y umbrales para el modo de contingencia/simulado.
3.  **Transcripción:** Instrucciones para el post-procesado de audio (ej. "Traducir al español", "Extraer solo términos médicos").
4.  **Alertas Predictivas:** Lógica para la detección temprana de riesgos (Pre-Triaje).

#### B. Ciclo de Vida de Versiones
El sistema implementa un control de versiones estricto para garantizar la estabilidad:
*   **Borrador (Draft):** Versiones en edición. Son las únicas que permiten modificaciones y pruebas.
*   **Activa (Active):** La versión que está utilizando el sistema en producción. Solo puede haber una activa por tipo. Inmutable.
*   **Deprecada (Archived):** Versiones antiguas conservadas por histórico.

#### C. Funcionalidades del Editor
*   **Clonado:** Permite crear una nueva versión basada en una existente (ej. para iterar sobre la versión activa).
*   **Selección de Modelo:** Asignación dinámica del modelo (ej. `gemini-1.5-pro` vs `gemini-1.5-flash`) por versión de prompt.
*   **Auditoría:** Registro automático de autor, fecha de creación y fecha de modificación.

#### D. Área de Pruebas (Sandboxing)
Antes de activar un prompt, los administradores pueden validarlo en un entorno seguro:
*   **Input de Prueba:** Campo para introducir casos clínicos ficticios o texto de prueba.
*   **Ejecución Aislada:** El sistema ejecuta el prompt seleccionado (Borrador) contra el modelo real sin afectar a pacientes reales.
*   **Visualización JSON:** Muestra la respuesta cruda de la IA para verificar la estructura y contenido.

### 5.10 Dashboard Multi-Centro (Red Global)
**Objetivo:** Visión consolidada y comparativa de todos los centros de la red asistencial.

*   **Vista General:** KPIs agregados en tiempo real (Total Pacientes, Salas Activas, Tiempos de Espera).
*   **Comparativas:** Gráficos de barras para analizar carga de trabajo y ocupación entre centros.
*   **Alertas Globales:** Sistema centralizado de detección de saturación o bloqueos en cualquier punto de la red.
*   **Tecnología:** Alimentado por `MultiCenterService` que agrega datos directamente de la base de datos central.

### 5.11 Reporte Clínico Integral (PDF)
**Objetivo:** Generación de documentación clínica legal y transferible.

El sistema permite generar un informe en formato PDF al finalizar la validación del triaje. Este documento consolida toda la información del episodio:
*   **Datos Administrativos:** Identificación del paciente, fecha/hora, centro.
*   **Datos Clínicos:** Motivo de consulta, signos vitales, antecedentes, alergias.
*   **Análisis IA:** Nivel sugerido, justificación clínica detallada.
*   **Validación Humana:** Decisión final del profesional, nivel asignado y destino.

**Características Técnicas:**
*   Generación dinámica con `reportlab`.
*   Persistencia de datos completa (`patient_snapshot`) en el registro de triaje para garantizar la integridad del informe histórico.
*   Accesible desde:
    *   **Formulario de Validación:** Al finalizar el triaje.
    *   **Tarjeta de Paciente (Borrador):** Si existe un triaje en curso, se puede descargar un informe preliminar desde la lista de selección de pacientes.
    *   **Historial de Paciente:** Acceso a informes históricos.

### 5.12 Integración IoT (Simulación)
**Objetivo:** Automatización de la captura de constantes vitales.

El sistema simula la conectividad con dispositivos médicos en el box de triaje para agilizar la entrada de datos y reducir errores de transcripción.

**Funcionalidades:**
*   **Configuración por Sala:** Asignación de dispositivos específicos (Monitor Multiparamétrico, Tensiómetro, Pulsioxímetro, Termómetro) a cada sala de triaje desde el panel de administración.
*   **Captura Automática:** Botón "Capturar Signos Vitales" en el formulario de triaje que simula la conexión y lectura de datos.
*   **Feedback Visual:** Indicadores de conexión y éxito en la transferencia de datos.

**Nota:** Al ser una simulación, los valores generados son aleatorios dentro de rangos fisiológicos realistas, pero la arquitectura está preparada para integrarse con drivers reales en el futuro.

### 5.13 Grupos de Centros (Multi-Tenant)
**Objetivo:** Agrupación lógica de centros para gestión consolidada.

Permite crear estructuras organizativas superiores (ej: "Zona Norte", "Hospitales Privados") para facilitar la gestión y el análisis de datos en redes de centros.

**Funcionalidades:**
*   **Gestión de Grupos:** Creación, edición y eliminación de grupos desde `Configuración > Centro > Grupos`.
*   **Asignación de Centros:** Vinculación de múltiples centros a un grupo.
*   **Dashboard Filtrado:** El Dashboard Multi-Centro permite filtrar métricas y alertas por grupo específico, facilitando la supervisión regional o temática.

---

## 6. Modos Avanzados de Operación

### 6.1 Modo Formación (Training Mode)
Diseñado para el entrenamiento de nuevo personal sin afectar a los datos reales de pacientes.
*   **Simulación:** Permite realizar triajes completos con datos ficticios.
*   **Evaluación de Competencia:** El sistema presenta casos clínicos predefinidos y compara la decisión del usuario con el "Gold Standard" clínico, ofreciendo feedback inmediato sobre aciertos y errores.
*   **Aislamiento de Datos:** Los registros generados en este modo se marcan con el flag `is_training=True` y se excluyen de las estadísticas operativas oficiales.

### 6.2 Modo Contingencia (Offline Mode)
Garantiza la continuidad operativa ante fallos de conexión a internet o caída de los servicios de IA.
*   **Activación:** Manual (por el supervisor) o automática (al detectar fallos repetidos de conexión).
*   **Funcionalidad Reducida:**
    *   Se desactiva el análisis de IA (Gemini).
    *   El sistema pasa a un modo de "Triaje Manual Estructurado" basado en reglas locales.
*   **Almacenamiento Local:** Los datos se guardan temporalmente en el navegador del usuario.
*   **Sincronización:** Al restablecerse la conexión, el sistema permite sincronizar los registros locales con la base de datos central, marcándolos como "Generados en Contingencia".

---

## 7. Arquitectura Técnica

### 7.1 Stack Tecnológico
*   **Frontend:** Streamlit (Python) - Framework de UI reactiva.
*   **Backend Logic:** Python 3.10+ (Servicios modulares en `src/services`).
*   **Base de Datos:** MongoDB 6.0+ (NoSQL Document Store).
*   **IA Generativa:** Google Vertex AI / Gemini API (Modelos: `gemini-1.5-flash`, `gemini-1.5-pro`).
*   **Machine Learning:** Scikit-learn (Random Forest para predicciones tabulares).
*   **Reportes:** ReportLab (Generación programática de PDFs).
*   **Multimedia:** `streamlit-webrtc` (Procesamiento de audio/video en tiempo real).

### 7.2 Estructura del Proyecto
El código sigue una arquitectura modular basada en servicios:
*   `src/ui`: Componentes de interfaz (Vistas y Widgets).
*   `src/services`: Lógica de negocio (Triaje, Pacientes, IA, Reportes).
*   `src/db`: Capa de persistencia (Repositorios y Modelos Pydantic).
*   `src/core`: Utilidades transversales (Configuración, Logging).

### 7.3 Despliegue
*   **Contenerización:** Docker Ready (Dockerfile optimizado para Streamlit).
*   **Estado:** Gestión de sesión mediante `st.session_state` (Server-side).

---

## 8. Modelo de Datos (Esquema Alto Nivel)

El sistema utiliza un esquema flexible pero estructurado en MongoDB. Las colecciones principales son:

### 8.1 `people` (Master Patient Index)
Repositorio único de identidades.
*   `_id`: UUID.
*   `nombre`, `apellidos`: Datos demográficos.
*   `identificaciones`: Array de documentos (DNI, SS, Pasaporte).
*   `fecha_nacimiento`: Para cálculo de edad.

### 8.2 `triage_records` (Episodios Clínicos)
Registro central de cada acto de triaje.
*   `patient_id`: Link a `people`.
*   `status`: `draft` (borrador), `completed` (validado), `discarded`.
*   `patient_snapshot`: Copia inmutable de los datos clínicos en el momento del triaje (evita inconsistencias si la ficha del paciente cambia).
*   `ia_result`: Respuesta completa de la IA (Nivel, Razones, Especialidad).
*   `ai_responses`: Array histórico de regeneraciones (Auditoría).
*   `final_priority`: Nivel validado por el humano.

### 8.3 `patient_flow` (Estado Operativo)
Tabla de estado actual para el orquestador.
*   `patient_code`: Link a `people`.
*   `sala_actual`: Código de sala.
*   `estado`: `EN_ESPERA`, `EN_TRIAJE`, `DERIVADO`.
*   `timestamp_entrada`: Para cálculo de tiempos de espera.

### 8.4 `config` & `clinical_options`
Configuración dinámica del sistema.
*   `config`: Datos del centro, definición de salas, usuarios y roles.
*   `clinical_options`: Catálogos para desplegables (Alergias, Síntomas, etc.).

---

## 9. Seguridad y Privacidad

### 9.1 Cumplimiento Normativo (GDPR/LOPD)
*   **Minimización de Datos:** Solo se recolectan los datos estrictamente necesarios para el acto clínico.
*   **Derecho al Olvido:** Arquitectura preparada para anonimización de registros en `people`.

### 9.2 Auditoría y Trazabilidad
*   **Logs de Acción:** Cada cambio de estado, validación o edición queda registrado con Timestamp y Usuario responsable.
*   **Trazabilidad IA:** Se almacena el prompt exacto y la respuesta generada para cada decisión algorítmica, permitiendo auditorías forenses de la IA.

### 9.3 Seguridad de la Información
*   **Acceso Basado en Roles (RBAC):** Permisos granulares definidos en `permissions_service.py`.
*   **Gestión de Sesión:** Cookies seguras y expiración de sesión.
*   **Protección de Datos:** Los datos sensibles (historial médico) se almacenan en colecciones separadas con acceso restringido.

---

## Anexo A: Opciones Clínicas (Base de Datos)

Valores extraídos de la colección `clinical_options`, utilizados para poblar los selectores dinámicos en la entrevista clínica y antecedentes.

### allergy_agent
- anesthetics_local
- cefalosporinas
- clorhexidina
- contrast_iodine
- contrastes
- egg
- fish
- fruits_rosaceae
- gluten
- lactose
- latex
- milk_protein
- nsaids
- nuts
- opioids
- penicillin
- penicilina
- shellfish
- soy
- sulfamidas
- sulfonamides

### allergy_reaction
- anaphylaxis
- angioedema
- bronchospasm
- gi_symptoms
- hypotension
- urticaria

### allergy_symptoms
- anaphylaxis
- angioedema
- diarrhea
- dyspnea
- hypotension
- nausea
- pruritus
- rash
- urticaria
- wheezing

### animal_contact
- birds
- dogs_cats
- exotic
- farm
- horses
- reptiles
- rodents
- wild

### belongings
- cane
- clothing
- dentures
- glasses
- hearing_aid
- jewelry
- keys
- mobile_phone
- walker
- wallet

### dementia
- alzheimer
- frontotemporal
- intellectual_disability
- lewy_body
- mild_cognitive
- mixed
- parkinson
- vascular

### diet_type
- diabetic
- diet_vegan
- diet_vegetarian
- gluten_free
- low_sodium
- normal
- pureed
- renal
- soft

### family_cancer
- breast
- colon
- melanoma
- ovary
- pancreas
- prostate

### family_cardio
- arrhythmia
- cardiomyopathy
- mi_early
- stroke
- sudden_death

### family_diabetes
- t1dm
- t2dm
- thyroid

### family_genetic
- cf
- hemochromatosis
- huntington
- marfan
- thrombophilia

### forensic_cultural
- family_decision
- gender_pref_pro
- language_barrier
- modesty

### forensic_religion
- diet_halal
- diet_kosher
- jehovah_witness
- no_pork
- prayer_times
- ramadan
- rel_vegetarian

### forensic_violence
- child_abuse
- domestic
- elder_abuse
- gender_violence
- neglect
- physical
- psychological
- self_harm
- sexual

### functional_status
- baston
- encamado
- independent
- independiente
- mild_dependence
- moderate_dependence
- severe_dependence
- silla
- total_dependence

### gi_category
- infection
- other
- pain
- respiratory
- trauma

### gi_infection_symptoms
- Diarrea
- Dolor al orinar
- Dolor de garganta
- Mocos
- Tos
- Vómitos

### gi_pain_type
- Cólico (va y viene)
- Opresivo (peso)
- Punzante (pinchazo)
- Quemante (ardor)
- Sordo (constante)

### gi_trauma_location
- Cabeza/Cara
- Cadera/Pierna
- Cuello
- Hombro/Brazo
- Mano/Muñeca
- Rodilla
- Tobillo/Pie
- Tórax/Espalda

### gi_trauma_mechanism
- Accidente Tráfico
- Caída
- Corte/Herida
- Deportivo
- Golpe directo

### immuno_onco
- asplenia
- autoimmune_sys
- cancer_hematologic
- cancer_history
- cancer_metastatic
- cancer_solid
- chemo_active
- corticoids_chronic
- hiv
- immunotherapy
- neutropenia
- pid
- radio_active
- transplant_marrow
- transplant_organ

### implant
- cochlear
- insulin_pump
- iud
- joint_prosthesis_hip
- joint_prosthesis_knee
- osteosynthesis
- pacemaker
- portacath
- stent_coronary
- stent_vascular
- valve_bio
- valve_mechanic
- vp_shunt

### living_situation
- acompanado
- alone
- caregiver
- family
- homeless
- institucionalizado
- institution
- parents
- shelter
- sin_hogar
- solo

### mrsa_type
- acinetobacter
- blee
- c_diff
- candida_auris
- kpc
- mrsa
- pseudomonas_mdr
- vre

### occupational_risk
- agriculture
- chemical
- construction
- education
- food_processing
- healthcare
- laboratory
- mining
- office

### pain_characteristics
- burning
- colicky
- dull
- electric
- oppressive
- sharp
- stabbing
- throbbing

### pain_location
- abdominal_chronic
- cervical
- fibromyalgia
- headache
- joint_hip
- joint_knee
- joint_shoulder
- lumbar
- neuropathic
- pelvic

### pathology
- asma
- cirrosis
- demencia
- diabetes_1
- diabetes_2
- dialisis
- epilepsia
- epoc
- fa
- hta
- iam_previo
- ictus
- insuf_cardiaca
- irc

### psych_diagnosis
- anxiety
- bipolar
- depression
- eating_disorder
- ocd
- personality
- ptsd
- schizophrenia
- substance_abuse

### psych_medication
- antipsychotic_atypical
- antipsychotic_typical
- benzodiazepine
- mood_stabilizer
- snri
- ssri
- stimulant
- tricyclic

### sensory_auditory
- deaf_total
- hypoacusis
- tinnitus

### sensory_language
- arabic
- bambara
- bengali
- bulgarian
- chinese
- english
- french
- german
- hindi
- italian
- japanese
- korean
- polish
- portuguese
- romanian
- russian
- sign_language
- spanish
- tagalog
- ukrainian
- urdu
- vietnamese
- wolof

### sensory_prosthesis
- dental_removable
- limb_lower_ak
- limb_lower_bk
- limb_upper
- ocular

### sensory_visual
- blind_total
- glaucoma
- low_vision
- maculopathy

### social_habit
- alcohol
- alcohol_dependence
- alcohol_risk
- alcohol_social
- drogas
- drugs_cannabis
- drugs_cocaine
- drugs_opioids
- drugs_synthetic
- ex_tabaco
- gambling
- tabaco
- tobacco_active
- tobacco_ex

### vaccine
- covid19
- flu
- hepatitis_a
- hepatitis_b
- hpv
- meningococcus
- mmr
- pneumococcus
- tetanus
- zoster

---

## Anexo B: Referencias de Signos Vitales

### Frecuencia Cardíaca (fc)
*Unidad: ppm | Rango Normal: 60-100*

| Rango | Prioridad | Etiqueta | Color |
| :--- | :--- | :--- | :--- |
| 0 - 39 | 3 (Alta) | Bradicardia Extrema | 🔴 Red |
| 40 - 49 | 2 (Media) | Bradicardia Severa | 🟠 Orange |
| 50 - 59 | 1 (Baja) | Bradicardia Leve | 🟡 Yellow |
| 60 - 100 | 0 (Normal) | Normal | 🟢 Green |
| 101 - 120 | 1 (Baja) | Taquicardia Leve | 🟡 Yellow |
| 121 - 140 | 2 (Media) | Taquicardia Severa | 🟠 Orange |
| 141 - 300 | 3 (Alta) | Taquicardia Extrema | 🔴 Red |

### Saturación O2 (spo2)
*Unidad: % | Rango Normal: 95-100*

| Rango | Prioridad | Etiqueta | Color |
| :--- | :--- | :--- | :--- |
| 0 - 89 | 3 (Alta) | Hipoxia Crítica | 🔴 Red |
| 90 - 94 | 2 (Media) | Hipoxia Moderada | 🟠 Orange |
| 95 - 100 | 0 (Normal) | Normal | 🟢 Green |

### Temperatura (temp)
*Unidad: °C | Rango Normal: 36-37.5*

| Rango | Prioridad | Etiqueta | Color |
| :--- | :--- | :--- | :--- |
| 0 - 34.9 | 2 (Media) | Hipotermia | 🟠 Orange |
| 35 - 35.9 | 1 (Baja) | Hipotermia Leve | 🟡 Yellow |
| 36 - 37.5 | 0 (Normal) | Afebril | 🟢 Green |
| 37.6 - 38.4 | 1 (Baja) | Febrícula | 🟡 Yellow |
| 38.5 - 40 | 2 (Media) | Fiebre Alta | 🟠 Orange |
| 40.1 - 50 | 3 (Alta) | Hiperpirexia | 🔴 Red |

### Presión Sistólica (pas)
*Unidad: mmHg | Rango Normal: 100-140*

| Rango | Prioridad | Etiqueta | Color |
| :--- | :--- | :--- | :--- |
| 0 - 79 | 3 (Alta) | Hipotensión Severa | 🔴 Red |
| 80 - 99 | 2 (Media) | Hipotensión | 🟠 Orange |
| 100 - 140 | 0 (Normal) | Normal | 🟢 Green |
| 141 - 160 | 1 (Baja) | Hipertensión Leve | 🟡 Yellow |
| 161 - 200 | 2 (Media) | Hipertensión Moderada | 🟠 Orange |
| 201 - 300 | 3 (Alta) | Crisis Hipertensiva | 🔴 Red |

### Presión Diastólica (pad)
*Unidad: mmHg | Rango Normal: 60-90*

| Rango | Prioridad | Etiqueta | Color |
| :--- | :--- | :--- | :--- |
| 0 - 130 | 0 (Normal) | Normal/Baja | 🟢 Green |
| 131 - 200 | 3 (Alta) | Hipertensión Diastólica Severa | 🔴 Red |

### Frecuencia Respiratoria (fr)
*Unidad: rpm | Rango Normal: 12-20*

| Rango | Prioridad | Etiqueta | Color |
| :--- | :--- | :--- | :--- |
| 0 - 8 | 3 (Alta) | Bradipnea Extrema | 🔴 Red |
| 9 - 11 | 2 (Media) | Bradipnea | 🟠 Orange |
| 12 - 20 | 0 (Normal) | Normal | 🟢 Green |
| 21 - 24 | 1 (Baja) | Taquipnea Leve | 🟡 Yellow |
| 25 - 29 | 2 (Media) | Taquipnea Moderada | 🟠 Orange |
| 30 - 100 | 3 (Alta) | Taquipnea Severa | 🔴 Red |

### Glasgow (gcs)
*Unidad: pts | Rango Normal: 15*

| Rango | Prioridad | Etiqueta | Color |
| :--- | :--- | :--- | :--- |
| 3 - 8 | 3 (Alta) | Coma (Grave) | 🔴 Red |
| 9 - 12 | 2 (Media) | Moderado | 🟠 Orange |
| 13 - 14 | 1 (Baja) | Leve | 🟡 Yellow |
| 15 - 15 | 0 (Normal) | Consciente | 🟢 Green |

### Escala Dolor (eva)
*Unidad: EVA | Rango Normal: 0-3*

| Rango | Prioridad | Etiqueta | Color |
| :--- | :--- | :--- | :--- |
| 0 - 3 | 0 (Normal) | Leve | 🟢 Green |
| 4 - 6 | 1 (Baja) | Moderado | 🟡 Yellow |
| 7 - 8 | 2 (Media) | Severo | 🟠 Orange |
| 9 - 10 | 3 (Alta) | Insoportable | 🔴 Red |
