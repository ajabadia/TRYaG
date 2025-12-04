# path: src/services/patient_flow_service.py
# Creado: 2025-11-24
# Actualizado: 2025-11-25 - Reescribiendo para modelo Log-based (Histórico de Pasos)
"""
Servicio para gestión del flujo de pacientes a través del sistema.
Implementa un modelo de Histórico de Pasos (Log-based):
- Cada movimiento es un nuevo documento en 'patient_flow'.
- Se mantiene la trazabilidad completa con 'secuencia', 'entrada', 'salida'.
- Solo un paso está 'activo=True' por paciente.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List

# Imports internos
from db import get_database
from db.models import PatientFlow
from ui.config.config_loader import load_centro_config, save_centro_config


def get_db():
    """Alias para compatibilidad."""
    return get_database()


# ---------------------------------------------------------------------------
# Gestión de Plazas (Helper)
# ---------------------------------------------------------------------------

def actualizar_plazas_sala(codigo_sala: str, delta: int) -> None:
    """Actualiza el número de plazas disponibles de una sala.
    Args:
        codigo_sala: Código identificador de la sala.
        delta: Cambio de plazas (negativo = ocupa, positivo = libera).
    """
    config = load_centro_config()
    salas = config.get('salas', [])
    found = False
    for sala in salas:
        if sala.get('codigo') == codigo_sala:
            total = sala.get('plazas', 0)
            disponibles = sala.get('plazas_disponibles', total)
            # Permitir overbooking: plazas disponibles pueden ser negativas
            nuevas = disponibles + delta
            sala['plazas_disponibles'] = nuevas
            found = True
            break
    if found:
        save_centro_config(config)


# ---------------------------------------------------------------------------
# Funciones Core de Flujo (Log-based)
# ---------------------------------------------------------------------------

def _get_sala_info(sala_code: str) -> Dict[str, str]:
    """Obtiene tipo y subtipo de una sala por su código."""
    config = load_centro_config()
    for s in config.get('salas', []):
        if s['codigo'] == sala_code:
            return {"tipo": s.get('tipo', 'desconocido'), "subtipo": s.get('subtipo', '')}
    return {"tipo": "desconocido", "subtipo": ""}


def crear_flujo_paciente(
    patient_code: str,
    sala_admision_code: str,
    motivo_rechazo: Optional[str] = None,
) -> PatientFlow:
    """Inicia un nuevo flujo para un paciente (Secuencia 1)."""
    db = get_db()
    collection = db["patient_flow"]
    
    # Verificar si ya tiene flujo activo (opcional, por seguridad)
    active = collection.find_one({"patient_code": patient_code, "activo": True})
    if active:
        # Si ya existe, lo cerramos forzosamente o lanzamos error.
        # Por ahora, cerramos el anterior.
        collection.update_one(
            {"_id": active["_id"]},
            {"$set": {"activo": False, "salida": datetime.now(), "notas": "Cierre forzoso por nuevo flujo"}}
        )
        actualizar_plazas_sala(active["sala_code"], 1) # Liberar plaza anterior

    # Generar ID de flujo único (ej: FLOW_YYYYMMDD_CODE)
    flow_id = f"FLOW_{datetime.now().strftime('%Y%m%d')}_{patient_code}"
    
    sala_info = _get_sala_info(sala_admision_code)
    
    nuevo_paso = PatientFlow(
        flow_id=flow_id,
        patient_code=patient_code,
        secuencia=1,
        sala_code=sala_admision_code,
        sala_tipo=sala_info["tipo"],
        sala_subtipo=sala_info["subtipo"],
        estado="EN_ADMISION" if not motivo_rechazo else "RECHAZADO",
        activo=True if not motivo_rechazo else False,
        entrada=datetime.now(),
        salida=datetime.now() if motivo_rechazo else None,
        motivo_rechazo=motivo_rechazo,
        notas="Inicio de flujo"
    )
    
    collection.insert_one(nuevo_paso.dict(by_alias=True, exclude={"id"}))
    
    if not motivo_rechazo:
        actualizar_plazas_sala(sala_admision_code, -1) # Ocupar plaza
        
    return nuevo_paso


def mover_paciente(
    patient_code: str,
    nueva_sala_code: str,
    nuevo_estado: str,
    notas: str = ""
) -> bool:
    """Mueve un paciente de su sala actual a una nueva (Cierra paso N, Crea paso N+1)."""
    db = get_db()
    collection = db["patient_flow"]
    
    # 1. Buscar paso actual activo
    paso_actual = collection.find_one({"patient_code": patient_code, "activo": True})
    if not paso_actual:
        return False
        
    # 2. Cerrar paso actual
    salida = datetime.now()
    entrada_anterior = paso_actual.get("entrada")
    duracion = int((salida - entrada_anterior).total_seconds() / 60) if entrada_anterior else 0
    
    collection.update_one(
        {"_id": paso_actual["_id"]},
        {
            "$set": {
                "activo": False,
                "salida": salida,
                "duracion_minutos": duracion,
                "updated_at": datetime.now()
            }
        }
    )
    
    # Liberar plaza de sala anterior
    actualizar_plazas_sala(paso_actual["sala_code"], 1)
    
    # 3. Crear nuevo paso
    sala_info = _get_sala_info(nueva_sala_code)
    
    nuevo_paso = PatientFlow(
        flow_id=paso_actual["flow_id"],
        patient_code=patient_code,
        secuencia=paso_actual["secuencia"] + 1,
        sala_code=nueva_sala_code,
        sala_tipo=sala_info["tipo"],
        sala_subtipo=sala_info["subtipo"],
        estado=nuevo_estado,
        activo=True,
        entrada=salida, # La entrada es la salida del anterior
        notas=notas
    )
    
    collection.insert_one(nuevo_paso.dict(by_alias=True, exclude={"id"}))
    
    # Ocupar plaza de nueva sala
    actualizar_plazas_sala(nueva_sala_code, -1)
    
    return True


def finalizar_flujo(patient_code: str, motivo: str, notas: str = "") -> bool:
    """Finaliza el flujo del paciente (Cierra paso actual, no crea nuevo)."""
    db = get_db()
    collection = db["patient_flow"]
    
    paso_actual = collection.find_one({"patient_code": patient_code, "activo": True})
    if not paso_actual:
        return False
        
    salida = datetime.now()
    entrada_anterior = paso_actual.get("entrada")
    duracion = int((salida - entrada_anterior).total_seconds() / 60) if entrada_anterior else 0
    
    collection.update_one(
        {"_id": paso_actual["_id"]},
        {
            "$set": {
                "activo": False,
                "salida": salida,
                "duracion_minutos": duracion,
                "estado": "FINALIZADO", # O RECHAZADO
                "motivo_rechazo": motivo, # Usamos este campo para motivo de fin
                "notas": notas,
                "updated_at": datetime.now()
            }
        }
    )
    
    actualizar_plazas_sala(paso_actual["sala_code"], 1)
    return True


# ---------------------------------------------------------------------------
# Wrappers de Compatibilidad / Lógica de Negocio Específica
# ---------------------------------------------------------------------------

def asignar_sala_triaje(patient_code: str, sala_triaje_code: str) -> bool:
    """Mueve paciente a sala de triaje (Espera o Atención según subtipo)."""
    # Normalmente se asigna a espera de triaje primero
    return mover_paciente(patient_code, sala_triaje_code, "EN_ESPERA_TRIAJE", "Asignado a triaje")

def admitir_a_triaje(patient_code: str) -> bool:
    """Mueve de Sala Espera Triaje -> Sala Atención Triaje."""
    # Requiere saber cuál es la sala de atención asociada o pasarla.
    # Como simplificación, asumimos que se pasa la sala destino en la llamada.
    # Esta función queda algo ambigua sin el destino explícito.
    # Se recomienda usar mover_paciente directamente desde la UI.
    pass 

def completar_triaje(patient_code: str, sala_destino_code: str) -> bool:
    """Mueve de Triaje -> Sala Destino (Espera Box, etc)."""
    return mover_paciente(patient_code, sala_destino_code, "DERIVADO", "Triaje completado")

def iniciar_atencion_box(patient_code: str, sala_box_code: str) -> bool:
    """Mueve de Espera -> Box Atención."""
    return mover_paciente(patient_code, sala_box_code, "EN_ATENCION", "Entrada a box")

def rechazar_paciente(patient_code: str, motivo: str) -> bool:
    """Finaliza el flujo por rechazo."""
    return finalizar_flujo(patient_code, motivo, "Rechazado por usuario")

def reassign_patient_flow(
    patient_code: str,
    new_sala_admision_code: Optional[str] = None,
    new_sala_triaje_code: Optional[str] = None,
    new_sala_espera_code: Optional[str] = None,
    new_sala_atencion_code: Optional[str] = None,
) -> bool:
    """Reasigna sala (movimiento genérico)."""
    target = new_sala_admision_code or new_sala_triaje_code or new_sala_espera_code or new_sala_atencion_code
    if not target:
        return False
        
    # Determinar estado según tipo de sala destino
    sala_info = _get_sala_info(target)
    tipo = sala_info["tipo"]
    subtipo = sala_info["subtipo"]
    
    estado = "DESCONOCIDO"
    if tipo == "admision": estado = "EN_ADMISION"
    elif tipo == "triaje": estado = "EN_TRIAJE" if subtipo == "atencion" else "EN_ESPERA_TRIAJE"
    elif tipo == "box": estado = "EN_ATENCION" if subtipo == "atencion" else "DERIVADO" # DERIVADO es espera para box
    elif tipo == "consulta_ingreso": estado = "EN_ATENCION" if subtipo == "atencion" else "DERIVADO"
    
    return mover_paciente(patient_code, target, estado, "Reasignación manual")


def save_triage_data(patient_code: str, triage_data: Dict[str, Any]) -> bool:
    """
    Guarda el registro completo de triaje en la colección 'triage_records'.
    Incluye: Datos paciente, Signos Vitales, Historia, Enfermería, Órdenes, Resultado IA.
    """
    try:
        db = get_db()
        collection = db["triage_records"]
        
        # Generar ID único
        audit_id = f"TRG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{patient_code}"
        
        record = {
            "audit_id": audit_id,
            "timestamp": datetime.now(),
            "patient_id": patient_code,
            "patient_data": triage_data.get('datos_paciente', {}),
            "vital_signs": triage_data.get('datos_paciente', {}).get('vital_signs', {}),
            "triage_result": triage_data.get('resultado', {}),
            "evaluator_id": triage_data.get('evaluator_id', 'system'),
            "prompt_type": "triage_gemini",
            "is_reevaluation": False, # TODO: Detectar si es reevaluación
            
            # Nuevos campos persistidos explícitamente
            "extended_history": {
                "ant_familiares": triage_data.get('datos_paciente', {}).get('ant_familiares'),
                "ant_fam_cardio_det": triage_data.get('datos_paciente', {}).get('ant_fam_cardio_det'),
                "ant_fam_cancer_det": triage_data.get('datos_paciente', {}).get('ant_fam_cancer_det'),
                "ant_fam_diabetes_det": triage_data.get('datos_paciente', {}).get('ant_fam_diabetes_det'),
                
                "ant_psiquiatricos": triage_data.get('datos_paciente', {}).get('ant_psiquiatricos'),
                "psy_suicidio_det": triage_data.get('datos_paciente', {}).get('psy_suicidio_det'),
                
                "ant_quirurgicos": triage_data.get('datos_paciente', {}).get('ant_quirurgicos'),
                
                "habitos_toxicos": triage_data.get('datos_paciente', {}).get('habitos_toxicos'),
                
                "nutricion_dieta": triage_data.get('datos_paciente', {}).get('nutricion_dieta'),
                "nut_disfagia_det": triage_data.get('datos_paciente', {}).get('nut_disfagia_det'),
                "nut_peso_det": triage_data.get('datos_paciente', {}).get('nut_peso_det'),
                
                "viajes_recientes": triage_data.get('datos_paciente', {}).get('viajes_recientes'),
                "exp_animales_det": triage_data.get('datos_paciente', {}).get('exp_animales_det'),
                
                "sensorial_ayudas": triage_data.get('datos_paciente', {}).get('sensorial_ayudas'),
                "sens_auditivo_det": triage_data.get('datos_paciente', {}).get('sens_auditivo_det'),
                "sens_visual_det": triage_data.get('datos_paciente', {}).get('sens_visual_det'),
                
                "dolor_cronico": triage_data.get('datos_paciente', {}).get('dolor_cronico'),
                "pain_cronico_det": triage_data.get('datos_paciente', {}).get('pain_cronico_det'),
                
                "hospitalizaciones_previas": triage_data.get('datos_paciente', {}).get('hospitalizaciones_previas'),
                "hosp_legal_det": triage_data.get('datos_paciente', {}).get('hosp_legal_det'),
                
                "situacion_legal": triage_data.get('datos_paciente', {}).get('situacion_legal'),
                "for_violencia_det": triage_data.get('datos_paciente', {}).get('for_violencia_det'),
            },
            "nursing_assessment": {
                "skin_integrity": triage_data.get('datos_paciente', {}).get('skin_integrity'),
                "skin_color": triage_data.get('datos_paciente', {}).get('skin_color'),
                "skin_edema": triage_data.get('datos_paciente', {}).get('skin_edema'),
                "fall_risk": triage_data.get('datos_paciente', {}).get('fall_risk'),
                "nut_disfagia": triage_data.get('datos_paciente', {}).get('nut_disfagia'),
                "id_bracelet": triage_data.get('datos_paciente', {}).get('id_bracelet'),
                "belongings": triage_data.get('datos_paciente', {}).get('belongings'),
            },
            "disposition_orders": {
                "order_diet": triage_data.get('datos_paciente', {}).get('order_diet'),
                "order_iv": triage_data.get('datos_paciente', {}).get('order_iv'),
                "order_labs": triage_data.get('datos_paciente', {}).get('order_labs'),
                "order_meds_stat": triage_data.get('datos_paciente', {}).get('order_meds_stat'),
                "dis_needs": triage_data.get('datos_paciente', {}).get('dis_needs'),
                "dis_barriers": triage_data.get('datos_paciente', {}).get('dis_barriers'),
            },
            "contingency_mode": triage_data.get('contingency_mode', False),
            "is_training": triage_data.get('is_training', False)
        }
        
        collection.insert_one(record)
        return True
    except Exception as e:
        print(f"Error saving triage record: {e}")
        
        # Fallback: Guardado Local (Graceful Degradation)
        try:
            import streamlit as st
            from services.contingency_service import save_triage_locally, set_contingency_mode
            
            print("⚠️ Database Error. Attempting local save...")
            
            # Reconstruir datos para el formato local
            patient_data = triage_data.get('datos_paciente', {})
            result = triage_data.get('resultado', {})
            
            save_triage_locally(patient_data, result)
            set_contingency_mode(True)
            
            st.warning("⚠️ Error de conexión con Base de Datos. El registro se ha guardado LOCALMENTE (RAM) como medida de emergencia.")
            return True # Retornamos True para que el flujo continúe (aunque sea en modo offline)
            
        except Exception as local_e:
            print(f"CRITICAL: Failed to save locally too: {local_e}")
            return False


# ---------------------------------------------------------------------------
# Consultas (Lectura)
# ---------------------------------------------------------------------------

def obtener_vista_global_salas() -> Dict[str, List[Dict[str, Any]]]:
    """Obtiene vista jerárquica de pacientes activos."""
    db = get_db()
    cursor = db["patient_flow"].find({"activo": True})
    
    flujos = list(cursor)
    vista_salas = {}

    patient_codes = [f["patient_code"] for f in flujos]
    pacientes_db = list(db["people"].find({"patient_code": {"$in": patient_codes}}))
    pacientes_map = {p["patient_code"]: p for p in pacientes_db}

    # Mapa de nombres de salas
    config = load_centro_config()
    salas_map = {s['codigo']: s.get('nombre', s['codigo']) for s in config.get('salas', [])}

    for flujo in flujos:
        sala_actual = flujo.get("sala_code")
        if not sala_actual: continue
            
        p_info = pacientes_map.get(flujo["patient_code"], {})
        
        # Nombre completo
        nombre = p_info.get('nombre', '')
        apellido1 = p_info.get('apellido1', '')
        apellido2 = p_info.get('apellido2', '')
        nombre_completo = f"{nombre} {apellido1} {apellido2}".strip()
        
        item = {
            "flow_id": flujo.get("flow_id"),
            "patient_code": flujo["patient_code"],
            "nombre_completo": nombre_completo,
            "nombre": nombre,
            "apellido1": apellido1,
            "apellido2": apellido2,
            "edad": p_info.get("edad"),
            "estado_flujo": flujo.get("estado"),
            "sala_code": sala_actual,
            "sala_nombre": salas_map.get(sala_actual, sala_actual),
            "sala_tipo": flujo.get("sala_tipo"),
            "sala_subtipo": flujo.get("sala_subtipo"),
            "created_at": flujo.get("created_at"),
            "entrada": flujo.get("entrada"),
            "wait_start": flujo.get("entrada"),
            "motivo_consulta": p_info.get("motivo_consulta", ""),
            "nivel_triaje": p_info.get("nivel_triaje", p_info.get("nivel_asignado", ""))
        }
        
        if sala_actual not in vista_salas:
            vista_salas[sala_actual] = []
        vista_salas[sala_actual].append(item)
        
    return vista_salas


def obtener_pacientes_en_espera(sala_code: str) -> List[Dict[str, Any]]:
    """Obtiene pacientes activos en una sala."""
    db = get_db()
    flujos = list(db["patient_flow"].find({"sala_code": sala_code, "activo": True}).sort("entrada", 1))
    
    # Obtener nombre de la sala
    config = load_centro_config()
    sala_nombre = next((s.get('nombre') for s in config.get('salas', []) if s['codigo'] == sala_code), sala_code)
    
    pacientes = []
    for flujo in flujos:
        p = db["people"].find_one({"patient_code": flujo["patient_code"]})
        if p:
            nombre = p.get('nombre', '')
            apellido1 = p.get('apellido1', '')
            apellido2 = p.get('apellido2', '')
            nombre_completo = f"{nombre} {apellido1} {apellido2}".strip()
            
            p_completo = {
                **p,
                "flow_id": flujo.get("flow_id"),
                "nombre_completo": nombre_completo,
                "estado_flujo": flujo.get("estado"),
                "sala_code": sala_code,
                "sala_nombre": sala_nombre,
                "sala_tipo": flujo.get("sala_tipo"),
                "sala_subtipo": flujo.get("sala_subtipo"),
                "entrada": flujo.get("entrada"),
                "created_at_flow": flujo.get("created_at"),
            }
            pacientes.append(p_completo)
    return pacientes


def obtener_flujo_activo(patient_code: str) -> Optional[Dict[str, Any]]:
    """Obtiene el paso activo actual del paciente (si existe)."""
    db = get_db()
    return db["patient_flow"].find_one({"patient_code": patient_code, "activo": True})


def clear_all_data():
    """Limpia la colección para reiniciar pruebas."""
    db = get_db()
    db["patient_flow"].delete_many({})
    return True


def detectar_errores_salas() -> List[Dict[str, Any]]:
    """Detecta pacientes en salas inexistentes o inactivas."""
    config = load_centro_config()
    # Crear set de códigos de salas activas y existentes
    salas_validas = {
        s['codigo'] for s in config.get('salas', []) 
        if s.get('activa', True)
    }
    
    db = get_db()
    # Buscar todos los flujos activos
    flujos_activos = list(db["patient_flow"].find({"activo": True}))
    
    errores = []
    patient_codes = [f["patient_code"] for f in flujos_activos]
    pacientes_db = list(db["people"].find({"patient_code": {"$in": patient_codes}}))
    pacientes_map = {p["patient_code"]: p for p in pacientes_db}

    for flujo in flujos_activos:
        sala_code = flujo.get("sala_code")
        
        # Si la sala no está en el set de válidas, es un error
        if sala_code not in salas_validas:
            p_info = pacientes_map.get(flujo["patient_code"], {})
            nombre = p_info.get('nombre', '')
            apellido1 = p_info.get('apellido1', '')
            apellido2 = p_info.get('apellido2', '')
            nombre_completo = f"{nombre} {apellido1} {apellido2}".strip()
            
            # Determinar motivo específico
            existe = any(s['codigo'] == sala_code for s in config.get('salas', []))
            motivo = "Sala inactiva" if existe else "Sala inexistente"
            
            errores.append({
                "patient_code": flujo["patient_code"],
                "nombre_completo": nombre_completo,
                "sala_erronea": sala_code,
                "estado": flujo.get("estado"),
                "motivo_error": motivo,
                "flow_id": flujo.get("flow_id"),
                "entrada": flujo.get("entrada")
            })
            
    return errores
