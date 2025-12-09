# Asistente de Triaje IA - Piloto Traumatología

![Status](https://img.shields.io/badge/Status-Producción-green)
![Version](https://img.shields.io/badge/Version-4.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![PWA](https://img.shields.io/badge/PWA-Offline%20Ready-purple)

## 📋 Descripción

12: 
13: Este proyecto es un **Asistente de Triaje Inteligente** diseñado para optimizar el flujo de pacientes en servicios de urgencias de Traumatología. Utiliza **Inteligencia Artificial Generativa de Última Generación (Google Gemini 2.5 Flash & 2.0 Pro)** y **Machine Learning (Scikit-learn)** para analizar síntomas, transcribir dictados médicos, predecir la demanda asistencial y sugerir niveles de prioridad, sirviendo como herramienta de apoyo a la decisión clínica.
14: 
15: > **⚠️ Aviso Legal:** Esta herramienta es un sistema de apoyo y **NO sustituye el juicio clínico** de un profesional sanitario cualificado.
16: 
17: ## ✨ Características Principales
18: 
19: ### 🏥 Gestión Clínica
20: *   **Triaje Estructurado:** Clasificación basada en signos vitales y síntomas con algoritmo de "peor caso" y escala Manchester/SET.
21: *   **Entrevista Guiada:** Asistente inteligente para la toma de datos (anamnesis) estructurada.
22: *   **Mapa Corporal Interactivo:** Selección visual de zonas de dolor.
23: *   **Gestión de Pacientes:** Flujo completo desde Admisión -> Triaje -> Sala de Espera -> Atención (Box) -> Alta.
24: 
25: ### 🧠 Inteligencia Artificial
26: *   **Análisis Multimodal:** Procesa texto, audio (transcripción en tiempo real) e imágenes de lesiones.
27: *   **Segunda Opinión Experta:** Módulo "Reasoning" con **Gemini 2.0 Pro** para casos complejos.
28: *   **Alertas Predictivas:** Detección temprana de riesgos (Sepsis, Caídas, Violencia) mediante análisis de patrones.
29: *   **Machine Learning Real:** Modelos **Random Forest** para predecir:
30:     *   Demanda de pacientes por hora.
31:     *   Tiempos de espera estimados.
32:     *   Recomendaciones de personal (Staffing).
33: 
34: ### ⚙️ Operativa y Gestión
35: *   **Orquestador de Salas:** Gestión visual de ubicaciones y movimiento de pacientes (Drag & Drop).
36: *   **Gestión de Turnos:** Planificación de personal y detección de conflictos.
37: *   **Auditoría Completa:** Registro detallado de acciones, validación científica y análisis de concordancia IA-Humano.
38: *   **Feedback Integral:** Sistema de gestión de incidencias y tickets para mejora continua.
39: *   **Modos Avanzados:**
40:     *   *Modo Formación:* Simulación con casos clínicos para entrenamiento.
41:     *   *Modo Contingencia:* Operativa offline ante fallos de red.
42: 
43: ### 📱 PWA & Offline-First
44: *   **Instalable:** Funciona como app nativa en iOS, Android y Desktop.
45: *   **Sincronización Automática:** Detecta recuperación de red y sube datos locales (`IndexedDB`).
46: *   **Video Nativo:** Grabación de evidencias sin dependencias externas.
47: 
48: ## 📚 Documentación
49: 
50: La documentación del proyecto está organizada en las siguientes secciones:
51: 
52: *   **[🤖 Fundamentos IA](docs/FUNDAMENTOS_IA.md):** (NUEVO) Explicación no técnica de la estrategia de Inteligencia Artificial (Triaje vs Segunda Opinión).
53: *   **[📖 Documentación Funcional](docs/FUNCTIONAL.md):** Descripción detallada de roles, flujos de trabajo, módulos de IA y anexos clínicos.
54: *   **[🛠️ Documentación Técnica](docs/TECHNICAL.md):** Arquitectura del software, stack tecnológico, estructura de carpetas y detalles de implementación.
55: *   **[🐳 Guía Docker](docs/DOCKER_GUIDE.md):** Instrucciones para desplegar la aplicación con contenedores.
56: *   **[🚀 Guía GitHub](docs/GITHUB_SETUP.md):** Pasos para el control de versiones.
57: *   **[📱 Guía PWA](docs/PWA_SETUP.md):** Configuración y uso de la Progressive Web App.
58: *   **[🗺️ Roadmap](ROADMAP.md):** Plan de desarrollo y estado de las tareas.

## 🚀 Inicio Rápido

### Prerrequisitos
*   Python 3.11 o superior.
*   Una cuenta de MongoDB Atlas (o base de datos local).
*   Una API Key de Google AI Studio.

### Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-repositorio>
    cd <nombre-carpeta>
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz con tus claves:
    ```toml
    MONGODB_URI="mongodb+srv://usuario:password@cluster.mongodb.net/..."
    GOOGLE_API_KEY="AIzaSy..."
    ```

5.  **Ejecutar la aplicación:**
    ```bash
    streamlit run src/app.py
    ```

### 🐳 Inicio Rápido con Docker

Si prefieres no instalar dependencias locales:

1.  **Asegúrate de tener Docker y Docker Compose instalados.**
2.  **Ejecuta:**
    ```bash
    docker-compose up --build
    ```
3.  Accede a la aplicación en `http://localhost:8501`.

## 🧪 Testing

El proyecto incluye una suite de pruebas automatizadas usando `pytest`.

1.  **Instalar dependencias de prueba:**
    ```bash
    pip install -r requirements-test.txt
    ```

2.  **Ejecutar tests:**
    ```bash
    python -m pytest tests/ -v
    ```

## 🤝 Contribución

Consulta las **[Directivas de Codificación](docs/coding_guidelines.md)** antes de realizar cambios en el código.

---
*Desarrollado como Piloto de Innovación en Salud Digital.*
