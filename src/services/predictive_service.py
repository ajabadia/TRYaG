# path: src/services/predictive_service.py
# Creado: 2025-11-29
"""
Servicio para generar alertas predictivas basadas en signos vitales y antecedentes.
Usa un prompt específico (triage_predictive) para detectar riesgos antes del triaje completo.
"""
import json
try:
    from .gemini_client import get_gemini_service
    from ..core.prompt_manager import PromptManager
    from ..core.config import get_model_triage
except ImportError:
    from services.gemini_client import get_gemini_service
    from core.prompt_manager import PromptManager
    from core.config import get_model_triage

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

from services.contingency_service import is_contingency_active

def generar_alertas_predictivas(edad, vital_signs, antecedentes=None, alergias=None, historia_integral=None, hda=None, contexto_clinico=None, prompt_content=None, user_id="system"):
    """
    Genera alertas predictivas usando Gemini.
    """
    # 0. Check Contingency
    if is_contingency_active():
        return {
            "risk_level": "Unknown",
            "alerts": ["Análisis IA no disponible en modo contingencia (Offline)."],
            "status": "OFFLINE"
        }, "Offline Mode"

    # 1. Obtener Prompt y Configuración
    pm = PromptManager()
    prompt_data = None
    
    if prompt_content:
        base_prompt = prompt_content
        model_name = "gemini-2.5-flash" # Default for tests
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
    
    # Configuración de Seguridad para evitar "Empty response parts" en contenido médico
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

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
            "max_output_tokens": 4096,
            "response_mime_type": "application/json",
        },
        safety_settings=safety_settings,
        metadata={
            "patient_age": edad
        }
    )

    return response_data, final_prompt

class PredictiveService:
    """
    Servicio para cálculos predictivos y de riesgo (PTR).
    Wrapper que expone lógica para API y uso interno.
    """
    def __init__(self):
        # En el futuro, cargar configuracion de DB (PTRConfig)
        pass

    def calculate_ptr(self, data: dict) -> float:
        """
        Calcula el Patient Triage Risk Score basado en reglas clínicas.
        Devuelve un score numérico.
        """
        score = 0.0
        
        # Extraer datos con defaults seguros
        sistolica = data.get("sistolica")
        fc = data.get("frecuencia_cardiaca")
        spo2 = data.get("saturacion")
        edad = data.get("edad", 0)
        temp = data.get("temperatura")
        glasgow = data.get("glasgow", 15)
        
        # Reglas básicas (Simplificadas tipo NEWS2)
        
        # 1. Tensión Arterial Sistólica
        if sistolica:
            if sistolica <= 90: score += 3
            elif sistolica >= 220: score += 3
            elif 91 <= sistolica <= 100: score += 2
            elif 101 <= sistolica <= 110: score += 1
            
        # 2. Frecuencia Cardíaca
        if fc:
            if fc <= 40: score += 3
            elif fc >= 131: score += 3
            elif 111 <= fc <= 130: score += 2
            elif 41 <= fc <= 50: score += 1
            elif 91 <= fc <= 110: score += 1
            
        # 3. Saturación
        if spo2:
            if spo2 <= 91: score += 3
            elif 92 <= spo2 <= 93: score += 2
            elif 94 <= spo2 <= 95: score += 1
            
        # 4. Temperatura
        if temp:
            if temp <= 35.0: score += 3
            elif temp >= 39.1: score += 2
            elif 35.1 <= temp <= 36.0: score += 1
            elif 38.1 <= temp <= 39.0: score += 1
            
        # 5. Glasgow (Inverso)
        if glasgow < 15:
            score += (15 - glasgow) # Cada punto menos es riesgo
            
        # 6. Edad
        if edad >= 65:
            score += 1 # Factor de riesgo geriátrico base
            
        return float(score)

    def generate_alerts(self, **kwargs) -> dict:
        """Wrapper para generar_alertas_predictivas"""
        # Adaptar argumentos si es necesario
        return generar_alertas_predictivas(**kwargs)
