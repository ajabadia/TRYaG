# Plan de Implementación: Funcionalidades Avanzadas de Triaje (Grado Hospitalario)

Este documento detalla la hoja de ruta para elevar la demo de triaje a un nivel avanzado, incorporando simulación de interoperabilidad, contextualización clínica, lógica de IA ponderada y métricas de calidad.

## 1. 🌍 Simulación de Interoperabilidad (HL7/FHIR)

**Objetivo:** Demostrar que el sistema puede integrarse con la Historia Clínica Electrónica (HCE) del hospital utilizando estándares internacionales.

### Funcionalidad
- **Botón de Acción:** En el Paso 2 (Resultados), añadir un botón `[Enviar Registro y Cerrar Atención]`.
- **Simulación:** Al hacer clic, mostrar un modal que simula el envío de un mensaje FHIR.

### Detalles Técnicos
- **Payload FHIR Simulado:**
```json
{
  "resourceType": "Encounter",
  "subject": { "reference": "Patient/[ID_Paciente]" },
  "priority": { 
    "coding": [ 
      { "code": "[Color_Final_IA]", "display": "Triaje [Color_Final_IA]" } 
    ] 
  },
  "serviceType": "Urgencias - Triaje",
  "period": { "start": "[Fecha_Hora_Registro]" },
  "status": "finished"
}
```
- **Feedback:** Mostrar mensaje de éxito: "✅ Éxito. Registro de Triaje [ID] enviado y confirmado por el HCE."

---

## 2. 👵 Adaptación de Rangos por Condición/Edad (Contextualización Clínica)

**Objetivo:** Adaptar la lógica de triaje a poblaciones vulnerables donde los signos vitales normales pueden ser engañosos.

### Funcionalidad
- **Nuevos Inputs (Paso 1):**
    - `[ ] Criterio Geriátrico (Edad >= 65)` (Auto-marcado si la edad coincide).
    - `[ ] Paciente Inmunodeprimido / Oncológico`.

### Lógica de Negocio (Prompt IA)
El sistema inyectará instrucciones específicas al modelo Gemini si estos flags están activos:
- **Geriátrico:** "Considerar taquicardia leve (>100) como riesgo moderado/alto. Umbrales de dolor más bajos."
- **Inmunodeprimido:** "Fiebre (>38.0°C) es EMERGENCIA (Nivel 2/Naranja) inmediata. Ignorar ponderación estándar de temperatura."

---

## 3. 🧠 Lógica de Ponderación de Variables (Motor Gemini)

**Objetivo:** Sustituir la lógica simple de "peor caso" por un sistema de puntuación ponderada (PTR) similar al *Manchester Triage System* o *MEWS*. ✅ **IMPLEMENTADO (Paralelo a NEWS2)**

### Sistema de Puntuación
La IA calculará el **PTR (Puntuación Total de Riesgo)** basándose en la suma de:
`Gravedad del Signo (0-3) x Multiplicador de Importancia`

#### Tabla de Multiplicadores
| Métrica | Multiplicador | Justificación |
| :--- | :---: | :--- |
| **GCS (Conciencia)** | **x4** | Alto riesgo neurológico/vía aérea. |
| **SpO2 (Saturación)** | **x3** | Alto riesgo fallo respiratorio. |
| **PAS/PAD (Tensión)** | **x3** | Alto riesgo de shock. |
| **FR (Respiración)** | **x2** | Dificultad respiratoria. |
| **FC, Temp, Dolor** | **x1** | Factores sistémicos/subjetivos. |

#### Ajustes por Contexto
- **Si Geriátrico:** FC pasa a multiplicador **x2**.
- **Si Inmunodeprimido:** Temperatura pasa a multiplicador **x3**.

#### Mapeo PTR a Color
| PTR (Puntuación Total) | Nivel de Triaje |
| :--- | :--- |
| **> 15** | 🔴 Nivel I/II (Rojo/Naranja) |
| **8 - 15** | 🟠 Nivel II/III (Naranja/Amarillo) |
| **3 - 7** | 🟡 Nivel III/IV (Amarillo/Verde) |
| **0 - 2** | 🟢 Nivel IV/V (Verde/Azul) |

---

## 4. 📊 Simulación de Métricas de Calidad (Auditoría)

**Objetivo:** Medir la calidad del triaje comparando la clasificación inicial con el resultado final del paciente.

### Cambios en Datos
- Nuevo campo en BD (Patient/Triage): `outcome` (Resultado de Atención).
    - Valores: `Alta Rápida`, `Ingreso Planta`, `Ingreso UCI`, `Fallecimiento`.

### Panel de Supervisión (KPIs)
Implementar pestaña "Calidad" en el Panel de Auditoría con las siguientes métricas:

#### 1. Sobre-Triaje (Over-Triage)
- **Definición:** Pacientes clasificados **Graves (Rojo/Naranja)** que tuvieron **Alta Rápida**.
- **Fórmula:** `(Rojo_Alta + Naranja_Alta) / Total_Rojo_Naranja`
- **Objetivo:** 10-15% (Es aceptable cierto margen por seguridad).

#### 2. Sub-Triaje (Under-Triage)
- **Definición:** Pacientes clasificados **Leves (Verde/Amarillo)** que acabaron en **UCI o Fallecieron**.
- **Fórmula:** `(Verde_UCI + Amarillo_UCI + Verde_Exitus + Amarillo_Exitus) / Total_Verde_Amarillo`
- **Objetivo:** < 1% (Error crítico de seguridad).

---

## Hoja de Ruta de Implementación

### Fase 1: Frontend & Interoperabilidad
1.  Modificar `input_form.py` para añadir checkboxes de contexto.
2.  Modificar `results_display.py` para añadir botón y modal FHIR.

### Fase 2: Backend & IA
1.  Actualizar `triage_service.py` para recibir y procesar los flags de contexto.
2.  Reescribir el System Prompt de Gemini (`triage_prompt`) para implementar la lógica PTR y las tablas de ponderación.

### Fase 3: Datos & Auditoría
1.  Añadir campo `outcome` al modelo de datos.
2.  Crear interfaz para registrar el `outcome` (ej. al "dar de alta" al paciente o en una vista de seguimiento).
3.  Implementar cálculos y gráficos en `audit_panel`.

---

## 5. 📴 Modo de Contingencia y Desconexión (Offline)

**Objetivo:** Garantizar la continuidad operativa ante fallos de red o servidor, demostrando robustez.

### Funcionalidad
- **Simulación de Fallo:** Botón `[SIMULAR FALLA DE RED]` en el panel de Supervisor.
- **Indicador Visual:** Banner persistente "MODO CONTINGENCIA ACTIVO - Funcionalidad Reducida".

### Lógica de Funcionamiento Reducido
- **IA Deshabilitada:** Se desactiva el cálculo de PTR y alertas predictivas.
- **Fallback a "Peor Caso":** El sistema utiliza la lógica básica de gravedad máxima de signos vitales (Rojo > Naranja > Amarillo > Verde) sin ponderación compleja.
- **Almacenamiento Local:** Los registros se guardan en una caché local (simulada en `st.session_state` o archivo temporal) con flag `sincronizado=False`.

### Sincronización
- Al desactivar el modo fallo, aparece botón `[SINCRONIZAR DATOS]`.
- Los registros offline se envían a la BD central con la etiqueta "Modo Contingencia" para auditoría.

---

## 6. 🎓 Módulo de Formación y Prueba de Competencia

**Objetivo:** Formar y auditar la competencia del personal en la lógica de triaje.

### Funcionalidad
- **Botón:** `[Prueba de Competencia]` en el menú principal.
- **Flujo:**
    1.  El sistema presenta un "Caso Ficticio" (ej. "FC 130, T 39.5, GCS 15").
    2.  El usuario selecciona la clasificación que cree correcta.
    3.  **Feedback Inmediato:**
        - **Acierto:** "¡Correcto! PTR: 16 (Taquicardia x1 + Fiebre x1...)."
        - **Fallo:** "Incorrecto. Ideal: Rojo. Motivo: PTR > 15 por..."

### Estructura de Datos (Simulada o Real)
- **Casos de Prueba:** Definiciones de escenarios con su "Clasificación Ideal" y "Justificación".
- **Resultados:** Registro de intentos (Usuario, Caso, Acierto/Fallo) para estadísticas de equipo.

---

## Actualización de Hoja de Ruta

### Fase 4: Robustez y Formación
1.  **Modo Contingencia:**
    - Implementar flag global `offline_mode`.
    - Crear lógica de fallback en `triage_logic.py` (bypass Gemini).
    - Implementar mecanismo de "Sync" simulado.
2.  **Módulo de Formación:**
    - Crear vista `training_view.py`.
    - Definir banco de casos JSON.
    - Implementar lógica de evaluación y feedback.

---

## 7. 📋 Historia Clínica Integral (Ingreso Exhaustivo)

**Objetivo:** Recopilar información crítica para seguridad del paciente y diagnóstico preciso, más allá del motivo de consulta inmediato.

### 9. Antecedentes Familiares (Hereditarios)
- **Cardiovasculares:** IAM/Ictus en familiares < 55 años.
- **Oncológicos:** Tipo y edad de diagnóstico.
- **Crónicos:** Diabetes, Hipertensión.
- **Genéticos:** Trastornos de coagulación, enfermedades hereditarias.

### 10. Psiquiátricos y Salud Mental
- **Diagnósticos:** Depresión, Ansiedad, Bipolaridad, Esquizofrenia.
- **Medicación:** Interacciones potenciales (ej. con antibióticos/analgésicos).
- **Riesgo de Seguridad:** Historial de intentos de suicidio o autolesión (Alerta de Seguridad).

### 11. Estado Nutricional y Dieta
- **Dieta:** Vegetariana, Vegana, Kosher, Hiposódica.
- **Riesgo Desnutrición:** Pérdida de peso no intencionada (3-6 meses).
- **Disfagia:** Dificultad para tragar (Impacto en administración de medicación).

### 12. Historial de Viajes y Exposición
- **Viajes:** Zonas tropicales/rurales (Malaria, Dengue).
- **Exposición:** Animales, agua no potable, enfermos.
- **Ocupacional:** Químicos, granjas, sanitario.

### 13. Déficits Sensoriales y Ayudas
- **Sensorial:** Hipoacusia, Visión (Uso de audífonos/gafas).
- **Comunicación:** Idioma, necesidad de intérprete.
- **Prótesis:** Dentales, extremidades (Seguridad en anestesia).

### 14. Historial de Dolor
- **Crónico:** Fibromialgia, Lumbalgia (Percepción alterada).
- **Opioides:** Uso crónico/tolerancia (Ajuste de dosis analgésica).

### 15. Historial de Hospitalizaciones Recientes
- **Ingresos:** Últimos 3-6 meses (Patrones de enfermedad).
- **Complicaciones:** Infecciones nosocomiales, reingresos.
- **Urgencias:** Visitas repetidas (Mal control/Diagnóstico incierto).

### 16. Estatus Legal y Representación
- **Legal:** Tutor/Poder Notarial (Demencia, Menores).
- **Cuidador:** Persona de contacto principal.

### 17. Protocolo y Documentación Forense
- **Trauma:** Circunstancias exactas, discrepancias relato/lesión.
- **Abuso:** Sospecha de abuso físico/sexual/financiero (Protocolo Seguridad).
- **Cadena de Custodia:** Preservación de evidencia (Ropa, heridas).

### 18. Aspectos Culturales y Espirituales
- **Religión:** Objeciones a tratamientos (ej. Transfusiones).
- **Cultural:** Preferencias de género en cuidadores, higiene.

### 19. Herramientas de Evaluación Específicas
- **Dolor (EVA/NRS):** Escala 0-10 (Ya integrado en Signos Vitales).
- **Úlceras (Braden):** Riesgo de úlceras por presión (Prevención).
- **Delirium (CAM):** Evaluación de estado mental en ancianos.

### Implementación Propuesta
- **Nuevo Componente UI:** `ExtendedHistoryForm` (Plegable o Paso Adicional).
- **Integración IA:** Inyectar alertas de seguridad (ej. "Riesgo Suicidio", "Disfagia", "Tolerancia Opioides", "Reingreso Frecuente", "Riesgo Forense", "Objeción Transfusión") en el prompt de triaje y enfermería.

---

## 8. ⚡ Evaluación Clínica Inmediata (Triaje)

**Objetivo:** Determinar la urgencia vital y monitorizar el estado fisiológico al instante.

### 1. Signos Vitales y Dolor
- **Completos:** Temp, FC, PA, FR, SpO2.
- **Oxígeno:** Necesidad de suplementación.
- **Dolor:** Escala EVA/NRS (0-10).

### 2. Estado Neurológico y Agudeza
- **GCS:** Escala de Coma de Glasgow (Conciencia).
- **Hidratación:** Piel, mucosas, orientación (Alerta Deshidratación/Shock).

### 3. Escalas de Riesgo
- **Triaje:** Nivel de urgencia (Manchester/SET).
- **Deterioro:** NEWS/MEWS (Puntuación de Alerta Temprana).

### Implementación Propuesta
- **Mejora de UI (Signos Vitales):** Añadir campos para "Oxígeno Suplementario" y "Estado Hidratación".
- **Cálculo Automático:** Implementar calculadora NEWS/MEWS en tiempo real basada en los signos vitales ingresados.

---

## 9. 🩹 Evaluación de Enfermería y Examen Físico

**Objetivo:** Documentar el estado físico, riesgos específicos y seguridad del paciente al ingreso.

### 4. Evaluación Integumentaria y Piel
- **Integridad:** Heridas, cortes, magulladuras (Ubicación/Tamaño).
- **Úlceras:** Presión (Sacro, talones) - Preexistente vs Adquirida.
- **Edema:** Fóvea, localización.
- **Aspecto:** Color (Pálido/Cianótico), Temperatura, Sudoración.

### 5. Evaluación Específica de Riesgos
- **Caídas:** Escala Morse/Hendrich (Historial, Sedantes, Deambulación).
- **Aspiración:** Disfagia, Sonda, Neurológico.

### 6. Inventario y Seguridad
- **Pertenencias:** Inventario de valor (Custodia).
- **Identificación:** Pulsera colocada (2 identificadores).
- **Soporte Vital:** Equipos propios (Oxígeno, Bombas).

### Implementación Propuesta
- **Nuevo Formulario:** `NursingAssessmentForm`.
- **Body Map:** Herramienta visual para marcar heridas/úlceras.
- **Checklists:** Inventario y Seguridad.

---

## 10. 🧐 Historia de la Enfermedad Actual (HDA) y Administrativos

**Objetivo:** Estructurar el motivo de consulta y registrar datos logísticos clave.

### 7. Historia de la Enfermedad Actual (HDA)
- **ALICIA:** Aparición, Localización, Intensidad, Características, Irradiación, Alivio.
- **Cronología:** Inicio, evolución.
- **Acompañantes:** Fiebre, náuseas, etc.
- **Tratamiento previo:** Medicación tomada en casa (ej. antipiréticos).

### 8. Datos Administrativos y Logística
- **Fuente:** Fiabilidad (Paciente, Familiar, Ambulancia).
- **Referencia:** Médico/Centro que deriva.
- **Seguro:** Situación de aseguramiento.

### Implementación Propuesta
- **HDA Estructurada:** Campos específicos para ALICIA (opcionalmente guiados por IA).
- **Metadatos:** Dropdowns para Fuente y Referencia en la cabecera del ingreso.

---

## 11. ➡️ Órdenes de Ingreso y Disposición Inicial

**Objetivo:** Definir el destino del paciente y las primeras acciones terapéuticas.

### 9. Destino y Nivel de Cuidado
- **Disposición:** Alta, Observación, Ingreso (Planta/UCI), Traslado.
- **Avisos:** Médico Guardia, Especialistas (Cirugía, Neuro), Trabajo Social.

### 10. Órdenes Médicas Inmediatas (Primer Set)
- **Dieta:** Absoluta (NPO), Blanda, Diabética.
- **Vía Venosa:** Canalización periférica.
- **Farmacología:** Analgesia, Antipiréticos (según EVA/Temp).
- **Pruebas:** Laboratorio (Sangre/Orina), Radiología (Rx/CT).

### Implementación Propuesta
- **Panel de Acción:** Botones rápidos para "Solicitar Analítica", "Dieta NPO", "Avisar Guardia".
- **Generador de Órdenes:** Checklists predefinidos según motivo de consulta (ej. Dolor Torácico -> ECG + Troponinas).
- **Integración IA:** Sugerencia de órdenes basada en el triaje (ej. "Sugerir ECG por Dolor Torácico").

---

## 12. ✨ Planificación Integral para el Alta (Discharge Planning)

**Objetivo:** Anticipar necesidades al alta desde el momento del ingreso.

### 10. Planificación de Alta
- **Cuidados Post-Agudos:** Rehabilitación, Enfermería domicilio, Paliativos.
- **Barreras Domiciliarias:** Escaleras, vive solo (Riesgo Social).
- **Equipamiento:** Oxígeno, Cama articulada, Andador (Solicitud anticipada).

## 13. 🔄 Hoja de Ruta Consolidada (Optimización)

Para una implementación más eficiente y lógica, agruparemos las funcionalidades en 4 grandes bloques de desarrollo:

### Fase 3: Núcleo de Admisión y Evaluación Inmediata (Core Triage)
*Combina HDA (Fase 8) y Evaluación Inmediata (Fase 6)*
- **Objetivo:** Capturar lo esencial para el triaje en una sola vista.
- **Componentes:**
    - **HDA:** ALICIA, Cronología.
    - **Signos Vitales:** NEWS/MEWS, Oxígeno, Hidratación.
    - **Administrativos:** Fuente, Referencia.

### Fase 4: Historia Clínica Integral (Extended Data)
*Corresponde a la Fase 5 original*
- **Objetivo:** Profundizar en antecedentes sin saturar la vista principal.
- **Componentes:** `ExtendedHistoryForm` (Plegable/Modal).
    - Antecedentes (Familiares, Psiquiatría, Nutrición, Viajes, Sensorial, Dolor, Legal, Forense, Cultural).

### Fase 5: Evaluación de Enfermería (Nursing)
*Corresponde a la Fase 7 original*
- **Objetivo:** Evaluación objetiva y física.
- **Componentes:** `NursingForm`.
    - Piel (Body Map), Riesgos (Caídas/Aspiración), Seguridad/Pertenencias.

### Fase 6: Resolución y Planificación (Outcome)
*Combina Disposición (Fase 9) y Alta (Fase 10)*
- **Objetivo:** Cerrar el ciclo de atención.
- **Componentes:** `DispositionForm`.
    - Destino, Órdenes Iniciales, Planificación de Alta (Barreras/Necesidades).

### Fase 7: Métricas y Robustez (Support)
*Fases originales 3 y 4*
- **Objetivo:** Calidad y Continuidad.
- **Componentes:** Métricas de Calidad, Modo Contingencia, Formación.
