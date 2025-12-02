# path: src/services/patient_service.py
# Creado: 2025-11-24
# Refactorizado: 2025-11-26 (Migración a Person/people y validaciones avanzadas)
"""
Servicio para gestión de pacientes en el sistema de admisión.
Utiliza la colección unificada 'people' y el modelo 'Person'.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from db import get_database
from db.models import Person, Identificacion
import re

def get_db():
    """Alias para mantener compatibilidad."""
    return get_database()

def validar_dni(dni: str) -> bool:
    """Valida un DNI español."""
    if not dni or len(dni) != 9:
        return False
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    try:
        numero = int(dni[:8])
        letra = dni[8].upper()
        return letras[numero % 23] == letra
    except (ValueError, IndexError):
        return False

def validar_nie(nie: str) -> bool:
    """Valida un NIE español."""
    if not nie or len(nie) != 9 or nie[0] not in 'XYZ':
        return False
    nie_num = nie.replace('X', '0').replace('Y', '1').replace('Z', '2')
    return validar_dni(nie_num)

def validar_pasaporte(pasaporte: str) -> bool:
    """Valida un pasaporte (formato básico)."""
    if not pasaporte:
        return False
    return 6 <= len(pasaporte) <= 9 and pasaporte.isalnum()

def validar_documento(num_doc: str, tipo: str) -> tuple[bool, str]:
    """Valida un documento de identificación según su tipo."""
    if not num_doc:
        return False, "El número de documento es obligatorio"
    
    num_doc = num_doc.strip().upper()
    
    if tipo == "DNI":
        if validar_dni(num_doc):
            return True, ""
        return False, "DNI inválido. Debe tener 8 dígitos y una letra válida"
    elif tipo == "NIE":
        if validar_nie(num_doc):
            return True, ""
        return False, "NIE inválido. Debe comenzar con X, Y o Z, seguido de 7 dígitos y una letra"
    elif tipo == "PASAPORTE":
        if validar_pasaporte(num_doc):
            return True, ""
        return False, "Pasaporte inválido. Debe tener entre 6 y 9 caracteres alfanuméricos"
    
    return False, f"Tipo de documento desconocido: {tipo}"

def generar_codigo_paciente(
    nombre: str,
    apellido1: str,
    apellido2: Optional[str],
    num_ss: Optional[str],
    num_identificacion: str
) -> str:
    """Genera un código único de paciente."""
    letra1 = nombre[0].upper()
    letra2 = apellido1[0].upper()
    letra3 = apellido2[0].upper() if apellido2 else apellido1[-1].upper()
    
    digitos_ss = ''.join(filter(str.isdigit, num_ss or ''))
    digitos_id = ''.join(filter(str.isdigit, num_identificacion or ''))
    suma = sum(int(d) for d in digitos_ss + digitos_id)
    numero = suma % 97
    
    codigo = f"{letra1}{letra2}{letra3}{numero:02d}"
    return codigo

def buscar_paciente_existente(
    num_ss: Optional[str] = None,
    num_identificacion: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Busca un paciente ACTIVO existente por SS o número de identificación."""
    db = get_db()
    
    query = {"activo": True, "$or": []}
    
    if num_ss:
        query["$or"].append({"num_ss": num_ss})
    
    if num_identificacion:
        num_identificacion = num_identificacion.upper()
        # Buscar en el array de identificaciones (solo activas)
        query["$or"].append({
            "identificaciones": {
                "$elemMatch": {
                    "value": num_identificacion,
                    "inactive_at": None
                }
            }
        })
    
    if not query["$or"]:
        return None
    
    # Buscar en people
    return db.people.find_one(query)

def _check_duplicate_identifications(
    db, 
    tipo_identificacion: str, 
    num_identificacion: str, 
    exclude_person_id=None
) -> Optional[str]:
    """
    Verifica si existe otra persona con la misma identificación activa.
    Retorna un mensaje de advertencia si existe, o None si no.
    """
    query = {
        "activo": True,
        "identificaciones": {
            "$elemMatch": {
                "type": tipo_identificacion,
                "value": num_identificacion,
                "inactive_at": None
            }
        }
    }
    
    if exclude_person_id:
        query["_id"] = {"$ne": exclude_person_id}
        
    duplicate = db.people.find_one(query)
    
    if duplicate:
        nombre = f"{duplicate.get('nombre')} {duplicate.get('apellido1')}"
        return f"ADVERTENCIA: La identificación {tipo_identificacion} {num_identificacion} ya está asignada a {nombre} (ID: {duplicate.get('patient_code')})."
    
    return None

def crear_paciente(
    nombre: str,
    apellido1: str,
    apellido2: Optional[str],
    fecha_nacimiento: datetime,
    num_ss: Optional[str],
    num_identificacion: str,
    tipo_identificacion: str,
    contact_info: Optional[List[Dict[str, Any]]] = None,
    insurance_info: Optional[Dict[str, Any]] = None,
    gender: Optional[str] = None,
    usuario: str = "admin",
    force_create: bool = False
) -> tuple[Dict[str, Any], Optional[str]]:
    """
    Crea un nuevo paciente (Persona) en el sistema.
    Retorna (person_data, warning_message).
    Si hay warning y force_create es False, lanza excepción o retorna warning.
    """
    db = get_db()
    num_identificacion = num_identificacion.upper()
    
    # 1. Verificar duplicados exactos (SS o ID) en el sistema (Bloqueante si es la misma persona lógica, pero aquí asumimos creación nueva)
    # Si existe alguien con el mismo SS, bloqueamos (el SS es único)
    if num_ss:
        existente_ss = db.people.find_one({"activo": True, "num_ss": num_ss})
        if existente_ss:
            raise ValueError(f"Ya existe un paciente con el número de SS {num_ss}")

    # 2. Verificar duplicidad de identificación en OTRAS personas (Advertencia)
    warning = _check_duplicate_identifications(db, tipo_identificacion, num_identificacion)
    
    if warning and not force_create:
        # Si no se fuerza, retornamos None y el warning para que el UI pida confirmación
        return None, warning
    
    # Generar código único
    codigo = generar_codigo_paciente(nombre, apellido1, apellido2, num_ss, num_identificacion)
    
    intentos = 0
    while db.people.find_one({"patient_code": codigo}) and intentos < 10:
        import random
        codigo = f"{codigo[:3]}{random.randint(0, 99):02d}"
        intentos += 1
    
    # Crear documento Person
    identificacion = Identificacion(
        type=tipo_identificacion, 
        value=num_identificacion,
        created_at=datetime.now(),
        inactive_at=None
    )
    
    person_data = {
        "patient_code": codigo,
        "nombre": nombre.strip(),
        "apellido1": apellido1.strip(),
        "apellido2": apellido2.strip() if apellido2 else None,
        "fecha_nacimiento": fecha_nacimiento,
        "gender": gender,
        "num_ss": num_ss,
        "identificaciones": [identificacion],
        "contact_info": contact_info or [],
        "insurance_info": insurance_info or None,
        "activo": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    person = Person(**person_data)
    result = db.people.insert_one(person.model_dump(by_alias=True, exclude={"id"}))
    
    person_data["_id"] = result.inserted_id
    return person_data, warning

def obtener_paciente_por_codigo(patient_code: str) -> Optional[Dict[str, Any]]:
    """Obtiene un paciente por su código."""
    db = get_db()
    return db.people.find_one({"patient_code": patient_code.upper()})

def calcular_edad(fecha_nacimiento: datetime) -> int:
    """Calcula la edad en años."""
    if not fecha_nacimiento:
        return 0
    hoy = datetime.now()
    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad

def marcar_paciente_inactivo(patient_code: str, usuario: str = "admin") -> bool:
    """Marca un paciente como inactivo."""
    db = get_db()
    result = db.people.update_one(
        {"patient_code": patient_code.upper(), "activo": True},
        {
            "$set": {
                "activo": False,
                "updated_at": datetime.now()
            }
        }
    )
    return result.modified_count > 0

def actualizar_paciente_con_auditoria(
    patient_code_anterior: str,
    nombre: str,
    apellido1: str,
    apellido2: Optional[str],
    fecha_nacimiento: datetime,
    num_ss: Optional[str],
    num_identificacion: str,
    tipo_identificacion: str,
    contact_info: Optional[List[Dict[str, Any]]] = None,
    insurance_info: Optional[Dict[str, Any]] = None,
    gender: Optional[str] = None,
    usuario: str = "admin",
    force_update: bool = False
) -> tuple[Dict[str, Any], Optional[str]]:
    """
    Actualiza los datos de un paciente (inactiva anterior, crea nuevo).
    Retorna (person_data, warning).
    """
    db = get_db()
    num_identificacion = num_identificacion.upper()
    
    paciente_anterior = db.people.find_one({
        "patient_code": patient_code_anterior.upper(),
        "activo": True
    })
    
    if not paciente_anterior:
        raise ValueError("El paciente anterior no existe o ya está inactivo")
    
    # Verificar duplicidad de identificación en OTRAS personas
    warning = _check_duplicate_identifications(db, tipo_identificacion, num_identificacion, exclude_person_id=paciente_anterior["_id"])
    
    if warning and not force_update:
        return None, warning

    # Verificar duplicidad interna (mismo valor activo en la misma persona)
    # En este caso de "actualización completa" (crear nuevo registro), verificamos contra el anterior
    # Pero como vamos a inactivar el anterior, la colisión interna no es relevante en el nuevo objeto,
    # sino que debemos asegurar que no estamos añadiendo una ID que ya tenía pero con otro tipo (si eso fuera posible)
    # La regla: "una persona no tiene dos values de identificaciones iguales activos".
    # Como aquí estamos creando un objeto nuevo con UNA sola identificación principal (por simplificación del flujo actual),
    # no hay conflicto interno.
    # TODO: Si en el futuro soportamos editar la lista de identificaciones, habrá que validar uniqueness en la lista.

    marcar_paciente_inactivo(patient_code_anterior, usuario)
    
    # Determinar si mantenemos código o generamos nuevo
    # Buscamos la identificación principal anterior para comparar
    old_ids = paciente_anterior.get("identificaciones", [])
    old_main_id = next((i for i in old_ids if i.get("inactive_at") is None), None)
    old_val = old_main_id["value"] if old_main_id else paciente_anterior.get("identification_number") # Fallback legacy
    
    if (num_ss == paciente_anterior.get("num_ss") and 
        num_identificacion == old_val):
        nuevo_codigo = patient_code_anterior.upper()
    else:
        nuevo_codigo = generar_codigo_paciente(nombre, apellido1, apellido2, num_ss, num_identificacion)
    
    intentos = 0
    while db.people.find_one({"patient_code": nuevo_codigo, "activo": True}) and intentos < 10:
        import random
        nuevo_codigo = f"{nuevo_codigo[:3]}{random.randint(0, 99):02d}"
        intentos += 1
    
    identificacion = Identificacion(
        type=tipo_identificacion, 
        value=num_identificacion,
        created_at=datetime.now(),
        inactive_at=None
    )
    
    # Preservar historial de identificaciones si fuera necesario (en este modelo de "nuevo registro" se suele reiniciar,
    # pero si queremos trazar historia, deberíamos copiar las IDs antiguas marcándolas como inactivas si cambiaron.
    # Por simplicidad y siguiendo el patrón de "inmutabilidad por versión", creamos limpio.)
    
    person_data = {
        "patient_code": nuevo_codigo,
        "nombre": nombre.strip(),
        "apellido1": apellido1.strip(),
        "apellido2": apellido2.strip() if apellido2 else None,
        "fecha_nacimiento": fecha_nacimiento,
        "gender": gender,
        "num_ss": num_ss,
        "identificaciones": [identificacion],
        "contact_info": contact_info or [],
        "insurance_info": insurance_info or None,
        "activo": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    person = Person(**person_data)
    result = db.people.insert_one(person.model_dump(by_alias=True, exclude={"id"}))
    
    person_data["_id"] = result.inserted_id
    return person_data, warning

def listar_pacientes(limite: int = 100, skip: int = 0, solo_activos: bool = True) -> list[Dict[str, Any]]:
    """Lista pacientes registrados (Personas con patient_code)."""
    db = get_db()
    
    query = {"patient_code": {"$ne": None}}
    if solo_activos:
        query["activo"] = True
    
    return list(db.people.find(query).sort("created_at", -1).limit(limite).skip(skip))
