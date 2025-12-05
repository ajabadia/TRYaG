# Manual de Mantenimiento y Configuración

Este manual está dirigido a los administradores del sistema ("Superadmin" o "Gestor") y detalla cómo configurar y mantener la aplicación.

## 1. Configuración General del Centro

Acceda a **"⚙️ Configuración" > "🏥 Datos del Centro"**.

Aquí puede personalizar la identidad de la aplicación:
*   **Denominación:** Nombre del hospital o centro médico (aparece en la cabecera).
*   **Mensaje de Cabecera:** Texto informativo o avisos (ej. "Mantenimiento programado a las 22:00").
*   **Logo:** Ruta al archivo de imagen del logotipo corporativo.

### 1.1 Configuración de Equipo (Hardware)
En la sección **"🖥️ Configuración Equipo"** puede seleccionar los dispositivos predeterminados para este puesto de trabajo:
*   **Cámara:** Seleccione la webcam a usar para fotos y video.
*   **Micrófono:** Seleccione el dispositivo de entrada de audio.
*   **Calidad de Video:** Ajuste la resolución (Baja/Media/Alta) según el ancho de banda disponible.

---

## 2. Gestión de Salas (Infraestructura)

El sistema debe reflejar la realidad física de su servicio de urgencias.

Acceda a **"⚙️ Configuración" > "🏥 Datos del Centro" > "Gestión de Salas"**.

### 2.1 Crear una Sala
1.  Pulse el botón **"➕ Nueva Sala"**.
2.  **Nombre:** Identificador visible (ej. "Box 1", "Espera Traumatología").
3.  **Tipo:** Función principal de la sala.
    *   `admision`: Mostradores de entrada.
    *   `triaje`: Boxes de enfermería.
    *   `box`: Consultas médicas.
    *   `consulta_ingreso`: Área de observación/ingreso.
4.  **Subtipo:**
    *   `espera`: Sala donde los pacientes aguardan (Cola).
    *   `atencion`: Sala donde los pacientes son atendidos (Ocupación 1 a 1).
5.  Pulse **"Guardar Sala"**.

### 2.2 Editar/Borrar
Use los iconos de lápiz (editar) o papelera (borrar) junto a cada sala en la lista.
> **Importante:** No borre salas que tengan pacientes asignados actualmente.

---

## 3. Gestión de Usuarios y Personal

El sistema distingue entre **Personas** (Ficha del empleado) y **Usuarios** (Credenciales de acceso).

### 3.1 Gestión de Personas (Staff)
Acceda a **"⚙️ Configuración" > "👥 Personas"**.
Aquí se da de alta al personal del centro.
1.  **Crear Persona:** Introduzca Nombre, Apellidos, DNI, Categoría Profesional y Nº Colegiado.
2.  **Identificaciones:** Puede añadir múltiples documentos (DNI, Pasaporte).
3.  **Contacto:** Teléfonos y emails.

### 3.2 Gestión de Usuarios (Credenciales)
Acceda a **"⚙️ Configuración" > "🔐 Usuarios"**.
## 4. Gestión de Inteligencia Artificial

El comportamiento de la IA se puede ajustar sin tocar código. Acceda a **"⚙️ Configuración" > "🧠 Inteligencia Artificial"**.

### 4.1 Base de Conocimiento (RAG)
Aquí puede subir documentos (PDF, TXT) que la IA usará como referencia.
1.  **Subir:** Arrastre el archivo al área de carga y pulse "Procesar e Indexar".
2.  **Listar:** Verá la lista de documentos activos.
3.  **Borrar:** Use el icono de papelera para eliminar documentos obsoletos.

### 4.2 Editor de Prompts
1.  Seleccione la pestaña **"Prompts"**.
2.  Seleccione el tipo de prompt a editar (ej. `triage_main`).
3.  Verá la versión **Activa** (solo lectura).
4.  Para hacer cambios, seleccione una versión **Borrador (Draft)** o clone la activa.
5.  **Probar:** Use el botón "Probar Prompt" antes de activar.
6.  **Activar:** Marque la versión como "Active" para producción.

---

## 5. Configuración Médica (Signos Vitales)

Acceda a **"⚙️ Configuración" > "🩺 Triaje (PTR)"**.

---

## 6. Gestión de Turnos y Personal

El sistema permite organizar al personal de dos formas:

### 6.1 Asignación Fija (Habitual)
Acceda a **"⚙️ Configuración" > "📍 Asignación Salas"**.
Use esta opción para definir dónde trabaja habitualmente cada persona.
1.  Despliegue la sala deseada (ej. "Triaje 1").
2.  Seleccione los usuarios en la lista "Personal Asignado".
3.  Pulse **"Guardar"**.

### 6.2 Planificación de Turnos (Calendario)
Acceda a **"⚙️ Configuración" > "📅 Turnos Avanzados"**.
Use esta opción para rotaciones, guardias o cambios puntuales.

*   **Crear Turno:** En la pestaña "Planificación", use el formulario "Crear Turno Rápido" para asignar un usuario a una sala en una fecha y hora específicas.
*   **Ver Conflictos:** La pestaña "⚠️ Conflictos" le avisará si ha programado a una persona en dos sitios a la vez.
*   **Recomendaciones IA:** El sistema puede sugerir la cobertura necesaria basándose en la predicción de demanda (ver Manual de Estadísticas > Predicciones ML).
*   **Exportar:** Puede descargar la planificación en Excel desde la pestaña "📤 Exportar".

---

## 7. Configuración de Notificaciones

Acceda a **"⚙️ Configuración" > "🔔 Notificaciones"**.

### 7.1 Canales
*   **Push Notifications:** Active el interruptor para habilitar notificaciones en el navegador. Requiere permiso del usuario.
*   **Email (SMTP):** Configure el servidor de correo saliente (Host, Puerto, Usuario, Password).
*   **Webhooks:** Configure URLs de Slack/Teams para recibir alertas en canales de chat.

### 7.2 Pruebas
Use el botón "Enviar Notificación de Prueba" para verificar que los canales funcionan correctamente.
