# path: src/services/room_suggestion_service.py
# Creado: 2025-11-25
"""
Servicio de auto-sugerencia de salas.
Recomienda la mejor sala alternativa basándose en múltiples criterios.
"""
from typing import List, Dict, Any, Optional
from ui.config_panel import load_centro_config
from services.patient_flow_service import obtener_vista_global_salas


def sugerir_sala_alternativa(
    sala_origen: str,
    tipo_requerido: Optional[str] = None,
    subtipo_requerido: Optional[str] = None,
    min_plazas: int = 1
) -> Optional[Dict[str, Any]]:
    """
    Sugiere la mejor sala alternativa basándose en criterios múltiples.
    
    Criterios de scoring (en orden de importancia):
    1. Sala activa (obligatorio)
    2. Tipo coincide (peso: 50)
    3. Subtipo coincide (peso: 30)
    4. Plazas disponibles > 0 (peso: 15)
    5. Menor ocupación relativa (peso: 5)
    
    Args:
        sala_origen: Código de la sala original (para excluirla)
        tipo_requerido: Tipo de sala buscado (admision, triaje, box, consulta_ingreso)
        subtipo_requerido: Subtipo buscado (espera, atencion)
        min_plazas: Plazas mínimas disponibles requeridas
    
    Returns:
        Dict con datos de la sala sugerida, o None si no hay candidatos
    """
    config = load_centro_config()
    salas = config.get('salas', [])
    vista_global = obtener_vista_global_salas()
    
    # Si no se especifica tipo, intentar inferirlo de la sala origen
    if not tipo_requerido:
        sala_origen_data = next((s for s in salas if s['codigo'] == sala_origen), None)
        if sala_origen_data:
            tipo_requerido = sala_origen_data.get('tipo')
            subtipo_requerido = sala_origen_data.get('subtipo')
    
    # Filtrar candidatos
    candidatos = []
    for sala in salas:
        # Obligatorio: sala activa y != origen
        if not sala.get('activa', True) or sala['codigo'] == sala_origen:
            continue
        
        # Calcular plazas disponibles
        total_plazas = sala.get('plazas', sala.get('capacidad_sillas', 0))
        plazas_disponibles = sala.get('plazas_disponibles', total_plazas)
        
        # Mínimo de plazas
        if plazas_disponibles < min_plazas:
            continue
        
        # Scoring
        score = 0
        reasons = []
        
        # 1. Tipo coincide (peso 50)
        if tipo_requerido and sala.get('tipo') == tipo_requerido:
            score += 50
            reasons.append(f"Mismo tipo ({tipo_requerido})")
        
        # 2. Subtipo coincide (peso 30)
        if subtipo_requerido and sala.get('subtipo') == subtipo_requerido:
            score += 30
            reasons.append(f"Mismo subtipo ({subtipo_requerido})")
        
        # 3. Plazas disponibles (peso 15 si > 0)
        if plazas_disponibles > 0:
            score += 15
            reasons.append(f"{plazas_disponibles} plazas libres")
        
        # 4. Menor ocupación relativa (peso 0-5)
        if total_plazas > 0:
            ocupacion = len(vista_global.get(sala['codigo'], []))
            ocupacion_relativa = ocupacion / total_plazas
            score += int((1 - ocupacion_relativa) * 5)
            reasons.append(f"Ocupación: {ocupacion}/{total_plazas}")
        
        candidatos.append({
            'sala': sala,
            'score': score,
            'reasons': reasons,
            'plazas_disponibles': plazas_disponibles,
            'ocupacion_actual': len(vista_global.get(sala['codigo'], []))
        })
    
    if not candidatos:
        return None
    
    # Ordenar por score (descendente)
    candidatos.sort(key=lambda x: x['score'], reverse=True)
    
    return candidatos[0]


def get_top_suggestions(
    sala_origen: str,
    tipo_requerido: Optional[str] = None,
    subtipo_requerido: Optional[str] = None,
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Obtiene las top N salas sugeridas.
    
    Args:
        sala_origen: Código de sala origen
        tipo_requerido: Tipo de sala
        subtipo_requerido: Subtipo de sala
        top_n: Número de sugerencias a devolver
    
    Returns:
        Lista ordenada de sugerencias (mejor primero)
    """
    config = load_centro_config()
    salas = config.get('salas', [])
    vista_global = obtener_vista_global_salas()
    
    # Si no se especifica tipo, intentar inferirlo
    if not tipo_requerido:
        sala_origen_data = next((s for s in salas if s['codigo'] == sala_origen), None)
        if sala_origen_data:
            tipo_requerido = sala_origen_data.get('tipo')
            subtipo_requerido = sala_origen_data.get('subtipo')
    
    # Filtrar y puntuar candidatos
    candidatos = []
    for sala in salas:
        if not sala.get('activa', True) or sala['codigo'] == sala_origen:
            continue
        
        total_plazas = sala.get('plazas', sala.get('capacidad_sillas', 0))
        plazas_disponibles = sala.get('plazas_disponibles', total_plazas)
        
        score = 0
        reasons = []
        
        if tipo_requerido and sala.get('tipo') == tipo_requerido:
            score += 50
            reasons.append(f"Tipo: {tipo_requerido}")
        
        if subtipo_requerido and sala.get('subtipo') == subtipo_requerido:
            score += 30
            reasons.append(f"Subtipo: {subtipo_requerido}")
        
        if plazas_disponibles > 0:
            score += 15
            reasons.append(f"{plazas_disponibles} plazas")
        
        if total_plazas > 0:
            ocupacion = len(vista_global.get(sala['codigo'], []))
            ocupacion_relativa = ocupacion / total_plazas
            score += int((1 - ocupacion_relativa) * 5)
            pct = int((1 - ocupacion_relativa) * 100)
            reasons.append(f"{pct}% libre")
        
        candidatos.append({
            'sala': sala,
            'score': score,
            'reasons': reasons,
            'plazas_disponibles': plazas_disponibles,
            'ocupacion_actual': len(vista_global.get(sala['codigo'], []))
        })
    
    # Ordenar y retornar top N
    candidatos.sort(key=lambda x: x['score'], reverse=True)
    return candidatos[:top_n]


def format_suggestion_display(suggestion: Dict[str, Any]) -> str:
    """
    Formatea una sugerencia para mostrar en UI.
    
    Args:
        suggestion: Dict con datos de la sugerencia
    
    Returns:
        str: Texto formateado para display
    """
    sala = suggestion['sala']
    reasons = " | ".join(suggestion['reasons'])
    
    return f"{sala['nombre']} ({sala['codigo']}) - Score: {suggestion['score']} - {reasons}"
