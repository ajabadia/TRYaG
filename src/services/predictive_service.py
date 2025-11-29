# path: src/services/predictive_service.py
# Creado: 2025-11-29
"""
Servicio para generar alertas predictivas basadas en signos vitales y antecedentes.
Usa un prompt específico (triage_predictive) para detectar riesgos antes del triaje completo.
"""
import google.generativeai as genai
import json
from src.config import get_model_triage

DEFAULT_PREDICTIVE_PROMPT = """## ROL ##
Eres un sistema experto de alerta temprana clínica. Analizas signos vitales y antecedentes para detectar riesgos inminentes ANTES de la valoración médica completa.

## TAREA ##
Analiza los datos proporcionados y genera alertas si detectas valores fuera de rango o combinaciones peligrosas (ej: Sepsis, Shock, Crisis Hipertensiva).

## INPUTS ##
- Edad: {edad}
- Signos Vitales: {signos_vitales}
- Antecedentes: {antecedentes}
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

def generar_alertas_predictivas(edad, vital_signs, antecedentes=None, alergias=None, prompt_content=None):
    """
    Genera alertas predictivas usando Gemini.

    Args:
        edad (int): Edad del paciente.
        vital_signs (dict): Diccionario con signos vitales.
        antecedentes (str, optional): Antecedentes médicos.
        alergias (str, optional): Alergias.
        prompt_content (str, optional): Contenido del prompt a usar (para pruebas).

    Returns:
        dict: Resultado con 'risk_level' y 'alerts'.
    """
    # 1. Obtener modelo configurado (usamos el mismo que para triaje)
    model_name = get_model_triage()
    
    generation_config = {
        "temperature": 0.1, # Muy determinista para alertas médicas
        "top_p": 0.95,
        "max_output_tokens": 1024,
        "response_mime_type": "application/json",
    }
    
    try:
        model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
    except Exception as e:
        return {"status": "ERROR", "msg": f"Error al inicializar modelo: {e}"}, ""

    # 2. Obtener Prompt
    if prompt_content:
        base_prompt = prompt_content
    else:
        from src.core.prompt_manager import PromptManager
        pm = PromptManager()
        prompt_data = pm.get_prompt("triage_predictive")
        
        if prompt_data:
            base_prompt = prompt_data.get("content", DEFAULT_PREDICTIVE_PROMPT)
        else:
            base_prompt = DEFAULT_PREDICTIVE_PROMPT

    # 3. Formatear Signos Vitales
    vs_str = "No registrados"
    if vital_signs:
        vs_list = [f"{k.upper()}: {v}" for k, v in vital_signs.items() if v is not None]
        if vs_list:
            vs_str = ", ".join(vs_list)

    # 4. Inyectar variables
    final_prompt = base_prompt.replace("{edad}", str(edad))\
                              .replace("{signos_vitales}", vs_str)\
                              .replace("{antecedentes}", str(antecedentes or "Sin antecedentes relevantes"))\
                              .replace("{alergias}", str(alergias or "No conocidas"))

    try:
        # 5. Llamada a Gemini
        response = model.generate_content(final_prompt)
        
        if not response.parts:
             return {"status": "ERROR", "msg": "Bloqueo de seguridad IA"}, final_prompt

        cleaned_text = response.text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.split("\n")
            if len(lines) >= 2:
                cleaned_text = "\n".join(lines[1:-1])
        
        result = json.loads(cleaned_text)
        return result, final_prompt

    except Exception as e:
        return {"status": "ERROR", "msg": f"Error en predicción: {e}"}, final_prompt
