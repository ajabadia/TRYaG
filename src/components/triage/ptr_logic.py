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
    """Evalúa una regla individual basada en rangos min/max."""
    # Soporte para objeto Pydantic o dict (por si acaso)
    r_min = getattr(rule, 'min', None)
    r_max = getattr(rule, 'max', None)
    
    # Si es dict
    if r_min is None and isinstance(rule, dict):
        r_min = rule.get('min')
        r_max = rule.get('max')
        
    if r_min is None or r_max is None:
        return False
        
    return r_min <= value <= r_max

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

    # Métricas a evaluar (incluyendo dolor/eva)
    metrics_to_check = ['gcs', 'spo2', 'pas', 'fr', 'fc', 'temp', 'dolor', 'eva']

    for key in metrics_to_check:
        # Normalizar clave (dolor -> eva)
        lookup_key = key
        if key == 'dolor': lookup_key = 'eva'
        
        val = vital_signs.get(key)
        
        # Si no está en vital_signs, buscar en el root (caso dolor)
        if val is None and key == 'dolor':
             # Esto debería venir en vital_signs si se procesó bien, pero por seguridad:
             pass 

        if val is None:
            continue
            
        try:
            val = float(val)
        except:
            continue

        config = _get_config(lookup_key)
        if not config:
            # Si buscamos 'dolor' y no hay config, intentamos 'eva'
            if key == 'dolor': config = _get_config('eva')
            if not config: continue

        # 1. Determinar puntos base según reglas
        base_points = 0
        matched_rule = None
        
        # Iterar reglas y tomar la que dé MAYOR puntuación en caso de solapamiento (Peor caso)
        # O la primera que coincida si son excluyentes.
        for rule in config.rules:
            if _evaluate_rule(val, rule):
                # Asumimos que si hay múltiples matches, queremos el de mayor puntos
                r_points = getattr(rule, 'points', 0)
                if isinstance(rule, dict): r_points = rule.get('points', 0)
                
                if r_points >= base_points:
                    base_points = r_points
                    matched_rule = rule
        
        if base_points == 0 and matched_rule is None:
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
            details.append(f"{config.name} ({val}): {base_points} {mult_desc} = +{points}")

    # Interpretación (Estudio 2.2)
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

    if not details:
        details.append("Sin criterios de riesgo identificados.")

    return {
        "score": score,
        "level_text": level,
        "color": color,
        "priority_code": prio,
        "details": details
    }

