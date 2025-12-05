import sys
import os
from datetime import datetime

# Add project root and src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.connection import get_database
from db.repositories.prompts import PromptsRepository

def update_prompt():
    print("Connecting to database...")
    # db = get_database() # Not needed if repo handles it
    repo = PromptsRepository()
    
    prompt_type = "triage_gemini"
    print(f"Fetching active version for {prompt_type}...")
    
    current_version = repo.get_active_version(prompt_type)
    if not current_version:
        print("Error: No active version found.")
        return

    content = current_version["content"]
    
    # Check if already updated
    if "cie10_posibles" in content:
        print("Prompt already contains CIE-10 instructions.")
        return

    print("Updating content...")
    
    # 1. Update Reasoning Process
    target_reasoning = "3. **Decisión**: Determina el nivel de triaje basándote en el PTR y la escala Manchester."
    replacement_reasoning = "3. **Decisión**: Determina el nivel de triaje basándote en el PTR y la escala Manchester.\n4. **Codificación**: Sugiere códigos CIE-10 probables."
    
    new_content = content.replace(target_reasoning, replacement_reasoning)
    
    # 2. Update JSON Format
    target_json = '  "acciones_sugeridas": ["Acción 1", "Acción 2"]'
    replacement_json = '  "acciones_sugeridas": ["Acción 1", "Acción 2"],\n  "cie10_posibles": [{"codigo": "R07.4", "descripcion": "Dolor en el pecho"}]'
    
    new_content = new_content.replace(target_json, replacement_json)
    
    if new_content == content:
        print("Warning: Could not find target strings to replace.")
        return

    # Create new version
    version_id = f"v{int(current_version['version_id'][1:]) + 1}"
    print(f"Creating new version {version_id}...")
    
    repo.add_version(
        prompt_type=prompt_type,
        version_id=version_id,
        content=new_content,
        model=current_version.get("model", "gemini-2.5-flash"),
        author="system_update_script",
        notes="Added CIE-10 coding request",
        status="draft"
    )
    
    print("Setting as active...")
    repo.set_active_version(prompt_type, version_id)
    print("Done!")

if __name__ == "__main__":
    update_prompt()
