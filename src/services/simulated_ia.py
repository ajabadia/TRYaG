# path: src/services/simulated_ia.py
# Creado: 2025-11-21
# Última modificación: 2025-11-23
"""
Módulo para la simulación de un modelo de IA para triaje traumatológico.
Ahora configurable mediante JSON.
"""
import json
from src.core.prompt_manager import PromptManager

def simulacion_ia(motivo, edad, dolor, prompt_content=None):
    """
    Simula el procesamiento de un modelo de IA para triaje traumatológico.
    
    Carga la configuración (reglas, keywords) desde el PromptManager o usa el prompt_content inyectado.
    """
    motivo = motivo.lower()
    
    # 1. Cargar Configuración
    if prompt_content:
        try:
            config = json.loads(prompt_content)
        except json.JSONDecodeError:
            return {"status": "ERROR", "msg": "Error de formato en la configuración de simulación (JSON inválido)."}
    else:
        pm = PromptManager()
        prompt_data = pm.get_prompt("triage_sim")
        
        if not prompt_data:
            # Fallback hardcoded si no hay configuración
            config = {
                "exclusion_keywords": ["pecho", "respirar", "fiebre", "mareo", "vomito", "abdomen", "desmayo"],
                "rules": [
                    {"keywords": ["abierta", "hueso", "sangre"], "level": 2, "reason": "Posible fractura abierta o lesión vascular."},
                    {"keywords": ["deformidad", "movilidad"], "level": 3, "reason": "Signos de fractura o luxación con compromiso funcional."}
                ],
                "pain_threshold": 8,
                "pain_level_cap": 3,
                "age_threshold": 75,
                "age_level_cap": 3,
                "default_level": 4,
                "default_reason": "Patología traumatológica sin signos de riesgo vital inmediato."
            }
        else:
            try:
                config = json.loads(prompt_data.get("content", "{}"))
            except json.JSONDecodeError:
                return {"status": "ERROR", "msg": "Error de formato en la configuración de simulación (JSON inválido)."}

    # 2. GUARDRAILS (Filtro de Seguridad)
    exclusion_keywords = config.get("exclusion_keywords", [])
    for word in exclusion_keywords:
        if word in motivo:
            return {
                "status": "EXCLUDED",
                "msg": f"⚠️ ALERTA: Detectado síntoma '{word}' no compatible con Traumatología. Derivar a Urgencias Generales."
            }

    # 3. LÓGICA DE TRIAJE
    nivel = config.get("default_level", 4)
    razonamiento = []

    # Reglas por keywords
    rules = config.get("rules", [])
    for rule in rules:
        keywords = rule.get("keywords", [])
        rule_level = rule.get("level", 4)
        rule_reason = rule.get("reason", "")
        
        for kw in keywords:
            if kw in motivo:
                if rule_level < nivel: # Prioridad a menor nivel (más urgente)
                    nivel = rule_level
                    if rule_reason not in razonamiento:
                        razonamiento.append(rule_reason)
                break # Solo aplicar una vez por regla

    # Factor Dolor
    pain_threshold = config.get("pain_threshold", 8)
    pain_cap = config.get("pain_level_cap", 3)
    if dolor >= pain_threshold:
        nivel = min(nivel, pain_cap)
        razonamiento.append(f"Nivel de dolor reportado alto ({dolor}/10).")
    
    # Factor Edad
    age_threshold = config.get("age_threshold", 75)
    age_cap = config.get("age_level_cap", 3)
    if edad > age_threshold:
        nivel = min(nivel, age_cap)
        razonamiento.append("Paciente geriátrico (riesgo aumentado de complicaciones).")

    if not razonamiento:
        razonamiento.append(config.get("default_reason", "Patología traumatológica sin signos de riesgo vital inmediato."))

    niveles_info = {
        1: {"color": "red", "text": "NIVEL I - RESUCITACIÓN"}, 
        2: {"color": "orange", "text": "NIVEL II - EMERGENCIA"}, 
        3: {"color": "#FFD700", "text": "NIVEL III - URGENCIA"}, 
        4: {"color": "green", "text": "NIVEL IV - MENOS URGENTE"}, 
        5: {"color": "blue", "text": "NIVEL V - NO URGENTE"}
    }

    return {"status": "SUCCESS", "nivel": niveles_info.get(nivel, niveles_info[4]), "razones": razonamiento}