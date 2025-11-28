"""
Módulo para la gestión de ficheros importados (imágenes, documentos, etc.).

Se encarga de calcular hashes, guardar los ficheros en el directorio de datos
y registrar la información en MongoDB.
"""
import os
import hashlib
import shutil
from datetime import datetime
from src.db.repositories.files import get_file_imports_repository

IMPORT_FILES_DIR = os.path.join('data', 'import_files')
RECORDED_FILES_DIR = os.path.join('data', 'recorded_files')
TEMP_DIR = 'temp'

def calculate_md5(file_object):
    """Calcula el hash MD5 de un objeto de fichero."""
    hash_md5 = hashlib.md5()
    # Rebobinamos el fichero para asegurarnos de leerlo desde el principio
    file_object.seek(0)
    for chunk in iter(lambda: file_object.read(4096), b""):
        hash_md5.update(chunk)
    # Rebobinamos de nuevo por si se necesita leer después
    file_object.seek(0)
    return hash_md5.hexdigest()

def process_and_log_files(audit_id, uploaded_files, ai_selected_files_names, source_type="imported"):
    """
    Procesa una lista de ficheros: los guarda y registra en MongoDB.

    Args:
        audit_id (str/ObjectId): El ID del registro de auditoría padre.
        uploaded_files (list): Lista de objetos UploadedFile de Streamlit o Wrappers.
        ai_selected_files_names (list): Lista de nombres de los ficheros enviados a la IA.
        source_type (str): 'imported' para ficheros subidos, 'recorded' para grabaciones.
    """
    if not uploaded_files:
        return

    target_dir = IMPORT_FILES_DIR if source_type == "imported" else RECORDED_FILES_DIR
    os.makedirs(target_dir, exist_ok=True)
    
    log_entries = []
    for file in uploaded_files:
        md5_hash = calculate_md5(file)
        
        # Determinar extensión y nombre
        if hasattr(file, 'name'):
            file_name = file.name
            _, file_type = os.path.splitext(file_name)
            file_type = file_type.lstrip('.')
        else:
            file_type = "wav" 
            file_name = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        if not file_type and source_type == "recorded":
             file_type = "wav"

        new_filename = f"{md5_hash}.{file_type}"
        save_path = os.path.join(target_dir, new_filename)

        # Guardar el fichero
        # Si tiene temp_path, copiamos desde allí
        if hasattr(file, 'temp_path') and file.temp_path and os.path.exists(file.temp_path):
            shutil.copy2(file.temp_path, save_path)
        else:
            # Fallback: escribir desde buffer
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())

        log_entries.append({
            "audit_id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "file_name": file_name,
            "file_md5": md5_hash,
            "file_type": file_type,
            "sended_IA": file_name in ai_selected_files_names,
            "source_type": source_type
        })

    # Guardar en MongoDB
    files_repo = get_file_imports_repository()
    
    for entry in log_entries:
        try:
            files_repo.create({
                "file_id": entry["file_md5"],
                "audit_id": str(entry["audit_id"]),
                "timestamp": datetime.fromisoformat(entry["timestamp"]),
                "file_name": entry["file_name"],
                "file_type": entry["file_type"],
                "sended_IA": entry["sended_IA"],
                "source_type": entry["source_type"]
            })
        except Exception as e:
            print(f"Error guardando archivo en BD: {e}")

def save_file_to_temp(file_obj, default_ext=".wav"):
    """
    Guarda temporalmente un fichero en el directorio TEMP.
    Devuelve info incluyendo el path temporal.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    md5_hash = calculate_md5(file_obj)
    
    # Intentar deducir extensión
    ext = default_ext
    if hasattr(file_obj, 'name'):
        _, ext = os.path.splitext(file_obj.name)
        if not ext:
            ext = default_ext
            
    new_filename = f"{md5_hash}{ext}"
    save_path = os.path.join(TEMP_DIR, new_filename)
    
    # Solo guardar si no existe, para ahorrar escrituras
    if not os.path.exists(save_path):
        with open(save_path, "wb") as f:
            f.write(file_obj.getbuffer())
        
    return {
        "name": file_obj.name if hasattr(file_obj, 'name') else f"file_{md5_hash[:8]}{ext}",
        "path": save_path,
        "type": ext.lstrip('.'),
        "size": file_obj.getbuffer().nbytes,
        "content": file_obj
    }

def cleanup_temp_files(files):
    """
    Elimina los ficheros temporales asociados a los objetos de archivo pasados.
    Se espera que los objetos tengan un atributo 'temp_path' si tienen un temporal asociado.
    """
    for f in files:
        # Verificamos si tiene 'path' (que usamos en save_recorded_file_temp) y si está en TEMP_DIR
        if hasattr(f, 'path') and TEMP_DIR in f.path and os.path.exists(f.path):
            try:
                os.remove(f.path)
            except Exception as e:
                print(f"Error eliminando temporal {f.path}: {e}")
        # O si usamos un atributo específico 'temp_path' en el wrapper
        elif hasattr(f, 'temp_path') and f.temp_path and os.path.exists(f.temp_path):
            try:
                os.remove(f.temp_path)
            except Exception as e:
                print(f"Error eliminando temporal {f.temp_path}: {e}")

class TempFileWrapper:
    """Wrapper para tratar ficheros (audio/imagen) como UploadedFile pero con respaldo en disco temporal."""
    def __init__(self, file_obj, name, temp_path=None, file_type=None):
        self.file_obj = file_obj
        self.name = name
        self.type = file_type if file_type else "application/octet-stream"
        self.size = file_obj.getbuffer().nbytes
        self._file_obj = file_obj
        self.temp_path = temp_path

    def getbuffer(self):
        return self.file_obj.getbuffer()
    
    def read(self, *args, **kwargs):
        return self.file_obj.read(*args, **kwargs)
    
    def seek(self, *args, **kwargs):
        return self.file_obj.seek(*args, **kwargs)

    def tell(self):
        return self.file_obj.tell()