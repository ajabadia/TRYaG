
import os
import sys

# Setup environment
web_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(web_root)
sys.path.append(os.path.join(web_root, 'src'))

from src.core.prompt_manager import PromptManager

def main():
    print("🚀 Adding 'clinical_dictation' prompt to MongoDB...")
    pm = PromptManager()
    
    prompt_content = """Actúa como un escriba médico experto.
Tu tarea es transcribir fielmente el archivo de audio proporcionado.
Objetivos:
1. Transcripción: Transcribe verbatim el contenido. Corrige gramática menor pero mantén la terminología médica exacta.
2. Extracción Estructurada: Si detectas signos vitales o datos estructurados claros (ej. "Tensión arterial 120 80", "Temperatura 38"), extráelos.

Devuelve SIEMPRE un JSON con este formato:
{
    "transcription": "El texto narrativo completo y corregido.",
    "structured_data": {
        "vital_signs": {
            "tas": null,
            "tad": null,
            "fc": null,
            "temp": null,
            "spo2": null
        },
        "symptoms": ["lista", "de", "sintomas"],
        "allergies": ["lista", "alergias"]
    }
}
Si no hay datos estructurados, devuelve los campos como null o listas vacías.
"""
    
    # Check if exists
    try:
        exists = pm.get_prompt("clinical_dictation")
        if exists:
            print("⚠️ Prompt 'clinical_dictation' already exists. Updating draft...")
            # We assume active version exists, let's create a new draft
            new_v = pm.create_version(
                prompt_type="clinical_dictation",
                content=prompt_content,
                model="gemini-2.0-flash-exp",
                author="system_update_script",
                notes="Created via script for Phase 11.4 refinement"
            )
            if new_v:
                print(f"✅ Created new draft version: {new_v}")
                # Activate it
                pm.set_active_version("clinical_dictation", new_v)
                print(f"✅ Activated version: {new_v}")
        else:
            print("✨ Creating new prompt 'clinical_dictation'...")
            ver = pm.create_version(
                prompt_type="clinical_dictation",
                content=prompt_content,
                model="gemini-2.0-flash-exp",
                author="system_setup",
                notes="Initial version for Voice Triage"
            )
            if ver:
                pm.set_active_version("clinical_dictation", ver)
                print(f"✅ Created and Activated version: {ver}")
            else:
                print("❌ Failed to create version.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
