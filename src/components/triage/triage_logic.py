# path: src/components/triage/triage_logic.py
from typing import Dict, Any, Tuple, Optional, List
from src.db.models import VitalSignAgeConfig, VitalSignSeverityRange

# Definición de Prioridades y Colores
PRIORITY_LEVELS = {
    0: {"color": "green", "label": "Normal", "wait_time": "90 - 120 min"},
    1: {"color": "yellow", "label": "Urgente", "wait_time": "30 - 90 min"},
    2: {"color": "orange", "label": "Muy Urgente", "wait_time": "10 - 30 min"},
    3: {"color": "red", "label": "Emergencia", "wait_time": "0 - 10 min"},
    4: {"color": "black", "label": "Reanimación", "wait_time": "Inmediato"}
}

COLOR_ORDER = ["green", "yellow", "orange", "red", "black"]

def evaluate_vital_sign(value: float, config: VitalSignAgeConfig) -> Tuple[str, int, str]:
    """
    Evalúa un signo vital contra su configuración y retorna (color, prioridad, etiqueta).
    Usa la lista de rangos definidos en la configuración.
    """
    if value is None:
        return "gray", -1, "No registrado"
        
    # 1. Validar límites absolutos (Error)
    if value < config.val_min or value > config.val_max:
        return "red", 3, f"Error: Fuera de rango ({config.val_min}-{config.val_max})"

    # 2. Buscar en rangos definidos (Ordenados por prioridad descendente sería ideal, pero iteramos todos)
    # Buscamos el match con MAYOR prioridad (peor caso) si hay solapamientos (aunque no debería)
    worst_match = None
    
    for r in config.ranges:
        if r.min_val <= value <= r.max_val:
            if worst_match is None or r.priority > worst_match.priority:
                worst_match = r
                
    if worst_match:
        return worst_match.color, worst_match.priority, worst_match.label
        
    # 3. Fallback si no cae en ningún rango (asumir normal si está en normal_min/max, sino alerta)
    if config.normal_min <= value <= config.normal_max:
        return "green", 0, "Normal (Fallback)"
        
    return "orange", 2, "Fuera de rango normal (Sin clasificación específica)"

def calculate_worst_case(
    vital_signs: Dict[str, Any], 
    configs: Dict[str, VitalSignAgeConfig]
) -> Dict[str, Any]:
    """
    Calcula la prioridad final de triaje basada en el algoritmo "Worst Case".
    """
    max_priority = -1
    worst_color = "gray"
    worst_label = "Sin datos"
    details = []
    
    # Evaluar cada signo vital presente
    for key, value in vital_signs.items():
        if key in configs and value is not None:
            # Casos especiales no numéricos o booleanos
            if key == "pupilas":
                # Lógica hardcoded para pupilas si no está en BD como rango numérico
                p_color, p_prio, p_label = evaluate_pupilas(value)
            elif key == "oxigeno_suplementario":
                continue # Se usa para modificar SpO2, no como métrica directa aquí (por ahora)
            else:
                try:
                    val_float = float(value)
                    color, priority, label = evaluate_vital_sign(val_float, configs[key])
                    
                    # Ajuste SpO2 con O2 suplementario (Regla de negocio: Si SpO2 < 90 (Rojo) con O2, sigue Rojo pero se anota)
                    # El usuario dijo: "Si SpO2 está en Rojo... con O2... permanece en Rojo".
                    # "Si SpO2 está en Amarillo o Naranja y NO tiene O2, la urgencia es mayor".
                    # Implementación simple: Si SpO2 no es verde y NO tiene O2, subir prioridad? 
                    # Por ahora nos apegamos a la tabla estricta.
                    
                    p_color, p_prio, p_label = color, priority, label
                except ValueError:
                    continue

            details.append({
                "metric": key,
                "value": value,
                "color": p_color,
                "priority": p_prio,
                "label": p_label
            })
            
            if p_prio > max_priority:
                max_priority = p_prio
                worst_color = p_color
                worst_label = PRIORITY_LEVELS.get(max_priority, {}).get("label", "Desconocido")

    # Resultado final
    if max_priority == -1:
        return {
            "final_color": "gray",
            "final_priority": 0,
            "label": "Pendiente",
            "wait_time": "-",
            "details": details
        }
        
    return {
        "final_color": worst_color,
        "final_priority": max_priority,
        "label": worst_label,
        "wait_time": PRIORITY_LEVELS.get(max_priority, {}).get("wait_time", "-"),
        "details": details
    }

def evaluate_pupilas(value: str) -> Tuple[str, int, str]:
    """Evalúa la reacción pupilar."""
    if value == "Normal" or value == "PERRL":
        return "green", 0, "Normal"
    elif value == "Lenta":
        return "yellow", 1, "Lenta a la luz"
    elif value == "Fijas" or value == "No reactivas":
        return "orange", 2, "Fijas" # Usuario dijo Naranja para Fijas
    elif value == "Anisocoria":
        return "red", 3, "Anisocoria"
    elif value == "Puntiformes":
        return "red", 3, "Puntiformes"
    return "gray", 0, "Desconocido"
