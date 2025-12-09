# Defensa de Trabajo Fin de Máster (TFM)
## Asistente de Triaje Inteligente con IA Generativa y RAG

### 1. Introducción y Contexto
*   **Título del Proyecto:** Desarrollo de un Asistente de Triaje Clínico basado en IA Generativa.
*   **Problemática:** Saturación de los servicios de urgencias, variabilidad en la clasificación de pacientes y fatiga cognitiva del personal sanitario.
*   **Objetivo:** Desarrollar una herramienta de apoyo a la decisión clínica (CDSS) que optimice el flujo de triaje, reduzca tiempos de espera y estandarice la aplicación de protocolos.

### 2. Marco Teórico y Tecnológico
*   **Arquitectura Híbrida:** Combinación de IA Generativa (Google Gemini 1.5 Flash) para el razonamiento clínico y Algoritmos Deterministas (Random Forest/NEWS2) para la predicción operativa.
*   **Gestión de IA Robusta:**
    *   **PromptManager:** Sistema centralizado en base de datos para versionado y A/B testing de prompts clínicos sin despliegues.
    *   **Modo Contingencia:** Fallback automático "Graceful Degradation" que deshabilita módulos IA ante fallos de red, garantizando continuidad operativa.
*   **RAG (Retrieval Augmented Generation):** Implementación de "Memoria Institucional" mediante ChromaDB para fundamentar las decisiones en protocolos locales.
*   **Stack Tecnológico:**
    *   **Backend/Frontend:** Python + Streamlit + FastAPI (Microservicios).
    *   **Persistencia:** MongoDB Atlas (NoSQL) y gestión de archivos/medios.
    *   **Resiliencia:** PWA Offline-First y Modo Manual asíncrono.

### 3. Metodología de Desarrollo
*   **Enfoque Ágil:** Ciclos iterativos (Fase 14 completada) con feedback continuo.
*   **Diseño Centrado en el Usuario:** Interfaces líquidas y adaptativas (Pediatría, Geriatría).
*   **Calidad del Software:**
    *   Pipeline de CI/CD con GitHub Actions.
    *   Testing exhaustivo: Unitario, E2E y Carga.
    *   **Auditoría IA:** Trazabilidad completa de prompts y respuestas para validación forense.

### 4. Resultados y Validación
*   **Funcionalidades Clave:**
    *   **Triaje Multimodal:** Voz (Audio Nativo), Texto y Contexto Clínico.
    *   **Relevo de Turno (Shift Handoff):** Generación automática de informes de cambio de guardia con IA.
    *   **Gestión de Salas:** Monitor Público para sala de espera (Anonimizado) y Orquestador de Flujos.
    *   **Identificación:** Generación de Tickets/Pulseras con QR para trazabilidad.
    *   **Segunda Opinión Experta:** Módulo "Reasoning ++" con análisis multimodal (Imágenes/Docs) y API-First.
    *   **Interface Líquida Dinámica (Parametrizada):** Motor de reglas No-Code que adapta la UI (alertas, campos, colores) según datos del paciente (Edad, Motivo, Vitales).
    *   **Ciclo de Mejora Continua:** Sistema integral de Feedback y Soporte (Admin/User) con trazabilidad y notificaciones para reporte de incidencias.
*   **Métricas del Piloto:**
    *   Capacidad validada para usuarios concurrentes con gestión de colas.
    *   Reducción estimada del 40% en tiempo de documentación.
    *   Estandarización de decisiones clínicas mediante RAG y Análisis Estructurado.

### 5. Conclusiones y Líneas Futuras
*   **Conclusión:** La plataforma demuestra que la IA Generativa, gobernada por reglas estrictas de contingencia y auditoría, transforma la eficiencia operativa en Urgencias.
*   **Roadmap (Próximos Pasos):**
    *   **Fase 11 y 18 (UX Avanzada):** Interfaz conversacional y "Liquid UI" parametrizada (Completado).
    *   **Fase 12 (API First):** Desacople total del backend mediante FastAPI para integración con Apps móviles y HIS de terceros.
    *   **Fase 13 (IoT):** Integración directa con monitores de constantes vitales.

---
**Autor:** [Tu Nombre]
**Máster:** [Nombre del Máster]
**Fecha:** Diciembre 2025
