# Documentación Técnica - Asistente de Triaje IA

## 🛠️ Stack Tecnológico

*   **Lenguaje:** Python 3.11+
*   **Framework Web:** Streamlit
*   **Base de Datos:** MongoDB Atlas (NoSQL)
*   **IA Generativa:** Google Gemini (vía `google-generativeai`)
*   **PWA:** Service Workers, Web Manifest (Offline Support)
*   **Librerías Clave:**
    *   `pymongo`: Driver de MongoDB.
    *   `streamlit-cookies-manager`: Gestión de sesiones persistentes.
    *   `pandas`, `plotly`: Análisis y visualización de datos.
    *   `pydantic`: Validación de modelos de datos.
    *   `reportlab`: Generación de PDFs.

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una arquitectura modular basada en componentes y servicios, separando la lógica de negocio de la interfaz de usuario.

### Estructura de Directorios (`src/`)

*   **`app.py`**: Punto de entrada principal. Configura la página, inicializa el estado de sesión y enruta a las vistas principales.
*   **`core/`**: Lógica de negocio pura (Manejadores de datos, lógica de prompts).
*   **`services/`**: Integración con servicios externos (Gemini, MongoDB) y lógica de aplicación (Permisos, Flujos).
    *   `report_service.py`: Generación de informes PDF.
    *   `multi_center_service.py`: Agregación de datos multi-centro.
    *   `notification_service.py`: Bus de notificaciones (SMTP, Webhooks).
    *   `training_service.py`: Lógica del modo formación (Casos y Evaluación).
*   **`db/`**: Capa de acceso a datos (DAL).
    *   `connection.py`: Gestión de conexión a Mongo (Singleton).
    *   `repositories/`: Implementación del patrón Repository para cada entidad (Pacientes, Centros, Configuración).
*   **`ui/`**: Componentes de interfaz de usuario (Vistas, Paneles).
*   **`components/`**: Widgets reutilizables (Selectores, Tarjetas, Visores).
    *   `common/pwa_installer.py`: Inyección de scripts PWA.
    *   `common/body_map.py`: Mapa corporal interactivo con Plotly.
    *   `analytics/concordance_analysis.py`: Módulo de validación científica (Pandas).
*   **`utils/`**: Funciones de utilidad (Iconos, PDFs, Imágenes).
*   **`templates/`**: Plantillas HTML y de texto.
    *   `email_templates.py`: Templates Jinja2-like para emails transaccionales.
*   **`static/`**: Recursos estáticos servidos directamente (Manifest, Service Worker, Iconos).

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
*   **Borradores (`triage_draft`):** Colección específica para el auto-guardado de sesiones de triaje en curso.

### Sistema de Notificaciones

El sistema utiliza una arquitectura de bus de eventos desacoplada para gestionar las notificaciones:

1.  **Core Service (`notification_service.py`):**
    *   Recibe solicitudes de notificación con prioridad y categoría.
    *   Resuelve los destinatarios (IDs de usuario -> Emails).
    *   Determina los canales de envío basándose en la prioridad (Lógica de negocio).

2.  **Canales:**
    *   **In-App:** Escritura directa en la colección `notifications` de MongoDB.
    *   **SMTP:** Envío síncrono de emails usando `smtplib` y templates HTML.
    *   **Webhooks:** Envío HTTP POST a endpoints externos (Slack/Teams) con payloads adaptativos.

3.  **Gestión de Errores:**
    *   El fallo en un canal secundario (ej. Email) no bloquea el flujo principal ni impide el registro en In-App.
    *   Estado de envío granular (`sent_status`) para auditoría de fallos.

### Modo Formación (Training Mode)

El sistema implementa un entorno de simulación aislado para entrenamiento:

1.  **Datos de Entrenamiento (`training_data.py`):**
    *   Módulo Python que contiene la biblioteca de casos clínicos predefinidos (JSON-like structure).
    *   Incluye datos demográficos simulados, signos vitales, síntomas y el "Gold Standard" (Nivel y Destino correctos).

2.  **Servicio de Evaluación (`training_service.py`):**
    *   **Carga de Casos:** Provee los casos al selector de pacientes cuando `is_training=True`.
    *   **Lógica de Evaluación:** Compara la decisión del usuario con el Gold Standard.
    *   **Scoring:** Calcula una puntuación (0-100) basada en la precisión del nivel (70%) y el destino (30%).

3.  **Aislamiento:**
    *   La UI intercepta el flujo normal en `step_patient_selection` y `step_final_disposition`.
    *   Los registros se marcan como `is_training=True` para ser excluidos de analytics.

### Progressive Web App (PWA)

El sistema implementa capacidades PWA mediante la inyección de scripts en el frontend de Streamlit:

1.  **Manifest (`static/manifest.json`):** Define metadatos, iconos y comportamiento de instalación (standalone).
2.  **Service Worker (`static/sw.js`):** Intercepta peticiones de red para ofrecer una estrategia de caché (Network First) y servir una página offline personalizada.
3.  **Installer (`pwa_installer.py`):** Componente Python que inyecta el registro del Service Worker y los tags `<link>` necesarios en el head de la aplicación.

## 🚀 Despliegue

Ver [DEPLOYMENT.md](../DEPLOYMENT.md) para instrucciones detalladas sobre el despliegue en Streamlit Community Cloud.

### Despliegue con Docker

El proyecto está completamente "dockerizado" para facilitar su despliegue en cualquier entorno.

*   **Dockerfile:** Define la imagen base (Python 3.11-slim), instala dependencias y copia el código fuente.
*   **docker-compose.yml:** Orquesta el contenedor de la aplicación (`web`) junto con una instancia local de MongoDB (`mongo`), ideal para desarrollo o entornos aislados.

Para levantar el entorno completo:
```bash
docker-compose up --build
```

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
