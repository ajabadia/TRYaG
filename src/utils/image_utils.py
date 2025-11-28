# path: src/utils/image_utils.py
# Creado: 2025-11-21
# Última modificación: 2025-11-22
"""
Módulo con funciones de utilidad para el procesamiento de imágenes.
"""
import os
import base64
import streamlit as st
from PIL import Image
from io import BytesIO

def is_valid_base64_image_string(b64_string: str) -> bool:
    """
    Comprueba si una cadena de texto parece ser una imagen Base64 válida.
    La validación es simple: comprueba que no esté vacía y que empiece con el prefijo correcto.
    """
    if not b64_string or not isinstance(b64_string, str):
        return False
    return b64_string.startswith('data:image/')

def get_or_create_thumbnail_base64(original_image_path, md5_hash, size=(256, 256)):
    """
    Obtiene la miniatura en Base64 desde la caché. Si no existe, la crea,
    la guarda en la caché y luego la devuelve.
    """
    THUMBS_DIR = os.path.join('data', 'import_files', 'thumbs')
    # Usamos el MD5 y el tamaño para un nombre de fichero único y seguro
    thumb_filename = f"thumb_{md5_hash}_{size[0]}.b64"
    thumb_path = os.path.join(THUMBS_DIR, thumb_filename)

    # Asegurarse de que el directorio de miniaturas existe
    os.makedirs(THUMBS_DIR, exist_ok=True)

    # 1. Comprobar si la miniatura ya existe en la caché
    if os.path.exists(thumb_path):
        try:
            with open(thumb_path, "r") as f:
                cached_content = f.read()
            # 1a. Validar el contenido de la caché
            if is_valid_base64_image_string(cached_content):
                return cached_content
            else:
                # st.warning(f"Fichero de caché de miniatura corrupto detectado: {thumb_path}. Se regenerará.")
                os.remove(thumb_path) # Eliminamos el fichero corrupto
        except Exception as e:
            # st.warning(f"Error al leer o eliminar el fichero de caché {thumb_path}: {e}. Se regenerará.")
            pass

    # 2. Si no existe, la generamos
    try:
        img = Image.open(original_image_path)
        img.thumbnail(size)  # Crea la miniatura
        buffered = BytesIO()
        img.save(buffered, format=img.format or "PNG")
        base64_string = f"data:image/{img.format.lower()};base64,{base64.b64encode(buffered.getvalue()).decode()}"

        # 3. Guardamos la cadena Base64 en la caché para futuros usos
        with open(thumb_path, "w") as f:
            f.write(base64_string)
        
        return base64_string
    except Exception:
        return None # Devolvemos None si hay un error al procesar la imagen