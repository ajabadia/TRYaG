# path: src/services/predictive_service.py
# Creado: 2025-11-29
"""
Servicio para generar alertas predictivas basadas en signos vitales y antecedentes.
Usa un prompt específico (triage_predictive) para detectar riesgos antes del triaje completo.
"""
import json
from src.services.gemini_client import get_gemini_service
from src.core.prompt_manager import PromptManager
from src.config import get_model_triage

DEFAULT_PREDICTIVE_PROMPT = """## ROL ##
Eres un sistema experto de alerta temprana clínica. Analizas signos vitales y antecedentes para detectar riesgos inminentes ANTES de la valoración médica completa.

## TAREA ##
Analiza los datos proporcionados y genera alertas si detectas valores fuera de rango o combinaciones peligrosas (ej: Sepsis, Shock, Crisis Hipertensiva).

## INPUTS ##
- Edad: {edad}
- Signos Vitales: {signos_vitales}
- HDA (Historia Actual): {hda}
- Contexto Clínico: {contexto_clinico}
- Antecedentes: {antecedentes}
- Historia Integral: {historia_integral}
- Alergias: {alergias}

## REGLAS ##
1. Sé extremadamente sensible a signos de inestabilidad hemodinámica o respiratoria.
2. Si todo es normal, devuelve una lista vacía de alertas y riesgo "Low".
3. Formato JSON EXACTO:
{
  "risk_level": "High" | "Medium" | "Low",
  "alerts": ["Alerta 1", "Alerta 2"]
}
"""

def generar_alertas_predictivas(edad, vital_signs, antecedentes=None, alergias=None, historia_integral=None, hda=None, contexto_clinico=None, prompt_content=None, user_id="system"):
    """
    Genera alertas predictivas usando Gemini.
    """
    # 1. Obtener Prompt y Configuración
    pm = PromptManager()
    prompt_data = None
    
    if prompt_content:
        base_prompt = prompt_content
        model_name = "gemini-1.5-flash" # Default for tests
        version_id = "test-override"
    else:
        prompt_data = pm.get_prompt("triage_predictive")
        if prompt_data:
            base_prompt = prompt_data.get("content", DEFAULT_PREDICTIVE_PROMPT)
            version_id = prompt_data.get("version_id", "unknown")
            model_name = prompt_data.get("model") or get_model_triage()
        else:
            base_prompt = DEFAULT_PREDICTIVE_PROMPT
            version_id = "default"
            model_name = get_model_triage()

    # 2. Formatear Signos Vitales
    vs_str = "No registrados"
    if vital_signs:
        vs_list = [f"{k.upper()}: {v}" for k, v in vital_signs.items() if v is not None]
        if vs_list:
            vs_str = ", ".join(vs_list)

    # 3. Inyectar variables
    final_prompt = base_prompt.replace("{edad}", str(edad))\
                              .replace("{signos_vitales}", vs_str)\
                              .replace("{hda}", str(hda or "No disponible"))\
                              .replace("{contexto_clinico}", str(contexto_clinico or "No disponible"))\
                              .replace("{antecedentes}", str(antecedentes or "Sin antecedentes relevantes"))\
                              .replace("{historia_integral}", str(historia_integral or "No disponible"))\
                              .replace("{alergias}", str(alergias or "No conocidas"))

    # 4. Llamar al Servicio Centralizado
    service = get_gemini_service()
    
    response_data, _ = service.generate_content(
        caller_id="predictive_service",
        user_id=user_id,
        call_type="predictive",
        prompt_type="triage_predictive",
        prompt_version_id=version_id,
        model_name=model_name,
        prompt_content=final_prompt,
        generation_config={
            "temperature": 0.1, # Muy determinista para alertas médicas
            "top_p": 0.95,
            "max_output_tokens": 1024,
            "response_mime_type": "application/json",
        },
        metadata={
            "patient_age": edad
        }
    )

    return response_data, final_prompt
