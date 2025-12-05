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

Esta sección permite consultar el historial completo de eventos del sistema. Está dividida en múltiples pestañas temáticas para facilitar la búsqueda.

### Colecciones Disponibles
*   **📋 Auditoría General:** Registro cronológico de todas las acciones importantes (inicios de sesión, validaciones, errores).
*   **📂 Archivos:** Historial de documentos e imágenes subidos por los usuarios.
*   **🎙️ Transcripciones:** Log de audios procesados y su conversión a texto.
*   **🐛 Feedback:** Reportes de errores y sugerencias enviados por los usuarios.
*   **🤖 AI Audit:** Registro detallado de cada interacción con la IA (prompt enviado y respuesta recibida).
*   **🏥 Triaje:** Histórico de episodios de triaje (borradores y finalizados).
*   **📅 Turnos:** Registro de asignaciones de personal y turnos.
*   **👤 Pacientes / Personal / Usuarios:** Tablas maestras de identidades.
*   **🔔 Notificaciones:** Historial de alertas enviadas.

### Funcionalidades de la Tabla
*   **Filtros:** Use los encabezados de columna para filtrar por texto, fecha o valor.
*   **Exportar:** Botón para descargar la vista actual en formato CSV/Excel.
*   **Detalle:** Al hacer clic en una fila, se despliega una vista JSON con todos los campos técnicos del registro.

---

## 3. 📈 Análisis Gráfico (Módulos)

Esta sección ofrece visualizaciones avanzadas para la toma de decisiones.

### 3.1 🎯 Resumen General (KPIs)
Indicadores clave de rendimiento del servicio:
*   **Total Triajes:** Volumen de pacientes atendidos en el periodo.
*   **Tiempo Medio:** Duración promedio del proceso de triaje.
*   **Nivel Promedio:** Gravedad media de los casos.

### 3.2 🏥 Análisis de Triaje
Desglose detallado de la actividad clínica:
*   **Distribución por Niveles:** Gráfico de barras (Nivel 1 a 5).
*   **Distribución por Especialidad:** Gráfico de sectores (Trauma vs General).
*   **Tabla Interactiva:** Listado de triajes con posibilidad de seleccionar para ver el detalle clínico completo (motivo, vitales, decisión).

### 3.3 🧪 Validación Científica (Concordancia)
Herramienta para evaluar la calidad de la IA comparándola con el humano ("Gold Standard").
*   **Matriz de Confusión:** Gráfico que cruza la propuesta de la IA con la decisión final del médico.
    *   *Diagonal:* Aciertos.
    *   *Fuera de diagonal:* Discrepancias.
*   **Métricas de Riesgo:**
    *   *Sobre-Triaje:* IA asigna mayor gravedad (Ineficiencia).
    *   *Sub-Triaje:* IA asigna menor gravedad (Riesgo clínico).

### 3.4 📜 Análisis de Prompts
Gestión de la ingeniería de instrucciones de la IA.
*   **Listado:** Muestra todas las versiones de prompts creadas.
*   **Detalle:** Permite ver el texto exacto de las instrucciones enviadas al modelo.

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
