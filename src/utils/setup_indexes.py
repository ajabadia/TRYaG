# path: src/utils/setup_indexes.py
# Creado: 2025-11-24
"""
Utilidad para crear índices en MongoDB desde la aplicación.
"""
from db.connection import get_database


def crear_indices_patient_flow():
    """
    Crea todos los índices necesarios para patient_flow.
    
    Returns:
        tuple: (éxito: bool, mensaje: str, índices: list)
    """
    try:
        db = get_database()
        collection = db.patient_flow
        
        indices_creados = []
        
        # 1. Buscar paciente activo
        collection.create_index([("patient_code", 1), ("activo", 1)], name="idx_patient_activo")
        indices_creados.append("idx_patient_activo: {patient_code: 1, activo: 1}")
        
        # 2. Historial del paciente
        collection.create_index([("flow_id", 1), ("secuencia", 1)], name="idx_flow_secuencia")
        indices_creados.append("idx_flow_secuencia: {flow_id: 1, secuencia: 1}")
        
        # 3. Pacientes en sala
        collection.create_index([("sala_code", 1), ("activo", 1), ("entrada", 1)], name="idx_sala_activo_entrada")
        indices_creados.append("idx_sala_activo_entrada: {sala_code: 1, activo: 1, entrada: 1}")
        
        # 4. Consultas por estado
        collection.create_index([("estado", 1), ("activo", 1)], name="idx_estado_activo")
        indices_creados.append("idx_estado_activo: {estado: 1, activo: 1}")
        
        # 5. Consultas por tipo de sala
        collection.create_index([("sala_tipo", 1), ("sala_subtipo", 1), ("activo", 1)], name="idx_tipo_subtipo_activo")
        indices_creados.append("idx_tipo_subtipo_activo: {sala_tipo: 1, sala_subtipo: 1, activo: 1}")
        
        # 6. Generar flow_id
        collection.create_index([("flow_id", -1)], name="idx_flow_id_desc")
        indices_creados.append("idx_flow_id_desc: {flow_id: -1}")
        
        # 7. Consultas por fecha
        collection.create_index([("created_at", 1)], name="idx_created_at")
        indices_creados.append("idx_created_at: {created_at: 1}")
        
        return True, f"✅ {len(indices_creados)} índices creados correctamente", indices_creados
        
    except Exception as e:
        return False, f"❌ Error al crear índices: {str(e)}", []


def listar_indices_patient_flow():
    """
    Lista todos los índices existentes en patient_flow.
    
    Returns:
        list: Lista de índices con sus detalles
    """
    try:
        db = get_database()
        collection = db.patient_flow
        
        indices = []
        for idx in collection.list_indexes():
            indices.append({
                "nombre": idx.get("name", ""),
                "keys": idx.get("key", {}),
                "unique": idx.get("unique", False)
            })
        
        return indices
        
    except Exception as e:
        return []


def verificar_indices_necesarios():
    """
    Verifica si todos los índices necesarios están creados.
    
    Returns:
        tuple: (todos_creados: bool, faltantes: list)
    """
    indices_necesarios = [
        "idx_patient_activo",
        "idx_flow_secuencia",
        "idx_sala_activo_entrada",
        "idx_estado_activo",
        "idx_tipo_subtipo_activo",
        "idx_flow_id_desc",
        "idx_created_at"
    ]
    
    indices_existentes = listar_indices_patient_flow()
    nombres_existentes = [idx["nombre"] for idx in indices_existentes]
    
    faltantes = [idx for idx in indices_necesarios if idx not in nombres_existentes]
    
    return len(faltantes) == 0, faltantes
