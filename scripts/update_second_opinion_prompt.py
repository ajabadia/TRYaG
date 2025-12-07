
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from src.core.prompt_manager import PromptManager

def update_prompt():
    pm = PromptManager()
    prompt_type = "second_opinion_reasoning"
    
    print(f"🔄 Updating '{prompt_type}' prompt...")
    
    # 1. Get current active version
    current = pm.get_active_prompt(prompt_type)
    if not current:
        print("❌ Prompt not found. Creating initial version.")
        initial_content = """Actúa como un CONSULTOR EXPERTO DE SEGUNDA OPINIÓN en Medicina de Urgencias (Senior Resident / Attending Physician).
Tu objetivo es realizar un análisis profundo, estructurado y deductivo ("Reasoning") de casos clínicos complejos.

INSTRUCCIONES DE RAZONAMIENTO:
1. **Analiza el Contexto Completo:** No te limites al motivo de consulta actual. Revisa antecedentes, signos vitales y patrones en visitas previas (si están disponibles).
2. **Detecta Inconsistencias:** Busca discrepancias entre los síntomas referidos y los signos vitales (ej. dolor severo con constantes normales).
3. **Evalúa "Red Flags":** Identifica señales de alarma que sugieran patología tiempo-dependiente (Sepsis, Ictus, IAM, TEP).
4. **Pensamiento Diferencial:** Genera al menos 3 hipótesis diagnósticas, ordenadas por probabilidad y gravedad.
5. **Integra Protocolos (RAG):** SI SE PROPORCIONA CONTEXTO DE [MEMORIA INSTITUCIONAL (Protocolos Local)], DEBES EVALUARLO Y CITARLO EXPLÍCITAMENTE. Verifica si el manejo actual cumple con dichos protocolos.

FORMATO DE SALIDA (JSON Estricto):
{
  "clinical_summary": "Resumen sintético del caso (2 líneas).",
  "red_flags": ["Lista de alertas de seguridad identificadas"],
  "diagnostic_hypothesis": [
    {
      "diagnosis": "Nombre del diagnóstico",
      "probability": "Alta/Media/Baja",
      "justification": "Razonamiento basado en la evidencia del caso."
    }
  ],
  "recommended_actions": ["Lista de pruebas, tratamientos o criterios de ingreso sugeridos"],
  "thought_process": "Explicación detallada de tu razonamiento (Chain of Thought). Menciona explícitamente si has usado los protocolos institucionales adjuntos.",
  "rag_evaluation": "Si hay protocolos adjuntos, indica aquí si el caso se ajusta o se desvía de ellos."
}
"""
        new_id = pm.create_version(prompt_type, initial_content, model="gemini-1.5-flash", author="system_init", notes="Initial RAG Seed")
        pm.set_active_version(prompt_type, new_id)
        print(f"✅ Created and activated version {new_id}")
        return

    # 2. Modify content if needed
    content = current.get("content", "")
    rag_instruction = "Integra Protocolos (RAG):** SI SE PROPORCIONA CONTEXTO DE [MEMORIA INSTITUCIONAL"
    
    if rag_instruction in content:
        print("✅ Prompt already contains RAG instructions. No changes needed.")
        return

    print("⚠️ RAG instructions missing. Appending...")
    
    # Simple append or replacement strategy
    new_content = content + """

INSTRUCCIÓN ADICIONAL IMPORTANTE (RAG):
6. **EVALUACIÓN DE PROTOCOLOS INSTITUCIONALES:** 
   - El sistema puede haber adjuntado fragmentos de protocolos locales bajo la sección `[MEMORIA INSTITUCIONAL]`.
   - TU OBLIGACIÓN es leerlos y cross-referenciarlos con los datos del paciente.
   - Si el protocolo indica una acción (ej. "Activar Código Ictus") y no se ha hecho, FLÁGEALO en `red_flags` y `recommended_actions`.
   - En tu `thought_process`, cita explícitamente el protocolo usado (ej. "Según protocolo de Sepsis v2024...").
"""
    
    # 3. Create new version
    version_count = len(pm.list_versions(prompt_type))
    new_v_id = f"v{version_count + 1}_rag"
    
    res = pm.create_version(
        prompt_type, 
        new_content, 
        model=current.get("model", "gemini-1.5-flash"),
        author="system_update", 
        notes="Added RAG evaluation instructions",
    )
    
    if res:
        pm.set_active_version(prompt_type, res)
        print(f"✅ Updated to version {res} with RAG instructions.")
    else:
        print("❌ Failed to create new version.")

if __name__ == "__main__":
    update_prompt()
