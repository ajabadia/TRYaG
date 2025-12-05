# Manual de Mantenimiento y Configuración

Este manual está dirigido a los administradores del sistema ("Superadmin" o "Gestor") y detalla cómo configurar y mantener la aplicación.

## 1. Configuración General del Centro

Acceda a **"⚙️ Configuración" > "🏥 Datos del Centro"**.

Aquí puede personalizar la identidad de la aplicación:
*   **Denominación:** Nombre del hospital o centro médico (aparece en la cabecera).
*   **Mensaje de Cabecera:** Texto informativo o avisos (ej. "Mantenimiento programado a las 22:00").
*   **Logo:** Ruta al archivo de imagen del logotipo corporativo.

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

## 3. Gestión de Usuarios

Acceda a **"⚙️ Configuración" > "👥 Usuarios"**.

### 3.1 Alta de Usuario
1.  Rellene el formulario "Nuevo Usuario".
2.  **Username:** Identificador único para el sistema.
3.  **Nombre/Apellidos:** Nombre real del profesional.
4.  **ID Interno:** Código usado como **contraseña** en el login simulado (ej. `EMP-123`).
5.  **Rol:** Determina los permisos (Ver tabla de roles en Documentación Funcional).
6.  Pulse **"Crear Usuario"**.

---

## 4. Gestión de la IA (Prompts)

El comportamiento de la Inteligencia Artificial se puede ajustar sin tocar código.

Acceda a **"⚙️ Configuración" > "🧠 Configuración IA"**.

### 4.1 Editor de Prompts
1.  Seleccione el tipo de prompt a editar (ej. `triage_main` para el análisis principal).
2.  Verá la versión **Activa** (solo lectura).
3.  Para hacer cambios, seleccione una versión **Borrador (Draft)** o clone la activa.
4.  Edite las instrucciones en el área de texto. Puede modificar:
    *   Rol del sistema ("Actúa como...").
    *   Reglas de decisión.
    *   Formato de salida JSON.
5.  **Probar:** Use el botón "Probar Prompt" para ver cómo responde con un caso de ejemplo antes de activarlo.
6.  **Activar:** Si está satisfecho, marque la versión como "Active" para que empiece a usarse en producción.

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
