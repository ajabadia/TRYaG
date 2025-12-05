# Manual de Datos y Estadísticas

Este manual describe en profundidad las herramientas de análisis, auditoría y control de calidad disponibles en el **Panel de Auditoría**.

Acceda a la pestaña **"📊 Auditoría"** desde el menú principal.

---

## 1. Estructura del Panel

El panel se organiza en cuatro grandes secciones (pestañas superiores):

1.  **📉 Datos en Bruto:** Acceso directo a los registros de la base de datos (Logs).
2.  **📈 Análisis Gráfico:** Cuadros de mando visuales e indicadores de rendimiento (KPIs).
3.  **🧠 Predicciones IA:** Panel de control de los modelos de Machine Learning.
4.  **🛠️ Debug MongoDB:** Herramientas técnicas para inspección de datos.

---

## 2. 📉 Datos en Bruto (Logs)

Esta sección permite consultar el historial completo de eventos del sistema. Para facilitar la navegación, los datos se han organizado en **Categorías**:

### 🏥 Actividad Clínica
*   **🏥 Triaje:** Histórico de episodios de triaje (borradores y finalizados).
*   **👤 Pacientes:** Tabla maestra de pacientes registrados.
*   **🌊 Flujo Pacientes:** Registro de movimientos y estados de los pacientes.
*   **🎙️ Transcripciones:** Log de audios procesados y su conversión a texto.
*   **📂 Archivos:** Historial de documentos e imágenes subidos.

### 👥 Gestión & Usuarios
*   **🔐 Usuarios:** Tabla maestra de usuarios del sistema.
*   **🔑 Accesos (Login):** Historial de inicios de sesión, cierres y bloqueos.
*   **👥 Personal:** Tabla maestra de personal (Staff).
*   **📅 Turnos:** Registro de asignaciones de turnos.

### 🤖 Inteligencia Artificial
*   **🤖 AI Audit:** Registro detallado de interacciones con la IA (prompts/respuestas).
*   **🧠 AI Models:** Registro de modelos de IA utilizados.
*   **🧪 Tests Prompts:** Resultados de tests de prompts.
*   **📜 Versiones Prompts:** Historial de cambios en los prompts.
*   **🐛 Feedback:** Reportes de errores y sugerencias de usuarios.

### ⚙️ Sistema
*   **📋 Auditoría General:** Log cronológico de acciones del sistema.
*   **🔔 Notificaciones:** Historial de alertas enviadas.

### Funcionalidades de la Tabla
*   **Filtros:** Use los encabezados de columna para filtrar por texto, fecha o valor.
*   **Exportar:** Botón para descargar la vista actual en formato CSV/Excel.
*   **Detalle:** Al hacer clic en una fila, se despliega una vista JSON con todos los campos técnicos.

---

## 3. 📈 Análisis Gráfico (Módulos)

Esta sección ofrece visualizaciones avanzadas organizadas por categorías:

### ⚙️ General & Evolución
*   **🎯 Resumen General (KPIs):** Indicadores clave (Total Triajes, Tiempo Medio, Nivel Promedio).
*   **📈 Evolución Temporal:** Gráficos de línea mostrando la tendencia de actividad diaria/semanal.

### 🏥 Actividad Clínica
*   **🏥 Análisis de Triaje:** Distribución por niveles (1-5) y especialidades. Tabla interactiva de casos.
*   **🧪 Validación Científica:** Matriz de confusión IA vs Humano, métricas de Sobre/Sub-triaje.
*   **📂 Análisis de Archivos:** Estadísticas de uso de adjuntos (imágenes, PDFs).
*   **🎙️ Análisis de Transcripciones:** Métricas sobre el uso del dictado por voz.
*   **🔗 Análisis Relacional:** Relación entre tipos de adjuntos y decisiones clínicas.

### 🤖 Inteligencia Artificial
*   **📜 Análisis de Prompts:** Historial y rendimiento de las distintas versiones de instrucciones.
*   **🐛 Análisis de Feedback:** Resumen de valoraciones y reportes de los usuarios.

---

## 4. 🧠 Predicciones IA (Machine Learning)

Panel de control para los modelos predictivos (**Random Forest**).

### 4.1 Módulos Predictivos
*   **📊 Demanda:** Predicción de afluencia de pacientes por hora. Ayuda a anticipar picos de trabajo.
*   **⏱️ Tiempos de Espera:** Estimación inteligente del tiempo de espera real, basada en la cola actual y la velocidad histórica de resolución.
*   **👥 Staffing:** Recomendación automática de personal (médicos/enfermeros) necesario para cubrir la demanda prevista en cada turno.
*   **🔍 Anomalías:** Sistema de alerta temprana que detecta si la actividad actual se desvía de lo normal (ej. afluencia masiva inesperada).

### 4.2 Gestión de Modelos
*   **Estado:** Indica si los modelos están cargados y activos.
*   **Re-entrenar:** Botón para actualizar los modelos con los datos más recientes de la base de datos.

---

## 5. 🛠️ Debug MongoDB

Herramienta técnica para administradores y desarrolladores.
Permite inspeccionar directamente las colecciones de la base de datos, ver índices y analizar la estructura de los documentos JSON sin necesidad de herramientas externas.
