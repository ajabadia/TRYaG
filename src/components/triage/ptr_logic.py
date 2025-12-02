"""
Lógica de Puntuación Total de Riesgo (PTR).
Implementa un sistema de triaje ponderado basado en multiplicadores clínicos configurables.
"""
from typing import Dict, Any, List, Optional
from db.repositories.ptr_config import get_ptr_config_repository, PTRConfig

# Cache simple en memoria para evitar consultas constantes a DB durante la misma sesión
_CONFIG_CACHE: Dict[str, PTRConfig] = {}

def _get_config(metric_key: str) -> Optional[PTRConfig]:
    """Obtiene la configuración, usando caché si está disponible."""
    if metric_key in _CONFIG_CACHE:
        return _CONFIG_CACHE[metric_key]
    
    repo = get_ptr_config_repository()
    config = repo.get_config(metric_key)
    if config:
        _CONFIG_CACHE[metric_key] = config
    return config

def _evaluate_rule(value: float, rule) -> bool:
    """Evalúa una regla individual."""
    op = rule.operator
    ref = rule.value
    
    if op == "<": return value < ref
    if op == "<=": return value <= ref
    if op == ">": return value > ref
    if op == ">=": return value >= ref
    if op == "==": return value == ref
    if op == "between":
        return ref <= value <= (rule.value_max or ref)
    return False

def calculate_ptr_score(vital_signs: Dict[str, Any], context_flags: Dict[str, bool]) -> Dict[str, Any]:
    """
    Calcula el PTR (Puntuación Total de Riesgo) basado en signos vitales y configuración dinámica.
    """
    score = 0
    details = []
    
    # Flags de contexto
    is_geriatric = context_flags.get('criterio_geriatrico', False)
    is_immuno = context_flags.get('criterio_inmunodeprimido', False) or \
                context_flags.get('ctx_is_immuno', False) or \
                context_flags.get('ctx_is_onco', False)

    # Métricas a evaluar
    metrics_to_check = ['gcs', 'spo2', 'pas', 'fr', 'fc', 'temp', 'dolor']

    for key in metrics_to_check:
        val = vital_signs.get(key)
        if val is None:
            continue
            
        try:
            val = float(val)
        except:
            continue

        config = _get_config(key)
        if not config:
            continue

        # 1. Determinar puntos base según reglas
        # Se asume que las reglas están ordenadas por prioridad o que se toma la primera que coincida (o la más grave).
        # En la implementación hardcoded original, se usaban if/elif, lo que implica prioridad.
        # Aquí iteraremos y tomaremos la primera regla que coincida.
        # IMPORTANTE: Las reglas en DB deben estar ordenadas lógicamente (ej: <9 antes que <13).
        
        base_points = 0
        matched_rule = None
        
        for rule in config.rules:
            if _evaluate_rule(val, rule):
                base_points = rule.points
                matched_rule = rule
                break # Stop at first match (priority)
        
        if base_points == 0:
            continue

        # 2. Aplicar multiplicadores
        multiplier = config.base_multiplier
        mult_desc = f"x{int(multiplier)}" if multiplier.is_integer() else f"x{multiplier}"
        
        # Modificadores de contexto
        if is_geriatric and config.geriatric_multiplier:
            multiplier = config.geriatric_multiplier
            mult_desc = f"x{int(multiplier)} (Geriátrico)" if multiplier.is_integer() else f"x{multiplier} (Geriátrico)"
            
        if is_immuno and config.immuno_multiplier:
            multiplier = config.immuno_multiplier
            mult_desc = f"x{int(multiplier)} (Inmuno)" if multiplier.is_integer() else f"x{multiplier} (Inmuno)"

        # 3. Calcular total parcial
        points = base_points * multiplier
        score += points
        
        if points > 0:
            rule_desc = matched_rule.description if matched_rule else ""
            details.append(f"{config.name} ({val}): {base_points} {mult_desc} = +{points} [{rule_desc}]")

    # Interpretación (Hardcoded por ahora, podría moverse a DB también en TriageRangeConfig)
    if score > 15:
        level = "Nivel I/II (Rojo/Naranja)"
        color = "red"
        prio = 1
    elif score >= 8:
        level = "Nivel II/III (Naranja/Amarillo)"
        color = "orange"
        prio = 2
    elif score >= 3:
        level = "Nivel III/IV (Amarillo/Verde)"
        color = "yellow"
        prio = 3
    else:
        level = "Nivel IV/V (Verde/Azul)"
        color = "green"
        prio = 4

    return {
        "score": score,
        "level_text": level,
        "color": color,
        "priority_code": prio,
        "details": details
    }

