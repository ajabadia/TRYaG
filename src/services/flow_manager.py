# path: src/services/flow_manager.py
# Creado: 2025-11-24
"""
Gestor del nuevo sistema de flujo de pacientes.
Implementa el modelo de registro por sala con flow_id único.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from db.connection import get_database


def generar_flow_id() -> str:
    """
    Genera un ID único para un nuevo flujo de paciente.
    Formato: FLOW_YYYYMMDD_NNN
    
    Returns:
        str: ID único del flujo (ej: FLOW_20241124_001)
    """
    db = get_database()
    hoy = datetime.now().strftime("%Y%m%d")
    
    # Buscar el último flow_id del día
    ultimo_flow = db.patient_flow.find_one(
        {"flow_id": {"$regex": f"^FLOW_{hoy}_"}},
        sort=[("flow_id", -1)]
    )
    
    if ultimo_flow:
        # Extraer el número y sumar 1
        ultimo_num = int(ultimo_flow["flow_id"].split("_")[-1])
        nuevo_num = ultimo_num + 1
    else:
        nuevo_num = 1
    
    return f"FLOW_{hoy}_{nuevo_num:03d}"


def crear_nuevo_flujo(
    patient_code: str,
    sala_admision_code: str,
    sala_tipo: str = "admision",
    sala_subtipo: str = "atencion",
    notas: str = "",
    usuario: str = ""
) -> str:
    """
    Crea un nuevo flujo de paciente con el primer registro en admisión.
    
    Args:
        patient_code: Código del paciente
        sala_admision_code: Código de la sala de admisión
        sala_tipo: Tipo de sala (default: admision)
        sala_subtipo: Subtipo de sala (default: atencion)
        notas: Notas adicionales
        usuario: Usuario que crea el flujo
    
    Returns:
        str: flow_id generado
    """
    db = get_database()
    flow_id = generar_flow_id()
    now = datetime.utcnow()
    
    # Crear primer registro
    registro = {
        "flow_id": flow_id,
        "patient_code": patient_code,
        "secuencia": 1,
        
        "sala_code": sala_admision_code,
        "sala_tipo": sala_tipo,
        "sala_subtipo": sala_subtipo,
        
        "estado": "EN_ADMISION",
        "activo": True,  # Primer registro activo
        
        "entrada": now,
        "salida": None,
        "duracion_minutos": None,
        
        "notas": notas,
        "usuario": usuario,
        
        "created_at": now,
        "updated_at": now,
    }
    
    db.patient_flow.insert_one(registro)
    return flow_id


def obtener_registro_activo(patient_code: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene el registro activo actual de un paciente.
    
    Args:
        patient_code: Código del paciente
    
    Returns:
        dict: Registro activo o None si no existe
    """
    db = get_database()
    return db.patient_flow.find_one({
        "patient_code": patient_code,
        "activo": True
    })


def obtener_historial_paciente(
    patient_code: str = None,
    flow_id: str = None
) -> List[Dict[str, Any]]:
    """
    Obtiene el historial completo de un paciente ordenado por secuencia.
    
    Args:
        patient_code: Código del paciente (opcional)
        flow_id: ID del flujo (opcional)
    
    Returns:
        list: Lista de registros ordenados por secuencia
    """
    db = get_database()
    
    if flow_id:
        query = {"flow_id": flow_id}
    elif patient_code:
        # Obtener flow_id del registro activo
        registro_activo = obtener_registro_activo(patient_code)
        if not registro_activo:
            return []
        query = {"flow_id": registro_activo["flow_id"]}
    else:
        return []
    
    return list(db.patient_flow.find(query).sort("secuencia", 1))


def obtener_pacientes_en_sala(
    sala_code: str,
    solo_activos: bool = True
) -> List[Dict[str, Any]]:
    """
    Obtiene todos los pacientes en una sala específica.
    
    Args:
        sala_code: Código de la sala
        solo_activos: Si True, solo devuelve registros activos
    
    Returns:
        list: Lista de registros de pacientes en la sala
    """
    db = get_database()
    
    query = {"sala_code": sala_code}
    if solo_activos:
        query["activo"] = True
    
    return list(db.patient_flow.find(query).sort("entrada", 1))


def mover_paciente_a_sala(
    patient_code: str,
    sala_destino_code: str,
    sala_destino_tipo: str,
    sala_destino_subtipo: str,
    nuevo_estado: str,
    notas: str = "",
    usuario: str = ""
) -> Tuple[bool, str]:
    """
    Mueve un paciente de su sala actual a una nueva sala.
    
    Args:
        patient_code: Código del paciente
        sala_destino_code: Código de la sala destino
        sala_destino_tipo: Tipo de la sala destino
        sala_destino_subtipo: Subtipo de la sala destino
        nuevo_estado: Nuevo estado del paciente
        notas: Notas del movimiento
        usuario: Usuario que realiza el movimiento
    
    Returns:
        tuple: (éxito: bool, mensaje: str)
    """
    db = get_database()
    now = datetime.utcnow()
    
    # 1. Obtener registro activo
    registro_actual = obtener_registro_activo(patient_code)
    if not registro_actual:
        return False, "No se encontró registro activo del paciente"
    
    # 2. Validar movimiento
    valido, mensaje = validar_movimiento(
        registro_actual["sala_tipo"],
        registro_actual["sala_subtipo"],
        sala_destino_tipo,
        sala_destino_subtipo
    )
    if not valido:
        return False, mensaje
    
    # 3. Cerrar registro actual
    duracion = int((now - registro_actual["entrada"]).total_seconds() / 60)
    
    db.patient_flow.update_one(
        {"_id": registro_actual["_id"]},
        {
            "$set": {
                "salida": now,
                "duracion_minutos": duracion,
                "activo": False,
                "updated_at": now
            }
        }
    )
    
    # 4. Crear nuevo registro
    nuevo_registro = {
        "flow_id": registro_actual["flow_id"],
        "patient_code": patient_code,
        "secuencia": registro_actual["secuencia"] + 1,
        
        "sala_code": sala_destino_code,
        "sala_tipo": sala_destino_tipo,
        "sala_subtipo": sala_destino_subtipo,
        
        "estado": nuevo_estado,
        "activo": True,
        
        "entrada": now,
        "salida": None,
        "duracion_minutos": None,
        
        "notas": notas,
        "usuario": usuario,
        
        "created_at": now,
        "updated_at": now,
    }
    
    db.patient_flow.insert_one(nuevo_registro)
    
    return True, f"Paciente movido a {sala_destino_code}"


def validar_movimiento(
    sala_origen_tipo: str,
    sala_origen_subtipo: str,
    sala_destino_tipo: str,
    sala_destino_subtipo: str
) -> Tuple[bool, str]:
    """
    Valida si un movimiento entre salas es permitido según las reglas del flujo.
    
    Reglas:
    - Solo se puede ir de ESPERA → ATENCIÓN (mismo tipo o siguiente)
    - Solo se puede ir de ATENCIÓN → ESPERA (siguiente tipo)
    - No se pueden saltar tipos
    
    Args:
        sala_origen_tipo: Tipo de sala origen
        sala_origen_subtipo: Subtipo de sala origen
        sala_destino_tipo: Tipo de sala destino
        sala_destino_subtipo: Subtipo de sala destino
    
    Returns:
        tuple: (válido: bool, mensaje: str)
    """
    # Orden de tipos
    orden_tipos = ["admision", "triaje", "boxes", "ingreso"]
    
    try:
        idx_origen = orden_tipos.index(sala_origen_tipo)
        idx_destino = orden_tipos.index(sala_destino_tipo)
    except ValueError:
        return False, "Tipo de sala no válido"
    
    # Regla 1: De ATENCIÓN → ESPERA (siguiente tipo)
    if sala_origen_subtipo == "atencion" and sala_destino_subtipo == "espera":
        if idx_destino == idx_origen + 1:
            return True, "Movimiento válido"
        else:
            return False, "Solo se puede avanzar al siguiente tipo de sala"
    
    # Regla 2: De ESPERA → ATENCIÓN (mismo tipo)
    if sala_origen_subtipo == "espera" and sala_destino_subtipo == "atencion":
        if idx_destino == idx_origen:
            return True, "Movimiento válido"
        else:
            return False, "Solo se puede atender en el mismo tipo de sala"
    
    # Regla 3: Admisión puede ir directamente a espera de triaje
    if sala_origen_tipo == "admision" and sala_destino_tipo == "triaje" and sala_destino_subtipo == "espera":
        return True, "Movimiento válido desde admisión"
    
    # Regla 4: Se puede volver atrás entre salas de espera
    if sala_origen_subtipo == "espera" and sala_destino_subtipo == "espera":
        if idx_destino < idx_origen:
            return True, "Movimiento hacia atrás permitido"
    
    return False, f"Movimiento no permitido de {sala_origen_tipo}/{sala_origen_subtipo} a {sala_destino_tipo}/{sala_destino_subtipo}"


def rechazar_paciente(
    patient_code: str,
    motivo: str,
    usuario: str = ""
) -> Tuple[bool, str]:
    """
    Rechaza un paciente y finaliza su flujo.
    
    Args:
        patient_code: Código del paciente
        motivo: Motivo del rechazo
        usuario: Usuario que rechaza
    
    Returns:
        tuple: (éxito: bool, mensaje: str)
    """
    db = get_database()
    now = datetime.utcnow()
    
    # Obtener registro activo
    registro_actual = obtener_registro_activo(patient_code)
    if not registro_actual:
        return False, "No se encontró registro activo del paciente"
    
    # Cerrar registro con estado RECHAZADO
    duracion = int((now - registro_actual["entrada"]).total_seconds() / 60)
    
    db.patient_flow.update_one(
        {"_id": registro_actual["_id"]},
        {
            "$set": {
                "salida": now,
                "duracion_minutos": duracion,
                "activo": False,
                "estado": "RECHAZADO",
                "notas": f"{registro_actual.get('notas', '')} | RECHAZADO: {motivo}",
                "updated_at": now
            }
        }
    )
    
    return True, "Paciente rechazado correctamente"


def finalizar_flujo(
    patient_code: str,
    tipo_finalizacion: str,
    notas: str = "",
    usuario: str = ""
) -> Tuple[bool, str]:
    """
    Finaliza el flujo de un paciente con un estado final.
    
    Args:
        patient_code: Código del paciente
        tipo_finalizacion: Tipo de finalización (ALTA_CURADO, ALTA_DERIVADO_AP, INGRESADO, etc.)
        notas: Notas adicionales
        usuario: Usuario que finaliza
    
    Returns:
        tuple: (éxito: bool, mensaje: str)
    """
    db = get_database()
    now = datetime.utcnow()
    
    # Obtener registro activo
    registro_actual = obtener_registro_activo(patient_code)
    if not registro_actual:
        return False, "No se encontró registro activo del paciente"
    
    # Cerrar registro con estado final
    duracion = int((now - registro_actual["entrada"]).total_seconds() / 60)
    
    db.patient_flow.update_one(
        {"_id": registro_actual["_id"]},
        {
            "$set": {
                "salida": now,
                "duracion_minutos": duracion,
                "activo": False,
                "estado": tipo_finalizacion,
                "notas": f"{registro_actual.get('notas', '')} | {notas}",
                "updated_at": now
            }
        }
    )
    
    return True, f"Flujo finalizado: {tipo_finalizacion}"


def calcular_tiempos_paciente(patient_code: str) -> Dict[str, Any]:
    """
    Calcula los tiempos totales de un paciente en el sistema.
    
    Args:
        patient_code: Código del paciente
    
    Returns:
        dict: Diccionario con tiempos calculados
    """
    historial = obtener_historial_paciente(patient_code=patient_code)
    
    if not historial:
        return {
            "tiempo_total_minutos": 0,
            "tiempo_espera_minutos": 0,
            "tiempo_atencion_minutos": 0,
            "num_movimientos": 0
        }
    
    tiempo_total = 0
    tiempo_espera = 0
    tiempo_atencion = 0
    
    for registro in historial:
        duracion = registro.get("duracion_minutos", 0) or 0
        tiempo_total += duracion
        
        if registro.get("sala_subtipo") == "espera":
            tiempo_espera += duracion
        elif registro.get("sala_subtipo") == "atencion":
            tiempo_atencion += duracion
    
    return {
        "tiempo_total_minutos": tiempo_total,
        "tiempo_espera_minutos": tiempo_espera,
        "tiempo_atencion_minutos": tiempo_atencion,
        "num_movimientos": len(historial)
    }
