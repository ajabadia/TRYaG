# Fundamentos de Inteligencia Artificial en el Proyecto
## Guía No Técnica de Estrategia y Decisiones Tecnológicas

Este documento explica **qué** hace la Inteligencia Artificial (IA) en nuestra aplicación, **por qué** hemos elegido tecnologías específicas para cada tarea y **qué alternativas** existen en el mercado.

---

### Visión General: El "Cerebro Híbrido"

Nuestra aplicación no utiliza "una sola IA" para todo. Al igual que un hospital tiene especialistas (médicos, enfermeros, administrativos), nuestro sistema utiliza diferentes tipos de inteligencia según la tarea necesaria. 

Utilizamos un enfoque **híbrido** que combina la creatividad y comprensión humana de la **IA Generativa** con la precisión matemática de los **Algoritmos Clásicos**.

---

### 1. El "Médico Asistente" (Triaje Clínico)
**Tecnología:** IA Generativa (Google Gemini 1.5 Flash).

*   **¿Qué hace?** Lee lo que le pasa al paciente ("me duele el pecho y el brazo izquierdo"), entiende el contexto, y sugiere una gravedad y especialidad.
*   **¿Por qué IA Generativa?** 
    *   La medicina es ambigua. Los pacientes no hablan en códigos médicos. La IA Generativa es excelente entendiendo lenguaje natural ("me falta el aire" = Disnea) y matices que un sistema rígido no captaría.
*   **¿Por qué este modelo (Gemini Flash)?**
    *   **Ventaja:** Es extremadamente rápido (baja latencia) y económico. En urgencias, la velocidad es crítica. Tiene una ventana de contexto grande (memoria a corto plazo) para leer muchos antecedentes.
*   **Alternativas:**
    *   **GPT-4 (OpenAI):** Es más "listo" pero mucho más caro y lento. Para triaje, Flash es suficiente y más ágil.
    *   **Modelos Locales (Llama 3):** Ofrecen privacidad total (no salen datos del hospital), pero requieren ordenadores muy potentes (GPUs caras) en cada centro.

### 2. El "Oído Clínico" (Transcripción de Voz)
**Tecnología:** IA Multimodal (Google Gemini Audio).

*   **¿Qué hace?** Escucha al médico o paciente y convierte el audio en texto médico estructurado.
*   **¿Por qué IA Multimodal?**
    *   No es un simple dictado como el del móvil. Esta IA "entiende" la conversación. Si el médico dice "paracetamol de un gramo", la IA sabe que es una dosis y un fármaco y lo coloca en su casilla correspondiente.
*   **¿Por qué este modelo?**
    *   **Ventaja:** Procesa audio nativo directamente, sin pasos intermedios, reduciendo errores de traducción fonética.
*   **Alternativas:**
    *   **Whisper (OpenAI):** Es el estándar de oro en transcripción local. Es una alternativa muy sólida que podríamos implementar si la privacidad de voz fuera absoluta prioridad, aunque requiere más hardware.

### 3. El "Matemático" (Cálculo de Riesgo y Alertas)
**Tecnología:** Algoritmos Deterministas y Machine Learning (Random Forest).

*   **¿Qué hace?** Calcula puntuaciones de riesgo (PTR, NEWS2) basándose **exclusivamente** en números (Tensión, Fiebre, Saturación).
*   **¿Por qué NO usar IA Generativa aquí?**
    *   **Seguridad:** Las IAs generativas pueden "alucinar" (inventarse cosas). Con los números de los signos vitales no podemos jugar. 2 + 2 debe ser siempre 4.
    *   **Ventaja:** Los algoritmos clásicos son 100% predecibles, auditables y nunca fallan en una suma.
*   **Alternativas:**
    *   **Redes Neuronales Profundas:** Serían "cajas negras" (no sabemos por qué deciden algo). En medicina, necesitamos saber el "por qué" (explicabilidad), por lo que las reglas claras son mejores.

### 4. La "Memoria del Hospital" (RAG - Búsqueda Semántica)
**Tecnología:** Búsqueda Vectorial Local (ChromaDB).

*   **¿Qué hace?** Antes de que la IA responda, el sistema busca en los PDFs de protocolos del hospital la respuesta correcta y se la "chiva" a la IA.
*   **¿Por qué IA Local (Búsqueda)?**
    *   **Control:** Queremos que la IA siga **nuestros** protocolos, no lo que leyó en internet en 2023.
    *   **Privacidad:** Nuestros documentos internos no se suben a ninguna nube pública para ser entrenados.
*   **Alternativas:**
    *   **Fine-Tuning (Re-entrenar la IA):** Enseñar a la IA nuestros manuales. Es muy caro y si cambia un protocolo mañana, hay que volver a entrenar. El RAG es instantáneo (cambias el PDF y listo).

### 5. El "Secretario" (Relevo de Turno)
**Tecnología:** IA Generativa (Resumen y Síntesis).

*   **¿Qué hace?** Lee los 50 casos del turno anterior y escribe un resumen narrativo de 1 página.
*   **¿Por qué IA Generativa?**
    *   Es la única tecnología capaz de sintetizar ("leer y resumir") de forma coherente, detectando patrones ("hoy han venido muchos casos de gripe") en lugar de solo contar números.
*   **Ventaja:** Ahorra horas de lectura al jefe de guardia entrante.

---

### Resumen de Decisiones

| Tarea | Tipo de IA | Modelo Elegido | ¿Por qué? |
| :--- | :--- | :--- | :--- |
| **Entender al Paciente** | Generativa | **Gemini Flash** | Rápido, barato, entiende contexto. |
| **Signos Vitales** | Reglas (No-IA) | **Código Python** | 100% fiable, sin errores matemáticos. |
| **Protocolos** | Búsqueda Semántica | **ChromaDB (Local)** | Privacidad y fidelidad a normas internas. |
| **Voz** | Multimodal | **Gemini** | Entiende términos médicos al escuchar. |

### Conclusión

Hemos priorizado la **seguridad del paciente** y la **velocidad**. Usamos la IA creativa para entender a las personas y la IA lógica para las matemáticas y los protocolos. Esta combinación nos da lo mejor de los dos mundos: **Empatía Artificial y Precisión Matemática.**
