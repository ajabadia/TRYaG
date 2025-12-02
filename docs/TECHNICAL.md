# Documentación Técnica - Asistente de Triaje IA

## 🛠️ Stack Tecnológico

*   **Lenguaje:** Python 3.11+
*   **Framework Web:** Streamlit
*   **Base de Datos:** MongoDB Atlas (NoSQL)
*   **IA Generativa:** Google Gemini (vía `google-generativeai`)
*   **Librerías Clave:**
    *   `pymongo`: Driver de MongoDB.
    *   `streamlit-cookies-manager`: Gestión de sesiones persistentes.
    *   `pandas`, `plotly`: Análisis y visualización de datos.
    *   `pydantic`: Validación de modelos de datos.

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una arquitectura modular basada en componentes y servicios, separando la lógica de negocio de la interfaz de usuario.

### Estructura de Directorios (`src/`)

*   **`app.py`**: Punto de entrada principal. Configura la página, inicializa el estado de sesión y enruta a las vistas principales.
*   **`core/`**: Lógica de negocio pura (Manejadores de datos, lógica de prompts).
*   **`services/`**: Integración con servicios externos (Gemini, MongoDB) y lógica de aplicación (Permisos, Flujos).
*   **`db/`**: Capa de acceso a datos (DAL).
    *   `connection.py`: Gestión de conexión a Mongo (Singleton).
    *   `repositories/`: Implementación del patrón Repository para cada entidad (Pacientes, Centros, Configuración).
*   **`ui/`**: Componentes de interfaz de usuario (Vistas, Paneles).
*   **`components/`**: Widgets reutilizables (Selectores, Tarjetas, Visores).
    *   `common/body_map.py`: Mapa corporal interactivo con Plotly.
    *   `analytics/concordance_analysis.py`: Módulo de validación científica (Pandas).
*   **`utils/`**: Funciones de utilidad (Iconos, PDFs, Imágenes).

### Patrones de Diseño

1.  **Repository Pattern:**
    *   El acceso a datos se abstrae en clases Repository (`src/db/repositories/`).
    *   Esto desacopla la lógica de negocio de la implementación específica de la base de datos.
    *   Ejemplo: `GeneralConfigRepository` maneja la configuración, ocultando si viene de JSON o Mongo.

2.  **Singleton:**
    *   Utilizado para la conexión a base de datos (`get_database()`) y configuración global, asegurando una única instancia.

3.  **Service Layer:**
    *   Los servicios (`src/services/`) orquestan operaciones complejas que involucran múltiples repositorios o llamadas a APIs externas.

### Integración con Google Gemini

La interacción con la IA se centraliza en `src/services/gemini_client.py`.
*   **Configuración:** Se carga la API Key desde `st.secrets` o variables de entorno.
*   **Modelos:** Se soportan múltiples modelos (Flash, Pro) configurables desde el panel de administración.
*   **Prompts:** Los prompts del sistema se almacenan en base de datos (`prompts` collection) y son editables en tiempo real sin redeploy.

### Persistencia y Estado

*   **Session State (`st.session_state`):** Maneja el estado efímero de la interfaz (navegación, datos de formularios temporales).
*   **Cookies:** Se usan para persistir la aceptación del disclaimer (`streamlit-cookies-manager`).
*   **MongoDB:** Almacenamiento persistente de toda la información crítica (Pacientes, Historial, Configuración).

## 🚀 Despliegue

Ver [DEPLOYMENT.md](../DEPLOYMENT.md) para instrucciones detalladas sobre el despliegue en Streamlit Community Cloud.

### Variables de Entorno Requeridas
*   `MONGODB_URI`: Connection string a Atlas.
*   `GOOGLE_API_KEY`: Clave de API de Google AI Studio.

## 🧪 Testing

El proyecto incluye una suite de pruebas automatizadas usando `pytest`.

### Configuración
1.  Instalar dependencias de prueba:
    ```bash
    pip install -r requirements-test.txt
    ```

### Ejecución
*   **Ejecutar todos los tests:**
    ```bash
    python -m pytest tests/ -v
    ```
*   **Ejecutar tests con cobertura:**
    ```bash
    python -m pytest tests/ -v --cov=src
    ```
