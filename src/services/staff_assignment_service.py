# path: src/services/staff_assignment_service.py
# Creado: 2025-11-26
"""
Servicio unificado para gestión de asignaciones de personal.
Resuelve el conflicto entre asignaciones fijas (sala_asignada) y turnos temporales.

Regla de Prioridad:
1. Si existe un turno ACTIVO para hoy/ahora -> Usar sala del turno
2. Si NO hay turno activo -> Usar sala_asignada (asignación fija)
3. Si no hay ninguno -> Usuario sin asignar
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Any
from src.db.repositories.users import get_users_repository
from src.db.repositories.turnos import get_turnos_repository


def _convert_to_time(time_value):
    """
    Convierte un valor de tiempo (string o time object) a time object.
    
    Args:
        time_value: String "HH:MM" o "HH:MM:SS", o datetime.time object
    
    Returns:
        datetime.time object
    """
    if isinstance(time_value, str):
        from datetime import time as time_class
        # Formato esperado: "HH:MM" o "HH:MM:SS"
        parts = time_value.split(':')
        return time_class(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    return time_value


def get_current_user_assignment(user_id: str, reference_datetime: Optional[datetime] = None) -> Optional[str]:
    """
    Obtiene la sala actual asignada a un usuario, considerando turnos y asignación fija.
    
    Args:
        user_id: ID del usuario
        reference_datetime: Fecha/hora de referencia (default: ahora)
    
    Returns:
        Código de sala asignada o None si no tiene asignación
    """
    if reference_datetime is None:
        reference_datetime = datetime.now()
    
    users_repo = get_users_repository()
    turnos_repo = get_turnos_repository()
    
    # 1. Buscar turno activo para esta fecha/hora
    user_shifts = turnos_repo.get_user_shifts(user_id, reference_datetime.date())
    
    # Filtrar turnos que estén activos en esta hora específica
    current_shift = None
    for shift in user_shifts:
        # Convertir horarios a datetime para comparar
        horario_inicio = _convert_to_time(shift.horario_inicio)
        horario_fin = _convert_to_time(shift.horario_fin)
        
        shift_start = datetime.combine(reference_datetime.date(), horario_inicio)
        shift_end = datetime.combine(reference_datetime.date(), horario_fin)
        
        if shift_start <= reference_datetime <= shift_end:
            current_shift = shift
            break
    
    # 2. Si hay turno activo, usar esa sala
    if current_shift:
        return current_shift.sala_code
    
    # 3. Si no hay turno, usar asignación fija
    user = users_repo.get_by_id(user_id)
    if user:
        return user.get("sala_asignada")
    
    return None


def get_room_staff(sala_code: str, reference_datetime: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Obtiene el personal asignado a una sala en un momento dado.
    Considera tanto turnos temporales como asignaciones fijas.
    
    Args:
        sala_code: Código de la sala
        reference_datetime: Fecha/hora de referencia (default: ahora)
    
    Returns:
        Lista de usuarios con información de asignación
    """
    if reference_datetime is None:
        reference_datetime = datetime.now()
    
    users_repo = get_users_repository()
    turnos_repo = get_turnos_repository()
    
    staff = []
    
    # 1. Obtener todos los usuarios activos
    all_users = users_repo.get_all_users()
    
    for user in all_users:
        if not user.get("activo", True):
            continue
        
        user_id = str(user["_id"])
        current_assignment = get_current_user_assignment(user_id, reference_datetime)
        
        if current_assignment == sala_code:
            # Determinar el tipo de asignación
            user_shifts = turnos_repo.get_user_shifts(user_id, reference_datetime.date())
            has_active_shift = any(
                shift.sala_code == sala_code and
                datetime.combine(reference_datetime.date(), _convert_to_time(shift.horario_inicio)) <= reference_datetime <= 
                datetime.combine(reference_datetime.date(), _convert_to_time(shift.horario_fin))
                for shift in user_shifts
            )
            
            staff.append({
                **user,
                "assignment_type": "turno" if has_active_shift else "fija",
                "sala_actual": current_assignment
            })
    
    return staff


def get_user_assignment_info(user_id: str, reference_datetime: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Obtiene información detallada sobre la asignación de un usuario.
    
    Args:
        user_id: ID del usuario
        reference_datetime: Fecha/hora de referencia (default: ahora)
    
    Returns:
        Dict con información de asignación
    """
    if reference_datetime is None:
        reference_datetime = datetime.now()
    
    users_repo = get_users_repository()
    turnos_repo = get_turnos_repository()
    
    user = users_repo.get_by_id(user_id)
    if not user:
        return {
            "user_id": user_id,
            "exists": False
        }
    
    # Asignación fija
    fixed_assignment = user.get("sala_asignada")
    
    # Turnos del día
    user_shifts = turnos_repo.get_user_shifts(user_id, reference_datetime.date())
    
    # Turno activo ahora
    current_shift = None
    for shift in user_shifts:
        shift_start = datetime.combine(reference_datetime.date(), _convert_to_time(shift.horario_inicio))
        shift_end = datetime.combine(reference_datetime.date(), _convert_to_time(shift.horario_fin))
        
        if shift_start <= reference_datetime <= shift_end:
            current_shift = shift
            break
    
    # Sala actual efectiva
    current_sala = current_shift.sala_code if current_shift else fixed_assignment
    
    return {
        "user_id": user_id,
        "exists": True,
        "nombre_completo": user.get("nombre_completo"),
        "fixed_assignment": fixed_assignment,
        "current_shift": {
            "sala_code": current_shift.sala_code,
            "horario_inicio": current_shift.horario_inicio,
            "horario_fin": current_shift.horario_fin
        } if current_shift else None,
        "current_sala": current_sala,
        "assignment_type": "turno" if current_shift else ("fija" if fixed_assignment else "ninguna"),
        "all_shifts_today": [
            {
                "sala_code": s.sala_code,
                "horario_inicio": s.horario_inicio,
                "horario_fin": s.horario_fin
            }
            for s in user_shifts
        ]
    }


def validate_shift_assignment(user_id: str, sala_code: str, fecha: date, 
                              horario_inicio: datetime.time, horario_fin: datetime.time) -> tuple[bool, Optional[str]]:
    """
    Valida si se puede asignar un turno a un usuario.
    
    Args:
        user_id: ID del usuario
        sala_code: Código de la sala
        fecha: Fecha del turno
        horario_inicio: Hora de inicio
        horario_fin: Hora de fin
    
    Returns:
        (es_valido, mensaje_error)
    """
    turnos_repo = get_turnos_repository()
    
    # 1. Verificar conflictos de horario con otros turnos del mismo día
    existing_shifts = turnos_repo.get_user_shifts(user_id, fecha)
    
    for shift in existing_shifts:
        # Verificar solapamiento
        if not (horario_fin <= shift.horario_inicio or horario_inicio >= shift.horario_fin):
            return False, f"Conflicto de horario con turno existente en {shift.sala_code} ({shift.horario_inicio}-{shift.horario_fin})"
    
    # 2. Advertencia si la sala del turno difiere de la asignación fija
    users_repo = get_users_repository()
    user = users_repo.get_by_id(user_id)
    
    if user and user.get("sala_asignada") and user.get("sala_asignada") != sala_code:
        # No es un error, pero es una advertencia
        return True, f"⚠️ Nota: El usuario tiene asignación fija en {user.get('sala_asignada')}, pero este turno es para {sala_code}"
    
    return True, None


def get_assignment_conflicts_report() -> List[Dict[str, Any]]:
    """
    Genera un reporte de posibles conflictos entre asignaciones fijas y turnos.
    
    Returns:
        Lista de conflictos detectados
    """
    users_repo = get_users_repository()
    turnos_repo = get_turnos_repository()
    
    conflicts = []
    today = date.today()
    
    all_users = users_repo.get_all_users()
    
    for user in all_users:
        if not user.get("activo", True):
            continue
        
        user_id = str(user["_id"])
        fixed_sala = user.get("sala_asignada")
        
        if not fixed_sala:
            continue
        
        # Obtener turnos de hoy
        today_shifts = turnos_repo.get_user_shifts(user_id, today)
        
        for shift in today_shifts:
            if shift.sala_code != fixed_sala:
                conflicts.append({
                    "user_id": user_id,
                    "nombre_completo": user.get("nombre_completo"),
                    "fixed_sala": fixed_sala,
                    "shift_sala": shift.sala_code,
                    "fecha": today,
                    "horario": f"{shift.horario_inicio}-{shift.horario_fin}",
                    "severity": "warning"  # No es error, solo advertencia
                })
    
    return conflicts
