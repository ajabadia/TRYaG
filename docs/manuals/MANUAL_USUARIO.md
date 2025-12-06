
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
*   **Funcionamiento:** Interactúe con un asistente tipo chat. Puede escribir o **usar su voz**.
*   **Entrada de Voz Nativa:** Pulse el icono de micrófono 🎙️ en la barra de chat para dictar. El sistema transcribirá automáticamente su voz usando IA avanzada (Gemini).
*   **Autocompletado Inteligente (Nuevo):** El sistema extraerá automáticamente la información clave (Síntomas, Vitales, Antecedentes) del texto dictado y rellenará el formulario estructurado por usted.
    *   *Ejemplo:* "Paciente varón de 45 años, refiere dolor opresivo en pecho desde hace 30 minutos y sudoración profusa. TA 140/90, Saturación 98%". -> Rellena Motivo, Sexo, Edad, Vitales y alerta de Dolor Torácico.
> **Nota de Seguridad:** Toda la conversación y las transcripciones quedan registradas ("Audit Log") para garantía clínica.

#### 3.5.2 Entrada de Voz en Formulario Estándar
Incluso en el modo "Estándar", dispone de un asistente de voz:
*   Busque el área **"🎙️ Entrada de Voz"** al inicio del formulario.
*   Grabe un resumen rápido del caso.
*   El texto se añadirá inteligentemente a los campos correspondientes (Motivo, Historia, etc.) sin borrar lo que ya haya escrito manualmente.

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

---

## 7. Integración Técnica (API)

El sistema dispone de una **API REST** ("Apificación") que permite la integración con otros sistemas del hospital (HIS, App Móvil).
Aunque esta funcionalidad es transparente para el usuario final, permite que:

1.  Se puedan enviar triajes desde una App de paciente.
2.  Los resultados se vuelquen automáticamente en la Historia Clínica.
3.  Se puedan realizar auditorías externas.

> Para más detalles técnicos, consulte el **Manual de Mantenimiento**.
