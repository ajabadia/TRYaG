# path: src/services/feedback_service.py
from datetime import datetime
from db import get_database
from bson import ObjectId
import os
import hashlib

COLLECTION_NAME = "feedback_reports"
UPLOAD_DIR = "data/feedback_uploads"

def save_feedback_report(report_data: dict, files: list = None) -> bool:
    """
    Guarda un reporte de feedback en la base de datos y sus adjuntos.
    
    Args:
        report_data (dict): Datos del reporte.
        files (list, optional): Lista de objetos tipo archivo (UploadedFile).
    
    Returns:
        bool: True si se guardó correctamente.
    """
    try:
        db = get_database()
        if db is None:
            return False
            
        collection = db[COLLECTION_NAME]
        
        # Añadir metadatos
        document = report_data.copy()
        document['timestamp'] = datetime.now()
        document['status'] = 'New'
        document['history'] = [] # Lista de cambios de estado
        document['conversation'] = [] # Lista de mensajes/respuestas
        document['unread_by_user'] = False
        document['unread_by_admin'] = True
        
        # 1. Insertar documento para obtener ID
        result = collection.insert_one(document)
        report_id = result.inserted_id
        
        # 2. Procesar archivos si existen
        if files:
            attachments = _process_files(files, str(report_id))
            
            # Actualizar documento con adjuntos
            collection.update_one(
                {"_id": report_id},
                {"$set": {"attachments": attachments}}
            )
            
        return result.acknowledged
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False

def _process_files(files, report_id_str):
    """Helper para guardar archivos y generar metadatos."""
    attachments = []
    report_dir = os.path.join(UPLOAD_DIR, report_id_str)
    os.makedirs(report_dir, exist_ok=True)
    
    for f in files:
        # Leer contenido
        f.seek(0)
        content = f.read()
        
        # Calcular MD5
        md5_hash = hashlib.md5(content).hexdigest()
        
        # Guardar archivo
        file_path = os.path.join(report_dir, f.name)
        with open(file_path, "wb") as out_file:
            out_file.write(content)
        
        attachments.append({
            "name": f.name,
            "md5": md5_hash,
            "path": file_path,
            "size": len(content),
            "timestamp": datetime.now()
        })
    return attachments

def get_feedback_reports(limit: int = 50, include_deleted: bool = False) -> list:
    """
    Recupera los últimos reportes de feedback.
    """
    try:
        db = get_database()
        if db is None:
            return []
            
        collection = db[COLLECTION_NAME]
        
        query = {}
        if not include_deleted:
            query["status"] = {"$ne": "Deleted"}
            
        cursor = collection.find(query).sort("timestamp", -1).limit(limit)
        return list(cursor)
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return []

def get_user_feedback(user_id: str) -> list:
    """Recupera los reportes de un usuario específico."""
    try:
        db = get_database()
        if db is None: return []
        collection = db[COLLECTION_NAME]
        
        cursor = collection.find({
            "user_id": user_id,
            "status": {"$ne": "Deleted"}
        }).sort("timestamp", -1)
        
        return list(cursor)
    except Exception as e:
        print(f"Error fetching user feedback: {e}")
        return []

def update_feedback_status(report_id, new_status: str, updated_by: str) -> bool:
    """Actualiza el estado de un reporte y registra el cambio."""
    try:
        db = get_database()
        collection = db[COLLECTION_NAME]
        
        # Obtener estado anterior
        doc = collection.find_one({"_id": ObjectId(report_id)})
        if not doc: return False
        
        old_status = doc.get("status", "New")
        
        if old_status == new_status: return True
        
        # Registro histórico
        history_entry = {
            "timestamp": datetime.now(),
            "user": updated_by,
            "old_status": old_status,
            "new_status": new_status
        }
        
        update_fields = {
            "status": new_status,
            "unread_by_user": True # El usuario debe saber que cambió su estado
        }
        
        result = collection.update_one(
            {"_id": ObjectId(report_id)},
            {
                "$set": update_fields,
                "$push": {"history": history_entry}
            }
        )
        return result.acknowledged
    except Exception as e:
        print(f"Error updating status: {e}")
        return False

def add_reply_to_report(report_id, message: str, user_id: str, is_admin: bool, files: list = None) -> bool:
    """Añade una respuesta al hilo de conversación."""
    try:
        db = get_database()
        collection = db[COLLECTION_NAME]
        
        attachments = []
        if files:
            attachments = _process_files(files, str(report_id))
            
        message_entry = {
            "timestamp": datetime.now(),
            "user_id": user_id,
            "message": message,
            "is_admin_reply": is_admin,
            "attachments": attachments
        }
        
        update_fields = {}
        if is_admin:
            update_fields["unread_by_user"] = True
        else:
            update_fields["unread_by_admin"] = True
            
        result = collection.update_one(
            {"_id": ObjectId(report_id)},
            {
                "$push": {"conversation": message_entry},
                "$set": update_fields
            }
        )
        return result.acknowledged
    except Exception as e:
        print(f"Error adding reply: {e}")
        return False

def check_unread_updates(user_id: str) -> int:
    """Devuelve el número de reportes con actualizaciones no leídas para el usuario."""
    try:
        db = get_database()
        collection = db[COLLECTION_NAME]
        return collection.count_documents({"user_id": user_id, "unread_by_user": True})
    except Exception:
        return 0

def mark_as_read_by_user(report_id):
    """Marca un reporte como leído por el usuario."""
    try:
        db = get_database()
        collection = db[COLLECTION_NAME]
        collection.update_one({"_id": ObjectId(report_id)}, {"$set": {"unread_by_user": False}})
    except Exception:
        pass

def soft_delete_feedback(report_id, updated_by):
    """Marca un reporte como eliminado."""
    return update_feedback_status(report_id, "Deleted", updated_by)
