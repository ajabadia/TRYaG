# path: src/services/room_service.py
# Creado: 2025-11-24
"""
Servicio para gestión y consulta de salas.
"""
from typing import Dict, Any, List
from ui.config.config_loader import load_centro_config

def obtener_salas_por_tipo(tipo: str) -> List[Dict[str, Any]]:
    """Obtiene las salas activas de un tipo, añadiendo una etiqueta legible.
    Incluye plazas libres (pueden ser negativas) y datos de horario/profesional.
    """
    config = load_centro_config()
    salas = config.get('salas', [])
    filtradas = []
    for sala in salas:
        if sala.get('tipo') == tipo and sala.get('activa', True):
            total = sala.get('plazas', sala.get('capacidad_sillas', 0))
            disponibles = sala.get('plazas_disponibles', total)
            # Etiqueta que muestra disponibilidad y datos extra
            sala['label'] = (
                f"{sala.get('nombre','')} ({sala.get('codigo')}) - "
                f"Plazas libres: {disponibles}/{total}\n"
                f"Horario: {sala.get('horario','08:00‑20:00')}\n"
                f"Profesional: {sala.get('profesional','Pendiente')}"
            )
            filtradas.append(sala)
    # Ordenar de mayor a menor disponibilidad
    filtradas.sort(key=lambda s: s.get('plazas_disponibles', s.get('plazas', s.get('capacidad_sillas', 0))), reverse=True)
    return filtradas


def obtener_sala_por_codigo(codigo: str) -> Dict[str, Any] | None:
    """
    Obtiene la configuración de una sala por su código.
    
    Args:
        codigo: Código de la sala
        
    Returns:
        dict: Configuración de la sala o None si no existe
    """
    config = load_centro_config()
    salas = config.get('salas', [])
    for sala in salas:
        if sala.get('codigo') == codigo:
            return sala
    return None
