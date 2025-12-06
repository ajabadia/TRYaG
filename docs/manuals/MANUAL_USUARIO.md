# Manual de Usuario - Asistente de Triaje IA

Este manual describe el funcionamiento operativo de la aplicación para los distintos perfiles de usuario: Administrativos, Enfermería y Médicos.

## 1. Acceso al Sistema

### 1.1 Pantalla de Login
Al acceder a la aplicación, se mostrará la pantalla de selección de usuario.

1.  **Seleccionar Usuario:** Haga clic en la tarjeta con su nombre y rol.
2.  **Contraseña:** Introduzca su **ID de Empleado** (ej. `EMP-001`).
3.  **Aviso Legal:** Marque la casilla "He leído y acepto..." para confirmar que entiende que esta es una herramienta de apoyo y no sustituye el juicio clínico.
4.  **Entrar:** Pulse el botón "Entrar al Sistema".

> **Seguridad:** El sistema cuenta con protección contra intentos fallidos.
> *   Tras **5 intentos fallidos**, el usuario se bloqueará temporalmente.
> *   El tiempo de bloqueo aumenta exponencialmente (30 min, 1 hora, 2 horas...) con cada reincidencia.
> *   Contacte con un administrador si necesita desbloqueo inmediato.

> **Nota:** Si necesita cambiar de usuario durante la sesión, abra el menú lateral (izquierda) y pulse "Cambiar Usuario / Salir".

### 1.2 Buscador de Protocolos
En la barra lateral izquierda, encontrará el botón **"🔍 Protocolos"**.
*   **Uso:** Púlselo en cualquier momento para buscar guías clínicas o normativas sin salir de su pantalla actual.
*   **Descargas:** Puede ver el texto relevante o descargar el PDF original.

---

## 2. Módulo de Admisión
**Perfil:** Administrativo / Admisión

Su función principal es registrar la llegada de pacientes y colocarlos en la cola de triaje.

### 2.1 Buscar Paciente
1.  Acceda a la pestaña **"📋 Admisión"**.
2.  Utilice la barra de búsqueda para encontrar al paciente por **DNI, Nombre o Apellidos**.
3.  Si el paciente existe, aparecerá en la lista. Pulse **"Seleccionar"** para abrir su ficha.

### 2.2 Registrar Nuevo Paciente
Si el paciente no existe:
1.  Pulse el botón **"Nuevo Paciente"** en la barra lateral o tras una búsqueda sin resultados.
2.  Rellene el formulario con los datos obligatorios (Nombre, Apellidos, DNI/Pasaporte, Fecha Nacimiento).
3.  Pulse **"Guardar y Admitir"**.

### 2.3 Confirmar Admisión
Una vez seleccionado el paciente:
1.  Verifique sus datos.
2.  Pulse el botón **"Registrar Llegada (Enviar a Triaje)"**.
3.  El paciente pasará al estado `EN_ESPERA_TRIAJE` y aparecerá en la cola de enfermería.

---

## 3. Módulo de Triaje
El sistema ha incorporado funciones avanzadas de asistencia (Fase 11) para agilizar el triaje:

#### 3.5.1 Triaje Conversacional (Chat)
Al iniciar el triaje, puede elegir entre **"Estándar"** (Formulario clásico) o **"Conversacional"** (Chat con IA).
*   **Funcionamiento:** Hable con el asistente como si fuera un compañero. Responda a sus preguntas sobre los síntomas.
*   **Autocompletado:** El sistema extraerá automáticamente la información clave.
    *   *Ejemplo:* Si escribe "Tiene dificultad para respirar y fiebre de 39", el sistema rellenará por usted el campo de "Motivo de Consulta" y marcará la temperatura si es posible.
> **Nota de Seguridad:** Toda la conversación queda grabada en la ficha del paciente ("Transcript") para futuras auditorías o revisiones médicas.

#### 3.5.2 Interfaz Contextual (Liquid UI)
La pantalla se adapta a lo que usted escribe para ahorrar tiempo.
*   **Modo Pediatría:** Si la edad es < 14 años, los rangos normales de constantes cambian y aparecerán avisos específicos.
*   **Modo Geriátrico:** Si la edad > 65 años, verá recordatorios sobre riesgo de caídas y delirium.
*   **Detector de Síntomas (Ej. Disnea):** Si menciona palabras clave como *"ahogo"*, *"disnea"* o *"falta de aire"*:
    1.  Los campos de **Saturación O2** y **Frecuencia Respiratoria** se iluminarán con un rayo (⚡) y color rosa.
    2.  El sistema le invitará visualmente a priorizar esa toma antes de seguir.

#### 3.5.3 Copiloto Proactivo
Mientras usted trabaja, el sistema "escucha" y busca en la base de conocimientos.
*   **Alerta Inteligente:** Si detecta un patrón grave (ej. "Dolor torácico irradiado"), le mostrará una notificación flotante (Toast) sugiriendo un protocolo específico (ej. "Protocolo SCA Activado").
*   **Sin Interrupciones:** Estas alertas son sutiles y no bloquean su trabajo.

### 3.6 Validación y Destino (Paso 3)
Revise la propuesta de la IA:
1.  **Nivel de Triaje:** Verifique el nivel sugerido (1-5). Puede modificarlo si no está de acuerdo.
2.  **Especialidad:** Confirme la especialidad (Traumatología, Medicina General).
3.  **Destino:** Seleccione la sala de espera o box donde debe ir el paciente.
4.  Pulse **"Finalizar y Derivar"** para guardar el triaje e imprimir el informe.

---

## 4. Modos Especiales

### 4.1 Modo Formación (Entrenamiento)
Diseñado para practicar con casos clínicos simulados sin afectar a pacientes reales.

1.  **Activar:** En el menú lateral izquierdo, active el interruptor **"🎓 Modo Formación"**.
2.  **Selección de Caso:** La lista de espera mostrará casos predefinidos (ej. "Dolor Torácico", "Esguince").
3.  **Realización:** Realice el triaje normalmente. Los datos del paciente se rellenarán automáticamente.
4.  **Evaluación:** Al finalizar, el sistema comparará su decisión con la respuesta correcta ("Gold Standard") y le dará una puntuación y feedback inmediato.

> **Nota:** Los registros de formación NO se guardan en las estadísticas oficiales.

---

## 5. Módulo de Atención (Box)
**Perfil:** Médico

Gestión de la consulta médica y resolución del caso.

### 4.1 Llamada a Paciente
1.  Acceda a la pestaña **"🏥 Atención Box"** (o "Consulta").
2.  Verá la lista de pacientes **"Pendientes de Atención"** (ya triados).
3.  Seleccione un paciente y pulse **"Llamar a Consulta"**. Esto cambiará su estado a `EN_ATENCION` y lo asignará a su box.

### 4.2 Acto Médico
En la pantalla de atención podrá ver:
*   **Resumen de Triaje:** Motivo, vitales, nivel de urgencia y notas de enfermería.
*   **Archivos:** Acceso a fotos, videos o informes adjuntados en triaje.
*   **Historial:** Consultas previas del paciente.

### 4.3 Finalización
Al terminar la consulta:
1.  Seleccione el destino de alta (Domicilio, Ingreso, Traslado).
2.  Pulse **"Finalizar Asistencia"**. El paciente saldrá de las listas activas.

---

## 5. Sala de Espera (Pantalla Pública)
**Uso:** Monitor de TV en sala de espera.

Acceda a la pestaña **"🪑 Sala de Espera"**. Esta vista está diseñada para mostrarse en pantallas públicas y permite a los pacientes saber su estado mediante códigos anonimizados (ej. `PAC-8392`).

---

## 6. Notificaciones
El sistema puede enviarle alertas importantes (ej. "Sala Inexistente", "Paciente Crítico") incluso si no está mirando la pantalla.

*   **Campana (In-App):** Icono en la esquina superior derecha.
*   **Push (Navegador):** Si las activa, recibirá avisos emergentes en su escritorio o móvil.
*   **Email:** Para alertas de alta prioridad (si está configurado).
