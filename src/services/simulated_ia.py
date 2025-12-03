# path: src/services/simulated_ia.py
# Creado: 2025-11-21
# Última modificación: 2025-12-03
"""
Módulo para la simulación de un modelo de IA para triaje traumatológico.
Ahora configurable mediante JSON.
"""
import json
from core.prompt_manager import PromptManager

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
    warnings = []
    for word in exclusion_keywords:
        if word in motivo:
            warnings.append(f"⚠️ ALERTA: Detectado síntoma '{word}' no compatible con Traumatología.")
            
    # Si hay warnings, los añadimos al razonamiento pero NO detenemos la ejecución
    # El status será SUCCESS pero con flag de warning para la UI

    # 3. LÓGICA DE TRIAJE (ÁRBOL DE DECISIÓN)
    # Estructura: Signos Vitales -> Exclusiones -> Discriminadores -> Modificadores
    
    nivel = 5 # Default: No Urgente
    razonamiento = []
    
    # A. Signos Vitales Críticos (Simulado - en producción vendría de datos reales)
    # Si el dolor es extremo, sube prioridad
    pain_threshold = config.get("pain_threshold", 8)
    if dolor >= pain_threshold:
        nivel = min(nivel, 3)
        razonamiento.append(f"Dolor severo ({dolor}/10) indica urgencia.")

    # B. Árbol de Reglas (Discriminadores)
    # Las reglas se evalúan en orden de prioridad (Nivel 1 -> Nivel 5)
    rules = config.get("rules", [])
    # Ordenar reglas por nivel ascendente (1 es más prioritario que 5)
    rules.sort(key=lambda x: x.get("level", 5))
    
    matched_rule = False
    for rule in rules:
        keywords = rule.get("keywords", [])
        rule_level = rule.get("level", 4)
        rule_reason = rule.get("reason", "")
        required_symptoms = rule.get("required_symptoms", []) # Futuro: Combinación de síntomas
        
        # Chequeo de keywords
        for kw in keywords:
            if kw in motivo:
                # Si encontramos una regla de mayor prioridad (menor nivel numérico)
                if rule_level < nivel:
                    nivel = rule_level
                    razonamiento.append(f"Regla coincidente: '{kw}' -> {rule_reason}")
                    matched_rule = True
                break # Salir de keywords, pasar a siguiente regla
        
        # Si ya encontramos una regla de Nivel 1 o 2, paramos (Short-circuit)
        if matched_rule and nivel <= 2:
            break

    # C. Modificadores Contextuales
    # Edad
    age_threshold = config.get("age_threshold", 75)
    if edad > age_threshold:
        old_level = nivel
        nivel = max(1, nivel - 1) # Sube un nivel de urgencia (resta 1), tope 1
        if nivel < old_level:
            razonamiento.append(f"Ajuste por edad (> {age_threshold} años): Se eleva prioridad.")

    # Default
    if not razonamiento:
        nivel = config.get("default_level", 4)
        razonamiento.append(config.get("default_reason", "Patología traumatológica sin signos de riesgo vital inmediato."))

    niveles_info = {
        1: {"color": "red", "text": "NIVEL I - RESUCITACIÓN"}, 
        2: {"color": "orange", "text": "NIVEL II - EMERGENCIA"}, 
        3: {"color": "#FFD700", "text": "NIVEL III - URGENCIA"}, 
        4: {"color": "green", "text": "NIVEL IV - MENOS URGENTE"}, 
        5: {"color": "blue", "text": "NIVEL V - NO URGENTE"}
    }

    # Construir respuesta
    razones_list = []
    
    # Añadir warnings al principio si existen
    if warnings:
        razones_list.extend(warnings)
        
    # Añadir contexto básico
    razones_list.append(f"Paciente de {edad} años.")
    razones_list.append(f"Dolor nivel {dolor}/10.")
    
    # Añadir razonamiento del árbol
    razones_list.extend(razonamiento)
        
    return {
        "nivel_sugerido": nivel,
        "nivel": {
            "text": niveles_info.get(nivel, niveles_info[4])["text"],
            "color": niveles_info.get(nivel, niveles_info[4])["color"]
        },
        "razones": razones_list, # Ahora devolvemos lista directamente
        "razonamiento": razones_list, # Legacy support
        "status": "SUCCESS",
        "warnings": warnings # Para manejo específico en UI si se desea
    }