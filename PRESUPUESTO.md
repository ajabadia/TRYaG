# Presupuesto y Plan de Implantación: Asistente de Triaje IA

**Proyecto:** Implantación de Sistema de Triaje Inteligente con Soporte a la Decisión Clínica (IA)  
**Cliente:** Entorno Hospitalario (Madrid)  
**Proveedor:** Equipo de Desarrollo (Zaragoza)  
**Fecha:** 07 de Diciembre de 2024  
**Versión:** 1.0

---

## 1. Resumen Ejecutivo

La presente propuesta detalla los costes y tiempos necesarios para la **implantación integral** del sistema "Asistente de Triaje IA" en un entorno hospitalario real. El proyecto abarca desde la toma de requisitos hasta el soporte post-arranque, incluyendo el desarrollo de software a medida, integración con HIS (Hospital Information System), formación del personal y gestión del cambio.

*   **Duración Estimada:** 8 Meses (33 Semanas)
*   **Metodología:** Híbrida (Gestión Waterfall para hitos + Desarrollo Agile/Scrum).
*   **Presupuesto Total Estimado:** **248.500 € + IVA** (Aprox.)

---

## 2. Equipo de Proyecto

Se propone un equipo multidisciplinar de **5 personas** con dedicación variable según la fase del proyecto.

| Perfil | Nivel | Tarifa Hora | Responsabilidad |
| :--- | :--- | :--- | :--- |
| **Jefe de Proyecto (PM)** | Senior | 85 €/h | Interlocución, seguimiento, gestión de riesgos y planificación. |
| **Arquitecto de Software** | Senior | 75 €/h | Diseño técnico, seguridad, integración HIS y supervisión de IA. |
| **Analista Funcional** | Senior | 65 €/h | Toma de requisitos, definición de reglas clínicas y manuales. |
| **Desarrollador Full-Stack** | Mid/Senior | 60 €/h | Desarrollo de frontend (Streamlit), backend y lógica de negocio. |
| **Ingeniero QA / Tester** | Mid | 50 €/h | Pruebas unitarias, integración, carga y validación clínica. |

---

## 3. Cronograma y Fases (Roadmap)

El proyecto se estructura en **6 Fases** principales, con un núcleo de desarrollo iterativo de **10 Sprints**.

### Fase 1: Inicio y Análisis (Semana 1-2)
*   Reunión de Lanzamiento (Kick-off) en Madrid.
*   Toma de requisitos detallada con Dirección Médica y Enfermería.
*   Definición de KPIs y objetivos de éxito.

### Fase 2: Diseño y Arquitectura (Semana 3-5)
*   Diseño técnico de la integración con HIS (HL7/FHIR).
*   Diseño de UX/UI y flujos de navegación.
*   Definición del modelo de datos y seguridad (GDPR).

### Fase 3: Construcción (Desarrollo Agile) (Semana 6-25)
Ejecución en **10 Sprints de 2 semanas**:

*   **Sprint 1-2:** Infraestructura, Autenticación y Gestión de Usuarios (RBAC).
*   **Sprint 3-4:** Módulo de Admisión, Identificación y Sala de Espera.
*   **Sprint 5-6:** Motor de Triaje Core (Algoritmos SET/Manchester) y Trazabilidad.
*   **Sprint 7-8:** **Integración IA:** Conexión Gemini, RAG (Protocolos) y Transcripción de Voz.
*   **Sprint 9:** Módulo de Gestión de Salas (Orquestador) y Dashboards.
*   **Sprint 10:** Auditoría, Reportes PDF e Integraciones finales (Webhooks/Tickets).

### Fase 4: Pruebas y QA (Semana 26-28)
*   Pruebas de aceptación de usuario (UAT).
*   Auditoría de seguridad y protección de datos.
*   Simulacros de carga y estrés.

### Fase 5: Despliegue y Formación (Semana 29-31)
*   Instalación en infraestructura hospitalaria (On-premise/Cloud).
*   **Formación presencial** a 50 usuarios.

### Fase 6: Soporte y Cierre (Semana 32-33)
*   Soporte presencial durante el arranque (Hypercare).
*   Reunión de Cierre y entrega de documentación final.

---

## 4. Detalle de Costes y Tiempos

### 4.1 Desarrollo e Ingeniería (Estimación por Esfuerzo)

| Concepto | Horas Est. | Coste Est. (€) | Notas |
| :--- | :--- | :--- | :--- |
| **Gestión de Proyecto** | 320 h | 27.200 € | 10h/semana x 32 sem aprox. |
| **Análisis y Diseño** | 240 h | 16.800 € | Fases iniciales intensivas. |
| **Desarrollo (2 Devs)** | 1.600 h | 96.000 € | 2 FTE durante fase construcción. |
| **Integración IA & Datos** | 300 h | 22.500 € | Arquitecto (RAG, Prompt Engineering). |
| **QA y Pruebas** | 240 h | 12.000 € | Pruebas continuas y fase QA. |
| **Documentación** | 120 h | 7.800 € | Manuales, técnica y funcional. |
| **TOTAL INGENIERÍA** | **2.820 h** | **182.300 €** | |

### 4.2 Logística y Desplazamientos (Zaragoza - Madrid)

Se contempla un modelo híbrido con presencia física intensiva para garantizar la adherencia al proyecto.
*   **Régimen:** 2 consultores desplazados 3 días/semana (Mar-Jue) durante la fase crítica (6 meses / 24 semanas).
*   **Eventos Especiales:** 3 personas extra para Kick-off, Comités (x3) y Cierre (5 viajes).

| Concepto | Unidades | Coste Unit. | Coste Total (€) | Detalle |
| :--- | :--- | :--- | :--- | :--- |
| **AVE Zgz-Mad (Ida/Vuelta)** | 144 viajes | 90 € | 12.960 € | 2 pers x 3 sem x 24 sem. |
| **Hotel Madrid (Noche)** | 144 noches | 130 € | 18.720 € | 2 pers x 3 noches x 24 sem. |
| **Dietas (Manutención)** | 144 días | 60 € | 8.640 € | Régimen de dietas estándar. |
| **Viajes Eventos (3 pax)** | 15 viajes | 90 € | 1.350 € | 3 pers x 5 eventos. |
| **Hotel/Dietas Eventos** | 15 packs | 190 € | 2.850 € | Pernocta eventos especiales. |
| **TOTAL LOGÍSTICA** | | | **44.520 €** | |

### 4.3 Formación y Gestión del Cambio

Formación presencial para **50 profesionales** (médicos, enfermería, admisión).
*   **Estrategia:** Grupos reducidos de 5 personas para formación práctica (Roleplay).
*   **Volumen:** 10 Grupos x 8 horas/sesión = 80 horas de impartición.

| Concepto | Horas | Coste Unit. | Coste Total (€) | Detalle |
| :--- | :--- | :--- | :--- | :--- |
| **Preparación Materiales** | 40 h | 65 € | 2.600 € | Guías rápidas, vídeos, entorno demo. |
| **Impartición Formación** | 80 h | 75 € | 6.000 € | Instructor experto in-situ. |
| **Soporte Arranque (Guardia)**| 80 h | 60 € | 4.800 € | 2 personas x 5 días x 8h (Semana 1). |
| **TOTAL FORMACIÓN** | | | **13.400 €** | |

### 4.4 Infraestructura y Licencias (Anual - Estimado)

| Concepto | Coste Mensual | Coste Anual (€) | Notas |
| :--- | :--- | :--- | :--- |
| **Google Vertex AI / Gemini** | ~300 € | 3.600 € | Variable según volumen de tokens. |
| **Hosting (AWS/Azure)** | ~400 € | 4.800 € | Servidores App + MongoDB Atlas Pro. |
| **TOTAL INFRAESTRUCTURA** | | **8.400 €** | A contratar por el cliente. |

---

## 5. Tabla Resumen de Costes (Exportable)

Esta tabla resume las partidas principales para su volcado a herramientas de gestión (Excel/SAP).

| ID | Concepto | Cantidad | Unidad | Precio Unitario | Total (€) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 | Gestión de Proyecto | 320 | Horas | 85,00 € | 27.200,00 € |
| 1.2 | Análisis y Diseño Funcional | 240 | Horas | 65,00 € | 15.600,00 € |
| 1.3 | Arquitectura y Desarrollo AI | 300 | Horas | 75,00 € | 22.500,00 € |
| 1.4 | Desarrollo de Software (Core) | 1.600 | Horas | 60,00 € | 96.000,00 € |
| 1.5 | Aseguramiento Calidad (QA) | 240 | Horas | 50,00 € | 12.000,00 € |
| 2.1 | Viajes y Desplazamientos | 159 | Viajes | 90,00 € | 14.310,00 € |
| 2.2 | Alojamiento y Dietas | 159 | Packs | 190,00 € | 30.210,00 € |
| 3.1 | Elaboración Material Formativo | 40 | Horas | 65,00 € | 2.600,00 € |
| 3.2 | Impartición Formación | 80 | Horas | 75,00 € | 6.000,00 € |
| 3.3 | Soporte al Arranque (In-situ) | 80 | Horas | 60,00 € | 4.800,00 € |
| **TOTAL** | **PROYECTO LLAVE EN MANO** | | | | **231.220,00 €** |

*(Nota: Infraestructura y licencias de terceros excluidas del total de servicios profesionales. IVA no incluido).*

---

## 7. Costes de Infraestructura y Operación (OPEX)

Se presentan dos escenarios de despliegue para la infraestructura base (Servidor de Aplicación + Base de Datos). La capa de IA Generativa (Google Gemini) es siempre Cloud (SaaS) y se calcula por separado.

### 7.1 Escenario A: Despliegue 100% In-House (On-Premise)
*Infraestructura alojada en el CPD del Hospital.*

| Concepto | Coste Mensual Est. | Coste Anual | Detalles |
| :--- | :--- | :--- | :--- |
| **Servidor Físico (Amortización)** | 150,00 € | 1.800,00 € | Parte proporcional de servidor (ej. Dell PowerEdge). |
| **Licencia MongoDB Enterprise** | 600,00 € | 7.200,00 € | Licencia "Advanced" self-managed (Opcional, puede usarse Community GRATIS). |
| **Mantenimiento CPD** | 200,00 € | 2.400,00 € | Electricidad, Refrigeración, Red, Backups locales. |
| **SysAdmin (Interno)** | 400,00 € | 4.800,00 € | 10% de dedicación de un técnico del hospital. |
| **TOTAL IN-HOUSE** | **1.350,00 €** | **16.200,00 €** | *(Con soporte Enterprise)* |

*(Nota: Si se usa MongoDB Community y hardware existente, el coste externo es ~0€, pero asume riesgo interno)*.

### 7.2 Escenario B: Despliegue Cloud (AWS + MongoDB Atlas)
*Infraestructura gestionada y escalable (Recomendado).*

| Concepto | Coste Mensual Est. | Coste Anual | Detalles |
| :--- | :--- | :--- | :--- |
| **Computación (AWS EC2)** | 120,00 € | 1.440,00 € | Instancia m5.large (2 vCPU, 8GB RAM) reservada 1 año. |
| **MongoDB Atlas (M30)** | 350,00 € | 4.200,00 € | Cluster Dedicado, Backups auto, Alta Disponibilidad. |
| **Almacenamiento (S3)** | 30,00 € | 360,00 € | Guardado de imágenes/archivos médicos (500GB est). |
| **Transferencia de Datos** | 50,00 € | 600,00 € | Tráfico de salida (Egress) estimado. |
| **TOTAL CLOUD** | **550,00 €** | **6.600,00 €** | **Alta Disponibilidad incluida** |

---

### 7.3 Consumo de IA (Gemini API) - Simulación de Costes

Coste variable basado en el uso real ("Pay-as-you-go"). Se realizan estimaciones proyectando el uso de modelos de nueva generación (**Gemini 2.5** y **Gemini 3.0**), asumiendo una política de precios competitiva similar a la actual para modelos "Flash" y "Pro".

#### Perfil de Uso Diario (Estimación)
Considerando una carga de **100 Triajes/día** completos, con uso intensivo de capacidades multimodales:

| Recurso por Caso | Cantidad Med. | Tokens Input (Aprox) | Tokens Output (Aprox) | Notas |
| :--- | :--- | :--- | :--- | :--- |
| **Contexto Clinico** | 1 (Texto) | 3.000 | 800 | Prompt Sistema + Historia + Vitales. |
| **Audio (Voz)** | 2 clips (90s) | 2.500 | - | ~25 tokens/segundo de audio. |
| **Imágenes** | 1 foto | 258 | - | 258 tokens fijos por imagen. |
| **Video** | 0.05 (1/20) | 150 | - | Video breve (10s) ocasional. |
| **Shift Handoff** | 4 al día | 15.000 | 2.000 | Contexto masivo de pacientes recientes. |

#### Cálculo de Tokens Diarios
*   Input Diario: (100 casos * ~5.900) + (4 informes * 15.000) = **650.000 Tokens Input**
*   Output Diario: (100 casos * ~800) + (4 informes * 2.000) = **88.000 Tokens Output**

#### Escenarios de Coste (Comparativa Generacional)

Se comparan los costes actuales (**1.5**) con las proyecciones para la próxima generación (**2.5** y **3.0**), permitiendo visualizar diferentes estrategias de adopción.

| Modelo | Generación | Perfil | Precio Input (/1M) | Precio Output (/1M) | Coste Mensual |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gemini 1.5 Flash** | Actual | Velocidad/Coste | 0,075 $ | 0,30 $ | **~2,40 $** |
| **Gemini 1.5 Pro** | Actual | Razonamiento | 3,50 $ | 10,50 $ | **~96,00 $** |
| **Gemini 2.5 Flash** | Futuro (Est) | Velocidad+ | 0,075 $ | 0,30 $ | **~2,40 $** |
| **Gemini 3.0 Pro** | Futuro (Est) | Razonamiento++ | 3,50 $ | 10,50 $ | **~96,00 $** |

> [!TIP]
> **Estrategia Recomendada (Híbrida):** Utilizar modelos **Flash (1.5/2.5)** para el 95% de los casos (Triaje rutinario, transcripción) por su coste residual (<3€/mes). Reservar modelos **Pro (1.5/3.0)** exclusivamente para casos complejos o de "Segunda Opinión", manteniendo el coste total del servicio por debajo de los 15€/mes.

---

## 8. Consideraciones y Supuestos

1.  **Colaboración del Cliente:** Se asume disponibilidad del personal sanitario para las reuniones de definición (Fase 1) y validación (Fase 4).
2.  **Entorno Tecnológico:** El hospital proveerá los accesos necesarios (VPN, Credenciales) a los entornos de pruebas del HIS para la integración.
3.  **Propiedad Intelectual:** El código fuente desarrollado será propiedad del cliente tras el pago final, salvo librerías de terceros u open source.
4.  **Garantía:** Se incluye un periodo de garantía correctiva de 3 meses tras el arranque.

---

**Firmado:**

*Antigravity AI Solutions*
*División de Consultoría Sanitaria*

---

# ANEXO I: Módulo "Segunda Opinión Experta" (Add-on)

Este anexo detalla la valoración económica para la incorporación del módulo de **"Razonamiento Clínico Avanzado"**, diseñado para casos complejos que requieren un análisis profundo mediante IA de última generación (Gemini 2.5/3.0 Pro).

## A. Descripción del Módulo
Herramienta independiente que permite al facultativo solicitar una revisión exhaustiva de un caso. El sistema agrega toda la información disponible (Historia, Triajes, Imagen, Audio, Constantes) y utiliza un modelo "Reasoning ++" para ofrecer diagnósticos diferenciales y recomendaciones fundamentadas.

## B. Valoración Económica (Comparativa)

Se presentan dos escenarios de contratación:

### Escenario 1: Desarrollo "Standalone" (Independiente)
*Si se contrata como proyecto aislado a posteriori.*

| Concepto | Esfuerzo | Coste Est. | Notas |
| :--- | :--- | :--- | :--- |
| **Gestión y Análisis** | 40 h | 3.200 € | Toma de requisitos aislada. |
| **Infraestructura Base** | 60 h | 4.500 € | Setup de entorno, seguridad, BB.DD. |
| **Módulo Agregador Datos** | 80 h | 4.800 € | Conectores a HIS/Archivos. |
| **Integración IA (Prompting)** | 60 h | 4.500 € | Ingeniería de prompts complejos. |
| **Frontend Específico** | 40 h | 2.400 € | Interfaz de usuario dedicada. |
| **Total Standalone** | **280 h** | **19.400 €** | Ineficiente por duplicidad de base. |

### Escenario 2: Desarrollo "Integrado" (Paralelo al Principal)
*Si se desarrolla aprovechando las sinergias del proyecto principal.*

| Concepto | Esfuerzo | Coste Est. | Ahorro / Sinergia |
| :--- | :--- | :--- | :--- |
| **Gestión y Análisis** | 15 h | 1.200 € | Compartido con Fase 1. |
| **Infraestructura Base** | 5 h | 0 € | Ya incluida en proyecto principal (API Setup). |
| **Módulo Agregador Datos** | 40 h | 2.400 € | Gestión de Archivos + RAG Service. |
| **Integración IA (Reasoning)** | 60 h | 4.500 € | Prompting Multimodal + Contexto Complejo. |
| **Frontend Específico** | 30 h | 1.800 € | UI Carga Archivos + Cards + PDF Report. |
| **Total Integrado** | **150 h** | **9.900 €** | **Más valor por menor coste marginal** |

## D. Paquete Documental y Procedimientos (NUEVO)

Se incluye una partida específica para el aseguramiento normativo y documental del piloto:

| Concepto | Entregables | Coste Est. |
| :--- | :--- | :--- |
| **Documentación Funcional** | Manual de Usuario, Mapas de Flujo (Mermaid), Guías Rápidas. | 1.500 € |
| **Documentación Técnica** | Especificación API (OpenAPI), Arquitectura, Diccionario de Datos. | 1.800 € |
| **Procedimientos (SOPs)** | Procedimientos Normalizados de Trabajo, Guía de Despliegue. | 1.200 € |
| **Kit Legal y Compliance** | Plantillas GDPR, Consentimiento Informado, Logs de Auditoría. | 2.000 € |
| **TOTAL DOCUMENTACIÓN** | **Pack Completo** | **6.500 €** |

## C. Costes Operativos Específicos (IA)

Dado el uso de modelos de razonamiento (Gemini 2.5/3.0 Pro), el coste por consulta es superior al estándar, pero el volumen esperado es bajo (solo casos complejos).

*   **Tokens por Consulta:** ~50k Input (Contexto masivo) / 2k Output.
*   **Coste Unitario (Gemini 2.5 Pro):** ~0,20 € / consulta.
*   **Estimación Mensual:** 5 consultas/día x 30 días = **30 €/mes**.

> [!IMPORTANT]
> Se recomienda encarecidamente la contratación en modalidad **Integrada (Escenario 2)** para maximizar la inversión, aprovechando la infraestructura de seguridad, usuarios y datos ya desplegada.
