# Sistema de Triaje IA

Sistema avanzado de gestión de urgencias y triaje asistido por Inteligencia Artificial (Google Gemini).

## 🚀 Características
*   **Triaje Inteligente**: Análisis de síntomas y constantes vitales con IA.
*   **Gestión de Pacientes**: Admisión, seguimiento y control de flujos.
*   **Asignación de Personal**: Gestión de turnos y asignación automática.
*   **Notificaciones Multicanal**: Alertas en tiempo real vía App, Email y Webhooks.
*   **Auditoría Completa**: Registro detallado de acciones y decisiones de la IA.

## 🛠️ Requisitos
*   Python 3.11+
*   MongoDB Atlas
*   Google AI Studio API Key

## 📦 Instalación

1.  **Clonar el repositorio**
2.  **Crear entorno virtual**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```
3.  **Instalar dependencias**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configurar variables de entorno**
    Crear un archivo `.env` con:
    ```
    MONGODB_URI=mongodb+srv://...
    GOOGLE_API_KEY=AIza...
    ```

## ▶️ Ejecución
```bash
streamlit run src/app.py
```

## 🧪 Testing

El proyecto incluye una suite de pruebas automatizadas usando `pytest`.

### Configuración de Tests
1.  Instalar dependencias de prueba:
    ```bash
    pip install -r requirements-test.txt
    ```

### Ejecución de Tests
*   **Ejecutar todos los tests:**
    ```bash
    python -m pytest tests/ -v
    ```
*   **Ejecutar tests con reporte de cobertura:**
    ```bash
    python -m pytest tests/ -v --cov=src
    ```
