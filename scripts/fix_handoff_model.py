import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.db.connection import get_database

def fix_handoff_model():
    db = get_database()
    repo = db.get_collection("prompts")
    
    # Buscar el prompt de handoff
    prompt = repo.find_one({"prompt_type": "shift_handoff"})
    if not prompt:
        print("No se encontró prompt shift_handoff")
        return

    active_version_id = prompt.get("active_version")
    if not active_version_id:
        print("No hay versión activa")
        return
        
    print(f"Versión activa: {active_version_id}")
    
    # Actualizar la versión activa dentro del array/objeto (dependiendo de estructura)
    # Según prompt_manager logic: { versions: { "v1": { ... } } }
    
    # Nota: MongoDB repo updates usually handle this via update_one
    # Manually updating specifically the model of the active version
    
    # Path to model field: versions.v1.model
    update_path = f"versions.{active_version_id}.model"
    
    result = repo.update_one(
        {"prompt_type": "shift_handoff"},
        {"$set": {update_path: "gemini-2.5-flash"}}
    )
    
    print(f"Actualizado: {result.modified_count} documentos.")
    if result.modified_count > 0:
        print("✅ Modelo cambiado a 'gemini-2.5-flash' exitosamente.")

if __name__ == "__main__":
    fix_handoff_model()
