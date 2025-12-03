# path: src/components/triage/triage_logic.py
from typing import Dict, Any, Tuple, Optional, List
from db.models import VitalSignAgeConfig, VitalSignSeverityRange
from components.triage.ptr_logic import calculate_ptr_score

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

def calculate_news_score(vital_signs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula el National Early Warning Score (NEWS2).
    Retorna score total y desglose.
    """
    score = 0
    details = []
    
    # 1. Frecuencia Respiratoria (rpm)
    fr = vital_signs.get('fr')
    if fr is not None:
        try:
            fr = float(fr)
            s = 0
            if fr <= 8: s = 3
            elif 9 <= fr <= 11: s = 1
            elif 12 <= fr <= 20: s = 0
            elif 21 <= fr <= 24: s = 2
            elif fr >= 25: s = 3
            score += s
            if s > 0: details.append(f"FR ({fr}): +{s}")
        except: pass

    # 2. Saturación de Oxígeno (%)
    spo2 = vital_signs.get('spo2')
    if spo2 is not None:
        try:
            spo2 = float(spo2)
            s = 0
            if spo2 <= 91: s = 3
            elif 92 <= spo2 <= 93: s = 2
            elif 94 <= spo2 <= 95: s = 1
            elif spo2 >= 96: s = 0
            score += s
            if s > 0: details.append(f"SpO2 ({spo2}%): +{s}")
        except: pass

    # 3. Aire u Oxígeno Suplementario
    o2 = vital_signs.get('oxigeno_suplementario', False)
    if o2:
        score += 2
        details.append("Oxígeno Suplementario: +2")

    # 4. Presión Arterial Sistólica (mmHg)
    pas = vital_signs.get('pas')
    if pas is not None:
        try:
            pas = float(pas)
            s = 0
            if pas <= 90: s = 3
            elif 91 <= pas <= 100: s = 2
            elif 101 <= pas <= 110: s = 1
            elif 111 <= pas <= 219: s = 0
            elif pas >= 220: s = 3
            score += s
            if s > 0: details.append(f"PAS ({pas}): +{s}")
        except: pass

    # 5. Frecuencia Cardíaca (ppm)
    fc = vital_signs.get('fc')
    if fc is not None:
        try:
            fc = float(fc)
            s = 0
            if fc <= 40: s = 3
            elif 41 <= fc <= 50: s = 1
            elif 51 <= fc <= 90: s = 0
            elif 91 <= fc <= 110: s = 1
            elif 111 <= fc <= 130: s = 2
            elif fc >= 131: s = 3
            score += s
            if s > 0: details.append(f"FC ({fc}): +{s}")
        except: pass

    # 6. Nivel de Conciencia (GCS < 15 o AVPU != Alert)
    # Simplificación: Si GCS < 15 -> +3
    gcs = vital_signs.get('gcs')
    if gcs is not None:
        try:
            gcs = float(gcs)
            if gcs < 15:
                score += 3
                details.append(f"Conciencia Alterada (GCS {gcs}): +3")
        except: pass

    # 7. Temperatura (°C)
    temp = vital_signs.get('temp')
    if temp is not None:
        try:
            temp = float(temp)
            s = 0
            if temp <= 35.0: s = 3
            elif 35.1 <= temp <= 36.0: s = 1
            elif 36.1 <= temp <= 38.0: s = 0
            elif 38.1 <= temp <= 39.0: s = 1
            elif temp >= 39.1: s = 2
            score += s
            if s > 0: details.append(f"Temp ({temp}): +{s}")
        except: pass

    # Interpretación
    risk = "Bajo"
    action = "Monitorización estándar"
    color = "green"
    
    if 0 <= score <= 4:
        risk = "Bajo"
        action = "Monitorización cada 4-6h"
        color = "green"
    elif score == 3 and any("+" in d for d in details): # Un solo parámetro con 3 puntos? (Simplificado: score 3 en un parametro es RED en NEWS, pero aqui sumamos)
        # NEWS2: Score 3 in any single parameter is Low-Medium risk requiring urgent review?
        # Simplificamos por score total:
        pass
    
    if 5 <= score <= 6:
        risk = "Medio"
        action = "Revisión Urgente (1h)"
        color = "orange"
    elif score >= 7:
        risk = "Alto"
        action = "Emergencia / UCI / SVA"
        color = "red"

    if not details:
        details.append("Todos los parámetros fisiológicos en rango normal.")

    return {
        "score": score,
        "risk": risk,
        "action": action,
        "color": color,
        "details": details
    }
