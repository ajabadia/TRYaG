# Defensa de Trabajo Fin de Máster (TFM)
## Asistente de Triaje Inteligente con IA Generativa y RAG

### 1. Introducción y Contexto
*   **Título del Proyecto:** Desarrollo de un Asistente de Triaje Clínico basado en IA Generativa.
*   **Problemática:** Saturación de los servicios de urgencias, variabilidad en la clasificación de pacientes y fatiga cognitiva del personal sanitario.
*   **Objetivo:** Desarrollar una herramienta de apoyo a la decisión clínica (CDSS) que optimice el flujo de triaje, reduzca tiempos de espera y estandarice la aplicación de protocolos.

### 2. Marco Teórico y Tecnológico
*   **Arquitectura Híbrida:** Combinación de IA Generativa (Google Gemini) para el razonamiento clínico y Algoritmos Deterministas (Random Forest) para la predicción operativa.
*   **RAG (Retrieval Augmented Generation):** Implementación de "Memoria Institucional" mediante ChromaDB para fundamentar las decisiones en protocolos locales, mitigando alucinaciones.
*   **Stack Tecnológico:**
    *   **Backend/Frontend:** Python + Streamlit (Prototipado rápido y despliegue ágil).
    *   **Persistencia:** MongoDB Atlas (NoSQL) para flexibilidad de esquemas clínicos.
    *   **Resiliencia:** Arquitectura PWA (Progressive Web App) con estrategias Offline-First.

### 3. Metodología de Desarrollo
*   **Enfoque Ágil:** Ciclos iterativos de desarrollo con feedback continuo de profesionales sanitarios.
*   **Diseño Centrado en el Usuario:** Interfaces intuitivas adaptadas a entornos de alta presión (Urgencias).
*   **Calidad del Software:**
    *   Pipeline de CI/CD con GitHub Actions.
    *   Testing exhaustivo: Unitario (Pytest), E2E (Playwright) y Carga (Locust).

### 4. Resultados y Validación
*   **Funcionalidades Clave:**
    *   Triaje multimodal (Voz, Texto, Imagen).
    *   Detección automática de signos vitales y cálculo de riesgo (PTR).
    *   Gestión de flujo de pacientes y asignación de salas.
*   **Métricas del Piloto:**
    *   Capacidad de carga validada para 50 usuarios concurrentes.
    *   Reducción estimada del tiempo de documentación en un 40% (gracias a transcripción y autocompletado).
    *   Adherencia a protocolos garantizada mediante RAG.

### 5. Conclusiones y Líneas Futuras
*   **Conclusión:** La IA Generativa, controlada mediante RAG y reglas de negocio, es una herramienta viable y segura para el apoyo al triaje.
*   **Futuro:**
    *   Integración profunda con HIS (Health Information Systems) vía FHIR.
    *   Expansión a otras especialidades más allá de Traumatología.
    *   Implementación de modelos locales (SLMs) para privacidad total offline.

---
**Autor:** [Tu Nombre]
**Máster:** [Nombre del Máster]
**Fecha:** Diciembre 2025
