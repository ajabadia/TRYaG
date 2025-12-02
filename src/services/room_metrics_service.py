# path: src/services/room_metrics_service.py
# Creado: 2025-11-25
"""
Servicio para tracking de métricas históricas de gestión de salas.
Registra errores detectados, correcciones realizadas y estadísticas.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from db import get_database


def registrar_error_detectado(
    patient_code: str,
    sala_erronea: str,
    motivo_error: str,
    estado: str,
    nombre_completo: str = ""
) -> bool:
    """
    Registra un error detectado en el sistema de tracking.
    
    Args:
        patient_code: Código del paciente
        sala_erronea: Código de la sala con error
        motivo_error: "Sala inexistente" o "Sala inactiva"
        estado: Estado actual del flujo
        nombre_completo: Nombre del paciente
    
    Returns:
        bool: True si se registró correctamente
    """
    db = get_database()
    collection = db["room_errors_log"]
    
    error_doc = {
        "patient_code": patient_code,
        "sala_erronea": sala_erronea,
        "motivo_error": motivo_error,
        "estado": estado,
        "nombre_completo": nombre_completo,
        "detected_at": datetime.now(),
        "resolved": False,
        "resolved_at": None,
        "resolution_type": None,  # "reasignado", "rechazado", "auto_corregido"
        "new_sala": None
    }
    
    try:
        collection.insert_one(error_doc)
        return True
    except Exception:
        return False


def marcar_error_resuelto(
    patient_code: str,
    sala_erronea: str,
    resolution_type: str,
    new_sala: Optional[str] = None
) -> bool:
    """
    Marca un error como resuelto.
    
    Args:
        patient_code: Código del paciente
        sala_erronea: Sala que tenía el error
        resolution_type: "reasignado", "rechazado", "auto_corregido"
        new_sala: Nueva sala (si aplica)
    
    Returns:
        bool: True si se actualizó correctamente
    """
    db = get_database()
    collection = db["room_errors_log"]
    
    try:
        result = collection.update_one(
            {
                "patient_code": patient_code,
                "sala_erronea": sala_erronea,
                "resolved": False
            },
            {
                "$set": {
                    "resolved": True,
                    "resolved_at": datetime.now(),
                    "resolution_type": resolution_type,
                    "new_sala": new_sala
                }
            }
        )
        return result.modified_count > 0
    except Exception:
        return False


def obtener_metricas_errores(dias: int = 7) -> Dict[str, Any]:
    """
    Obtiene métricas de errores detectados en los últimos N días.
    
    Args:
        dias: Número de días hacia atrás para calcular métricas
    
    Returns:
        Dict con métricas: total, resueltos, pendientes, por tipo, etc.
    """
    db = get_database()
    collection = db["room_errors_log"]
    
    fecha_inicio = datetime.now() - timedelta(days=dias)
    
    # Total de errores en el periodo
    total_errores = collection.count_documents({"detected_at": {"$gte": fecha_inicio}})
    
    # Errores resueltos
    resueltos = collection.count_documents({
        "detected_at": {"$gte": fecha_inicio},
        "resolved": True
    })
    
    # Errores pendientes
    pendientes = collection.count_documents({
        "detected_at": {"$gte": fecha_inicio},
        "resolved": False
    })
    
    # Por motivo
    pipeline_motivo = [
        {"$match": {"detected_at": {"$gte": fecha_inicio}}},
        {"$group": {"_id": "$motivo_error", "count": {"$sum": 1}}}
    ]
    por_motivo = {item["_id"]: item["count"] for item in collection.aggregate(pipeline_motivo)}
    
    # Por tipo de resolución
    pipeline_resolucion = [
        {"$match": {"detected_at": {"$gte": fecha_inicio}, "resolved": True}},
        {"$group": {"_id": "$resolution_type", "count": {"$sum": 1}}}
    ]
    por_resolucion = {item["_id"]: item["count"] for item in collection.aggregate(pipeline_resolucion)}
    
    # Tiempo promedio de resolución (en minutos)
    pipeline_tiempo = [
        {"$match": {"detected_at": {"$gte": fecha_inicio}, "resolved": True}},
        {
            "$project": {
                "tiempo_resolucion": {
                    "$divide": [
                        {"$subtract": ["$resolved_at", "$detected_at"]},
                        60000  # Convertir ms a minutos
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "avg_tiempo": {"$avg": "$tiempo_resolucion"}
            }
        }
    ]
    tiempo_result = list(collection.aggregate(pipeline_tiempo))
    tiempo_promedio = int(tiempo_result[0]["avg_tiempo"]) if tiempo_result else 0
    
    return {
        "total_errores": total_errores,
        "resueltos": resueltos,
        "pendientes": pendientes,
        "por_motivo": por_motivo,
        "por_resolucion": por_resolucion,
        "tiempo_promedio_minutos": tiempo_promedio,
        "tasa_resolucion": round((resueltos / total_errores * 100) if total_errores > 0 else 0, 1),
        "periodo_dias": dias
    }


def obtener_historial_errores(
    limit: int = 50,
    solo_pendientes: bool = False
) -> List[Dict[str, Any]]:
    """
    Obtiene el historial de errores detectados.
    
    Args:
        limit: Número máximo de registros a devolver
        solo_pendientes: Si True, solo devuelve errores sin resolver
    
    Returns:
        Lista de errores ordenados por fecha de detección (más recientes primero)
    """
    db = get_database()
    collection = db["room_errors_log"]
    
    query = {"resolved": False} if solo_pendientes else {}
    
    errores = list(collection.find(query).sort("detected_at", -1).limit(limit))
    
    # Convertir ObjectId a string
    for error in errores:
        if '_id' in error:
            error['_id'] = str(error['_id'])
    
    return errores


def sync_errores_actuales():
    """
    Sincroniza los errores detectados actualmente con la base de datos.
    Registra solo errores nuevos que no estén ya en la BD.
    
    Returns:
        int: Número de nuevos errores registrados
    """
    from services.patient_flow_service import detectar_errores_salas
    
    errores_actuales = detectar_errores_salas()
    db = get_database()
    collection = db["room_errors_log"]
    
    nuevos_registrados = 0
    
    for error in errores_actuales:
        # Verificar si ya existe un registro sin resolver para este paciente/sala
        existe = collection.find_one({
            "patient_code": error["patient_code"],
            "sala_erronea": error["sala_erronea"],
            "resolved": False
        })
        
        if not existe:
            # Registrar nuevo error
            registrado = registrar_error_detectado(
                patient_code=error["patient_code"],
                sala_erronea=error["sala_erronea"],
                motivo_error=error["motivo_error"],
                estado=error["estado"],
                nombre_completo=error["nombre_completo"]
            )
            if registrado:
                nuevos_registrados += 1
    
    return nuevos_registrados


def get_errors_time_series(dias: int = 30) -> Dict[str, List[Any]]:
    """
    Obtiene errores agrupados por día para gráficos de series temporales.
    
    Args:
        dias: Número de días hacia atrás
    
    Returns:
        Dict con listas de 'fecha', 'total' y 'resueltos'
    """
    db = get_database()
    collection = db["room_errors_log"]
    
    fecha_inicio = datetime.now() - timedelta(days=dias)
    
    pipeline = [
        {"$match": {"detected_at": {"$gte": fecha_inicio}}},
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$detected_at"}},
                "total": {"$sum": 1},
                "resueltos": {"$sum": {"$cond": ["$resolved", 1, 0]}}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    results = list(collection.aggregate(pipeline))
    
    # Rellenar días faltantes con ceros
    fechas = []
    total = []
    resueltos = []
    
    # Crear mapa de resultados
    data_map = {item["_id"]: item for item in results}
    
    for i in range(dias):
        fecha = (fecha_inicio + timedelta(days=i)).strftime("%Y-%m-%d")
        fechas.append(fecha)
        
        if fecha in data_map:
            total.append(data_map[fecha]["total"])
            resueltos.append(data_map[fecha]["resueltos"])
        else:
            total.append(0)
            resueltos.append(0)
            
    return {
        "fecha": fechas,
        "total": total,
        "resueltos": resueltos
    }
