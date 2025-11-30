# path: src/services/triage_service.py
# Creado: 2025-11-23
"""
Servicio para la lógica de triaje con Gemini.
"""
import json
from src.services.gemini_client import get_gemini_service
from src.core.prompt_manager import PromptManager
from src.config import get_model_triage

def llamar_modelo_gemini(motivo, edad, dolor, vital_signs=None, imagen=None, prompt_content=None, triage_result=None, antecedentes=None, alergias=None, user_id="system"):
    """
    Llama al modelo Gemini de Google para obtener una sugerencia de triaje.
    """
    # 1. Obtener Prompt y Configuración
    pm = PromptManager()
    prompt_data = None
    
    if prompt_content:
        base_prompt = prompt_content
        model_name = "gemini-1.5-flash" # Default for tests if not specified
        version_id = "test-override"
    else:
        # Obtener versión activa
        prompt_data = pm.get_prompt("triage_gemini")
        if not prompt_data:
            return {"status": "ERROR", "msg": "No se ha encontrado un prompt activo para 'triage_gemini'."}, ""
            
        base_prompt = prompt_data.get("content", "")
        version_id = prompt_data.get("version_id", "unknown")
        # Usar modelo de la versión o fallback a config global
        model_name = prompt_data.get("model") or get_model_triage()

    # 2. Formatear Signos Vitales
    vs_str = "No registrados"
    if vital_signs:
        vs_list = []
        for k, v in vital_signs.items():
            if v is not None:
                vs_list.append(f"{k.upper()}: {v}")
        
        if triage_result:
            vs_list.append("\n--- ANÁLISIS AUTOMÁTICO DE SIGNOS VITALES ---")
            vs_list.append(f"Clasificación Global: {triage_result.get('label', 'N/A')} (Prioridad {triage_result.get('final_priority', 'N/A')})")
            vs_list.append(f"Tiempo Máximo Sugerido: {triage_result.get('wait_time', 'N/A')}")
            
            if 'details' in triage_result:
                vs_list.append("Detalles:")
                for det in triage_result['details']:
                    icon = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴", "black": "⚫", "gray": "⚪"}.get(det.get('color'), "")
                    vs_list.append(f"- {det.get('metric', '').upper()}: {det.get('value')} -> {icon} {det.get('label', '')}")
        
        if vs_list:
            vs_str = "\n".join(vs_list)

    # 3. Inyectar variables
    motivo_completo = str(motivo)
    if antecedentes:
        motivo_completo += f"\n\n[ANTECEDENTES]: {antecedentes}"
    if alergias:
        motivo_completo += f"\n\n[ALERGIAS]: {alergias}"
        
    final_prompt = base_prompt.replace("{motivo}", motivo_completo)\
                              .replace("{edad}", str(edad))\
                              .replace("{dolor}", str(dolor))\
                              .replace("{signos_vitales}", vs_str)

    prompt_parts = [final_prompt]
    if imagen:
        prompt_parts.append("\nInput (Imagen):")
        prompt_parts.append(imagen)

    # 4. Llamar al Servicio Centralizado
    service = get_gemini_service()
    
    response_data, raw_prompt = service.generate_content(
        caller_id="triage_service",
        user_id=user_id,
        call_type="triage",
        prompt_type="triage_gemini",
        prompt_version_id=version_id,
        model_name=model_name,
        prompt_content=prompt_parts,
        generation_config={
            "temperature": 0.2,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
            "response_mime_type": "application/json",
        },
        metadata={
            "patient_age": edad,
            "has_image": bool(imagen)
        }
    )

    # 5. Post-procesamiento específico de Triaje
    if response_data.get("status") == "ERROR":
        return response_data, final_prompt

    # Manejar exclusión (Nivel 0)
    if response_data.get("nivel_sugerido") == 0:
        return {
            "status": "EXCLUDED",
            "msg": f"⚠️ ALERTA: La IA ha clasificado el caso como no traumatológico. {response_data.get('razonamiento', [''])[0]}"
        }, final_prompt

    return response_data, final_prompt
