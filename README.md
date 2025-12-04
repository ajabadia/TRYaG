# Asistente de Triaje IA - Piloto Traumatología

![Status](https://img.shields.io/badge/Status-Piloto-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)

## 📋 Descripción

Este proyecto es un **Asistente de Triaje Inteligente** diseñado para optimizar el flujo de pacientes en servicios de urgencias de Traumatología. Utiliza **Inteligencia Artificial Generativa (Google Gemini)** y **Machine Learning (Scikit-learn)** para analizar síntomas, transcribir dictados médicos, predecir la demanda asistencial y sugerir niveles de prioridad, sirviendo como herramienta de apoyo a la decisión clínica.

> **⚠️ Aviso Legal:** Esta herramienta es un sistema de apoyo y **NO sustituye el juicio clínico** de un profesional sanitario cualificado.

## ✨ Características Principales

### 🏥 Gestión Clínica
*   **Triaje Estructurado:** Clasificación basada en signos vitales y síntomas con algoritmo de "peor caso" y escala Manchester/SET.
*   **Entrevista Guiada:** Asistente inteligente para la toma de datos (anamnesis) estructurada.
*   **Mapa Corporal Interactivo:** Selección visual de zonas de dolor.
*   **Gestión de Pacientes:** Flujo completo desde Admisión -> Triaje -> Sala de Espera -> Atención (Box) -> Alta.

### 🧠 Inteligencia Artificial
*   **Análisis Multimodal:** Procesa texto, audio (transcripción en tiempo real) e imágenes de lesiones.
*   **Alertas Predictivas:** Detección temprana de riesgos (Sepsis, Caídas, Violencia) mediante análisis de patrones con Gemini.
*   **Machine Learning Real:** Modelos **Random Forest** para predecir:
    *   Demanda de pacientes por hora.
    *   Tiempos de espera estimados.
    *   Recomendaciones de personal (Staffing).

### ⚙️ Operativa y Gestión
*   **Orquestador de Salas:** Gestión visual de ubicaciones y movimiento de pacientes (Drag & Drop).
*   **Gestión de Turnos:** Planificación de personal y detección de conflictos.
*   **Auditoría Completa:** Registro detallado de acciones, validación científica y análisis de concordancia IA-Humano.
*   **Modos Avanzados:**
    *   *Modo Formación:* Simulación con casos clínicos para entrenamiento.
    *   *Modo Contingencia:* Operativa offline ante fallos de red.

## 📚 Documentación

La documentación del proyecto está organizada en las siguientes secciones:

*   **[📖 Documentación Funcional](docs/FUNCTIONAL.md):** Descripción detallada de roles, flujos de trabajo, módulos de IA y anexos clínicos.
*   **[🛠️ Documentación Técnica](docs/TECHNICAL.md):** Arquitectura del software, stack tecnológico, estructura de carpetas y detalles de implementación.
*   **[🚀 Guía de Despliegue](DEPLOYMENT.md):** Instrucciones para desplegar la aplicación en producción.
*   **[🗺️ Roadmap](ROADMAP.md):** Plan de desarrollo y estado de las tareas.

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
