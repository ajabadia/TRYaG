"""
Módulo para la gestión de transcripciones de audio.
Maneja la persistencia en MongoDB.
"""
import uuid
from datetime import datetime
from db.repositories.transcriptions import get_transcriptions_repository

def get_transcription(file_md5):
    """
    Recupera la transcripción asociada a un hash MD5 desde MongoDB.
    
    Args:
        file_md5 (str): Hash MD5 del fichero de audio.
        
    Returns:
        dict: Diccionario con los datos de la transcripción o None si no existe.
    """
    repo = get_transcriptions_repository()
    try:
        # El repositorio tiene un método find_one que acepta filtros
        return repo.find_one({"file_md5": file_md5})
    except Exception as e:
        print(f"Error leyendo transcripciones de BD: {e}")
        return None

def save_transcription(file_md5, transcription_data, source="AI", spanish_user_text=None, **kwargs):
    """
    Guarda o actualiza una transcripción en MongoDB.
    
    Args:
        file_md5 (str): Hash MD5 del fichero.
        transcription_data (dict): Datos devueltos por Gemini (original_text, language_code, translated_ia_text, etc.)
        source (str): Fuente de la transcripción ('AI', 'MANUAL', 'AI_MODIFIED', 'AI_ERROR').
        spanish_user_text (str, optional): Texto modificado por el usuario.
        **kwargs: Argumentos adicionales como error_msg.
    """
    repo = get_transcriptions_repository()
    
    try:
        # Asegurar que tenemos las claves correctas del dict de entrada
        translated_ia = transcription_data.get("translated_ia_text", transcription_data.get("spanish_text", ""))
        
        # Determinar sended_text
        # Lógica: spanish_user_text > translated_ia_text > original_text
        original = transcription_data.get("original_text", "")
        
        # Si es MANUAL, el spanish_user_text es lo que cuenta
        sended = spanish_user_text if spanish_user_text else (translated_ia if translated_ia else original)

        new_entry = {
            "transcription_id": str(uuid.uuid4()),
            "timestamp": datetime.now(),
            "file_md5": file_md5,
            "original_text": original,
            "language_code": transcription_data.get("language_code", "und"),
            "language_name": transcription_data.get("language_name", "Unknown"),
            "translated_text": translated_ia,
            "translated_ia_text": translated_ia,
            "spanish_user_text": spanish_user_text if spanish_user_text is not None else "",
            "sended_text": sended,
            "source": source,
            "error_msg": kwargs.get("error_msg", "")
        }
        
        # Buscar si ya existe
        existing = repo.find_one({"file_md5": file_md5})
        
        if existing:
            # Actualizar
            repo.update(existing['_id'], new_entry)
        else:
            # Crear
            # Añadir ID numérico legacy si es necesario, o dejar que Mongo use ObjectId
            # new_entry["id"] = int(datetime.now().timestamp() * 1000) 
            repo.create(new_entry)
            
    except Exception as e:
        print(f"Error guardando transcripción en BD: {e}")
