# path: src/services/training_service.py
"""
Servicio para la gestión del Modo Formación (Training Mode).
Maneja la carga de casos clínicos y la evaluación de decisiones.
"""
from typing import List, Dict, Any, Optional
from services.training_data import CLINICAL_CASES

def get_all_cases() -> List[Dict[str, Any]]:
    """
    Obtiene todos los casos clínicos disponibles.
    
    Returns:
        List[Dict]: Lista de casos.
    """
    return CLINICAL_CASES

def get_case_by_id(case_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un caso específico por su ID.
    
    Args:
        case_id: ID del caso.
        
    Returns:
        Dict: Datos del caso o None si no existe.
    """
    for case in CLINICAL_CASES:
        if case["id"] == case_id:
            return case
    return None

def evaluate_decision(case_id: str, user_level: int, user_destination: str) -> Dict[str, Any]:
    """
    Evalúa la decisión del usuario contra el Gold Standard.
    
    Args:
        case_id: ID del caso.
        user_level: Nivel de triaje seleccionado por el usuario.
        user_destination: Destino seleccionado por el usuario.
        
    Returns:
        Dict: Resultado de la evaluación (score, feedback, gold_standard).
    """
    case = get_case_by_id(case_id)
    if not case:
        return {"error": "Caso no encontrado"}
        
    gold = case["gold_standard"]
    
    # Evaluación de Nivel
    level_diff = abs(gold["triage_level"] - user_level)
    level_score = max(0, 100 - (level_diff * 25)) # 100 si exacto, 75 si +/-1, 50 si +/-2...
    
    # Evaluación de Destino (Simple string match por ahora, idealmente fuzzy o normalizado)
    # Asumimos que si contiene la palabra clave es correcto
    dest_score = 100 if gold["destination"].lower() in user_destination.lower() or user_destination.lower() in gold["destination"].lower() else 0
    
    total_score = (level_score * 0.7) + (dest_score * 0.3)
    
    return {
        "total_score": round(total_score, 1),
        "level_score": level_score,
        "destination_score": dest_score,
        "is_correct_level": level_diff == 0,
        "is_correct_destination": dest_score == 100,
        "gold_standard": gold,
        "user_decision": {
            "level": user_level,
            "destination": user_destination
        }
    }
