# path: src/services/queue_manager.py
from datetime import datetime
from typing import List, Dict, Any

def calculate_priority_score(patient: Dict[str, Any]) -> int:
    """
    Calcula un score de prioridad para ordenamiento.
    Menor score = Mayor prioridad.
    
    Lógica:
    - Nivel 1 (Rojo): 1000
    - Nivel 2 (Naranja): 2000
    - Nivel 3 (Amarillo): 3000
    - Nivel 4 (Verde): 4000
    - Nivel 5 (Azul/Blanco): 5000
    
    Se resta el tiempo de espera en minutos para desempatar (FIFO dentro del mismo nivel).
    """
    # Mapeo de niveles a base score
    level_map = {
        "Nivel I": 1000, "Rojo": 1000, "Red": 1000,
        "Nivel II": 2000, "Naranja": 2000, "Orange": 2000,
        "Nivel III": 3000, "Amarillo": 3000, "Yellow": 3000,
        "Nivel IV": 4000, "Verde": 4000, "Green": 4000,
        "Nivel V": 5000, "Azul": 5000, "Blue": 5000
    }
    
    # Obtener nivel del paciente (normalizar string)
    triage_level = patient.get('nivel_triaje', 'Nivel V')
    # Intentar buscar substring clave (ordenar por longitud descendente para evitar falsos positivos como 'Nivel I' en 'Nivel IV')
    base_score = 5000
    sorted_keys = sorted(level_map.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        if key.lower() in str(triage_level).lower():
            base_score = level_map[key]
            break
            
    # Calcular tiempo de espera
    wait_start = patient.get('wait_start')
    wait_minutes = 0
    if wait_start:
        if isinstance(wait_start, str):
            try:
                wait_start = datetime.fromisoformat(wait_start)
            except ValueError:
                wait_start = datetime.now() # Fallback
        
        wait_minutes = int((datetime.now() - wait_start).total_seconds() / 60)
        
    # Score final: Base - Minutos (para que más tiempo de espera reduzca el score y suba prioridad)
    # Ejemplo: Rojo (1000) con 10 min espera = 990. Rojo con 20 min = 980 (Va antes).
    return base_score - wait_minutes

def sort_queue(patients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ordena la lista de pacientes por prioridad."""
    return sorted(patients, key=calculate_priority_score)

def get_wait_time_alert(patient: Dict[str, Any]) -> str:
    """
    Determina el nivel de alerta por tiempo de espera.
    Returns: 'normal', 'warning', 'critical'
    """
    triage_level = str(patient.get('nivel_triaje', '')).lower()
    wait_start = patient.get('wait_start')
    
    if not wait_start:
        return 'normal'
        
    if isinstance(wait_start, str):
        try:
            wait_start = datetime.fromisoformat(wait_start)
        except ValueError:
            return 'normal'

    wait_min = (datetime.now() - wait_start).total_seconds() / 60
    
    # Umbrales (en minutos)
    thresholds = {
        'rojo': {'warn': 5, 'crit': 10},     # Nivel I
        'naranja': {'warn': 15, 'crit': 30}, # Nivel II
        'amarillo': {'warn': 45, 'crit': 60},# Nivel III
        'verde': {'warn': 90, 'crit': 120},  # Nivel IV
        'azul': {'warn': 120, 'crit': 240}   # Nivel V
    }
    
    # Detectar color usando mapeo ordenado por longitud de clave
    color_map = {
        'rojo': 'rojo', 'nivel i': 'rojo',
        'naranja': 'naranja', 'nivel ii': 'naranja',
        'amarillo': 'amarillo', 'nivel iii': 'amarillo',
        'verde': 'verde', 'nivel iv': 'verde',
        'azul': 'azul', 'nivel v': 'azul'
    }
    
    color_key = 'azul' # Default
    sorted_keys = sorted(color_map.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        if key in triage_level:
            color_key = color_map[key]
            break
            
    limits = thresholds[color_key]
    
    if wait_min >= limits['crit']:
        return 'critical'
    elif wait_min >= limits['warn']:
        return 'warning'
    
    return 'normal'
