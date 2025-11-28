# Asistente de Triaje IA - Piloto Traumatología

![Status](https://img.shields.io/badge/Status-Piloto-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)

## 📋 Descripción
Este proyecto es un **Asistente de Triaje Inteligente** diseñado para optimizar el flujo de pacientes en servicios de urgencias de Traumatología. Utiliza Inteligencia Artificial Generativa (Google Gemini) para analizar síntomas, transcribir dictados médicos y sugerir niveles de prioridad, sirviendo como herramienta de apoyo a la decisión clínica.

> **⚠️ Aviso Legal:** Esta herramienta es un sistema de apoyo y **NO sustituye el juicio clínico** de un profesional sanitario cualificado.

## 📚 Documentación

La documentación del proyecto está organizada en las siguientes secciones:

*   **[📖 Documentación Funcional](FUNCTIONAL.md):** Descripción detallada de roles, flujos de trabajo (Admisión, Triaje, Atención) y características del sistema. Ideal para entender *qué* hace la aplicación.
*   **[🛠️ Documentación Técnica](TECHNICAL.md):** Arquitectura del software, stack tecnológico, estructura de carpetas y detalles de implementación. Ideal para desarrolladores.
*   **[🚀 Guía de Despliegue](../DEPLOYMENT.md):** Instrucciones paso a paso para desplegar la aplicación en Streamlit Community Cloud.

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

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar entorno:**
    Crea un archivo `.env` en la raíz (o `.streamlit/secrets.toml`) con tus claves:
    ```toml
    MONGODB_URI="mongodb+srv://..."
    GOOGLE_API_KEY="AIza..."
    ```

4.  **Ejecutar:**
    ```bash
    streamlit run src/app.py
    ```

## 🤝 Contribución
Consulta las **[Directivas de Codificación](coding_guidelines.md)** antes de realizar cambios en el código.

---
*Desarrollado como Piloto de Innovación en Salud Digital.*