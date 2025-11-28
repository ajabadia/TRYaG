# path: src/utils/file_utils.py
# Creado: 2025-11-21
# Última modificación: 2025-11-21
"""
Módulo con funciones de utilidad para el manejo de archivos generales.
"""
import os
import base64

def get_file_extension(filename: str) -> str:
    """Devuelve la extensión del archivo en minúsculas sin el punto."""
    if not filename:
        return ""
    return os.path.splitext(filename)[1].lower().lstrip('.')

def is_supported_media_file(extension: str) -> bool:
    """Comprueba si la extensión corresponde a un tipo de medio soportado por el visor."""
    supported_types = [
        'png', 'jpg', 'jpeg', 'gif', 'webp', 
        'mp3', 'wav', 'ogg', 
        'mp4', 'webm', 
        'pdf'
    ]
    return extension.lower() in supported_types

def get_file_base64(file_path: str) -> str:
    """Lee un archivo y devuelve su contenido codificado en base64."""
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Error al leer archivo {file_path}: {e}")
        return None
