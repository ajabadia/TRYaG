# Documentación Técnica - Asistente de Triaje IA

## 🛠️ Stack Tecnológico

*   **Lenguaje:** Python 3.11+
*   **Framework Web:** Streamlit
*   **Base de Datos:** MongoDB Atlas (NoSQL)
*   **IA Generativa:** Google Gemini (vía `google-generativeai`)
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
*   **`assets/`**: Recursos estáticos del proyecto.
    *   `icons/`: Iconos SVG del sistema.
    *   `logos/`: Logotipos de la aplicación y centros.
*   **`scripts/`**: Scripts de mantenimiento y utilidades (Health Checks, Seeds).
*   **`templates/`**: Plantillas HTML y de texto.
    *   `email_templates.py`: Templates Jinja2-like para emails transaccionales.
*   **`static/`**: Recursos estáticos servidos directamente (Manifest, Service Worker).

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

### Memoria Institucional (RAG)

El sistema implementa **RAG (Retrieval Augmented Generation)** para fundamentar las respuestas de la IA en documentación local.
*   **Motor Vectorial:** Se utiliza **ChromaDB** en modo persistente local (`data/chroma_db`) para almacenar los embeddings de los documentos.
*   **Ingestión:**
    *   Los documentos (PDF, TXT) se procesan en `rag_service.py`.
    *   Se utiliza `RecursiveCharacterTextSplitter` para dividir el texto en fragmentos (chunks) de ~1000 caracteres con solapamiento.
    *   Se generan embeddings (vectores) usando el modelo por defecto de Chroma (`all-MiniLM-L6-v2`) que corre localmente en CPU.
*   **Recuperación (Retrieval):**
    *   Antes de llamar a Gemini, `triage_service.py` consulta ChromaDB con el motivo de consulta.
    *   Se recuperan los 3 fragmentos más relevantes y se inyectan en el prompt bajo la sección `[MEMORIA INSTITUCIONAL]`.
*   **Pre-Triaje Aumentado (Risk Analysis):**
    *   En el panel de análisis de riesgos (`risk_analysis_panel.py`), se utiliza RAG en modo "solo recuperación" para el botón "Verificar riesgos sin IA".
    *   Se buscan protocolos coincidentes con los síntomas y se muestran como alertas, sin invocar al LLM.

### Persistencia y Estado

*   **Session State (`st.session_state`):** Maneja el estado efímero de la interfaz (navegación, datos de formularios temporales).
*   **Cookies:** Se usan para persistir la aceptación del disclaimer (`streamlit-cookies-manager`).
*   **MongoDB:** Almacenamiento persistente de toda la información crítica (Pacientes, Historial, Configuración).
*   **Borradores (`triage_draft`):** Colección específica para el auto-guardado de sesiones de triaje en curso.

### Autenticación (Simulada)

Para el entorno de piloto, se ha implementado un flujo de autenticación simplificado pero funcional en `src/ui/login_view.py`.

*   **Intercepción:** `app.py` verifica la existencia de `st.session_state.current_user` al inicio. Si no existe, renderiza `login_view` y detiene la ejecución (`st.stop()`).
*   **Validación:** Se valida la entrada del usuario contra el campo `internal_id` del documento de usuario en MongoDB.
*   **Seguridad:** Aunque simplificada, la sesión se gestiona en el servidor (`session_state`) y no se exponen credenciales reales. El disclaimer se fuerza en cada login.

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

El sistema implementa dos estrategias de resiliencia:

1.  **Modo Manual (Soft Fallback):**
    *   Permite operar sin el servicio de IA (Gemini).
    *   Los datos se persisten directamente en MongoDB (requiere conexión al servidor).
    *   Gestionado por `contingency_service.py` (flag de estado) y `input_form.py`.

2.  **Modo Offline Total (Hard Fallback / PWA):**
    *   Permite operar sin conexión al servidor Streamlit.
    *   **Manifest (`static/manifest.json`):** Habilita instalación como app nativa.
    *   **Service Worker (`static/sw.js`):** Cachea `offline.html` y sirve esta página cuando falla la red.
    *   **Estrategia Híbrida:**
        *   *Stale-While-Revalidate* para activos estáticos (iconos, CSS, JS) para carga instantánea.
        *   *Network First* para navegación y datos, con fallback a página offline.
    *   **Gestión de Caché:** Versionado automático (`tryag-v2`) y limpieza de cachés antiguas.
3.  **Installer (`pwa_installer.py`):** Componente Python que inyecta el registro del Service Worker y los tags `<link>` necesarios en el head de la aplicación.
4.  **Sincronización (`offline_sync.py`):**
    *   **Exportación (JS):** Lee `IndexedDB` y genera un blob JSON para descarga.
    *   **Importación (Python):** Procesa el JSON subido, valida la estructura y guarda los registros en MongoDB.
    *   **Auto-Detección:** Se utiliza el evento `window.addEventListener('online', ...)` en `offline_db.js` para detectar la recuperación de red y notificar al usuario.

### Etiquetas de Depuración (Debug Footers)
El sistema incluye etiquetas discretas en el pie de cada componente UI para facilitar la localización del código fuente.
*   **Implementación:** Se usa la clase CSS `.debug-footer` definida en `styles.css`.
*   **Visibilidad:** Por defecto están ocultas (`display: none`).
*   **Activación:** Cuando `st.session_state.developer_mode` es `True`, `app.py` inyecta un estilo global que anula la ocultación (`display: block`), haciéndolas visibles en toda la aplicación sin necesidad de lógica condicional en cada archivo.

### 4.5 Interoperabilidad (FHIR)
El sistema implementa un servicio de exportación compatible con HL7 FHIR R4.
- **Servicio:** `src/services/fhir_service.py`
- **Recursos Soportados:**
    - `Patient`: Datos demográficos.
    - `Encounter`: Datos del episodio de triaje.
    - `Observation`: Signos vitales codificados con LOINC.

## 📚 Bibliografía y Referencias
El desarrollo de este sistema se basa en estándares internacionales y guías clínicas reconocidas:

*   **HL7 FHIR:** Health Level Seven International. (2019). *HL7 FHIR Release 4*. Recuperado de http://hl7.org/fhir/R4/
*   **CIE-10:** Organización Mundial de la Salud. (2019). *Clasificación Internacional de Enfermedades, 10.ª revisión*. Recuperado de https://icd.who.int/browse10/2019/en
*   **LOINC:** Regenstrief Institute. (2024). *Logical Observation Identifiers Names and Codes*. Recuperado de https://loinc.org/

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
    pip install -r requirements.txt
    playwright install
    ```

### Ejecución de Pruebas

**1. Pruebas Unitarias:**
Validan la lógica interna de los servicios y repositorios.
```bash
pytest tests/unit
```

**2. Pruebas E2E (End-to-End):**
Validan el flujo completo del usuario en un navegador real. Requieren que la aplicación esté corriendo.
```bash
# Terminal 1: Iniciar App
streamlit run src/app.py

# Terminal 2: Ejecutar Tests
pytest tests/e2e
```

**3. Pruebas de Carga:**
Simulan múltiples usuarios concurrentes para verificar el rendimiento.
```bash
locust -f tests/load/locustfile.py --host http://localhost:8501
```

## 8. Arquitectura API REST (FastAPI)

En la Fase 12 se introdujo un microservicio paralelo para exponer la lógica de negocio mediante API REST.

*   **Framework:** FastAPI + Uvicorn.
*   **Puerto:** 8000 (Internal Docker Network & Host mapped).
*   **Estructura:**
    *   `src/api/main.py`: Punto de entrada y configuración CORS.
    *   `src/api/routers/`: División lógica de endpoints (`triage.py`, `ai.py`).
*   **Schema:** Uso de Pydantic para validación estricta de Request/Response.
*   **Seguridad:** Preparado para API Key Header (Placeholder).

### Endpoints (v1)

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `POST` | `/v1/core/analyze` | Análisis de triaje completo (Wrapper de TriageService). |
| `POST` | `/v1/core/predict/risk` | Cálculo de PTR (Wrapper de PredictiveService). |
| `POST` | `/v1/ai/rag/search` | Búsqueda semántica en ChromaDB. |

## 9. CI/CD Pipeline
El proyecto utiliza **GitHub Actions** para la integración continua.

### Workflow: `tests.yml`
Se ejecuta en cada `push` y `pull_request` a las ramas principales.
1.  **Setup:** Python 3.11, instalación de dependencias.
2.  **Unit Tests:** Ejecución de pruebas unitarias con `pytest`.
3.  **E2E Tests:** Ejecución de pruebas de navegador con `playwright`.

### Ejecución Local
Para replicar el pipeline localmente:
```bash
# Instalar dependencias
pip install -r requirements.txt
playwright install

# Ejecutar tests
pytest tests/
```
