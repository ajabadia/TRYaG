import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from db.repositories.prompts import get_prompts_repository
    print("✅ Módulos importados correctamente.")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

def seed_prompt():
    repo = get_prompts_repository()
    prompt_type = "second_opinion_reasoning"
    
    # Check if exists
    existing = repo.get_by_type(prompt_type)
    
    content = """
    ACTÚA COMO: Un Panel Médico Experto (Medical Board) compuesto por especialistas en Medicina Interna, Traumatología y Urgencias.
    
    TAREA: Realizar una "Segunda Opinión" exhaustiva sobre el caso clínico presentado.
    
    OBJETIVO:
    1. Detectar inconsistencias, riesgos ocultos o diagnósticos diferenciales graves que el triaje inicial podría haber pasado por alto.
    2. Utilizar un proceso de razonamiento "Chain of Thought" (Cadena de Pensamiento) para justificar cada conclusión.
    
    ENTRADA DE DATOS:
    - Perfil del Paciente (Edad, Género, Antecedentes)
    - Historial de Triajes (Signos vitales, quejas principales)
    - Archivos Multimedia (Transcripciones, Análisis de Imágenes)
    - Notas del Médico Solicitante (Dudas específicas)
    
    FORMATO DE RESPUESTA (JSON estricto):
    {
        "thought_process": "Explica tu razonamiento paso a paso aquí...",
        "diagnostic_hypothesis": [
            {"diagnosis": "Nombre", "probability": "Alta/Media/Baja", "justification": "..."}
        ],
        "red_flags": ["Lista de alertas rojas o riesgos vitales..."],
        "recommended_actions": ["Pruebas complementarias...", "Interconsultas..."],
        "clinical_summary": "Resumen ejecutivo para el médico."
    }
    
    IMPORTANTE:
    - Sé conservador en cuanto a la seguridad del paciente (ante la duda, sugiere descartar lo grave).
    - No inventes datos. Si falta información, solicítala en 'recommended_actions'.
    """
    
    if not existing:
        print(f"creando nuevo prompt type: {prompt_type}")
        repo.create_prompt_type(prompt_type)
        
    # Añadir nueva versión siempre para actualizar contenido
    version_id = "v1_release"
    success = repo.add_version(
        prompt_type=prompt_type,
        version_id=version_id,
        content=content,
        model="gemini-1.5-pro", # Usamos 1.5 Pro como motor de "Reasoning"
        author="system_seed",
        notes="Prompt inicial para Módulo Segunda Opinión",
        status="active"
    )
    
    if success:
        repo.set_active_version(prompt_type, version_id)
        print(f"✅ Prompt '{prompt_type}' (v: {version_id}) configurado correctamente.")
    else:
        print(f"⚠️ No se pudo añadir la versión (quizás ya existía).")

if __name__ == "__main__":
    seed_prompt()
