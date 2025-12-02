# path: src/services/feedback_service.py
from datetime import datetime
from db import get_database

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
        
        # 1. Insertar documento para obtener ID
        result = collection.insert_one(document)
        report_id = result.inserted_id
        
        # 2. Procesar archivos si existen
        if files:
            attachments = []
            report_dir = os.path.join(UPLOAD_DIR, str(report_id))
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
                    "size": len(content)
                })
            
            # Actualizar documento con adjuntos
            collection.update_one(
                {"_id": report_id},
                {"$set": {"attachments": attachments}}
            )
            
        return result.acknowledged
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False

def get_feedback_reports(limit: int = 50) -> list:
    """
    Recupera los últimos reportes de feedback.
    """
    try:
        db = get_database()
        if db is None:
            return []
            
        collection = db[COLLECTION_NAME]
        
        cursor = collection.find().sort("timestamp", -1).limit(limit)
        return list(cursor)
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return []
