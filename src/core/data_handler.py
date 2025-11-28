# src/core/data_handler.py
# Creado: 2025-11-21
# Última modificación: 2025-11-24
"""
Módulo para la persistencia y acceso a datos.

Contiene toda la lógica para leer y escribir en los repositorios de datos.
"""
import os
from utils.file_handler import process_and_log_files, cleanup_temp_files
from src.db.repositories.audit import get_audit_repository

# --- CONSTANTES ---
# AUDIT_LOG_FILE ya no se usa

def guardar_auditoria(datos, session_state):
    """
    Guarda los datos de una decisión de triaje en MongoDB.
    """
    audit_repo = get_audit_repository()
    
    # Extraer usuario y patient_code si están disponibles
    usuario = datos.get('usuario', 'unknown')
    patient_code = datos.get('patient_code')
    accion = datos.get('accion', 'triaje') # Asumimos triaje si no se especifica
    
    # Crear registro en MongoDB
    try:
        # El repositorio devuelve el ID del nuevo registro (ObjectId como string)
        audit_id = audit_repo.registrar_accion(
            accion=accion,
            usuario=usuario,
            detalles=datos,
            patient_code=patient_code
        )
        
        # Procesamos los ficheros asociados, ahora pasando el session_state
        # Nota: session_state.datos_paciente puede no existir si la estructura cambió,
        # pero mantenemos la lógica original adaptada.
        datos_paciente = getattr(session_state, 'datos_paciente', {})
        if not datos_paciente and isinstance(session_state, dict):
             datos_paciente = session_state.get('datos_paciente', {})
             
        all_files = datos_paciente.get('imagenes', [])
        ai_selected = [f.name for f in datos_paciente.get('imagenes_confirmadas_ia', [])]
        
        # Separar por tipo (Importados vs Grabados)
        recorded_files = []
        imported_files = []
        
        for f in all_files:
            # Verificamos si es un wrapper temporal
            is_wrapper = f.__class__.__name__ == 'TempFileWrapper'
            # Si es wrapper y es audio (por nombre o extensión), lo consideramos grabado
            is_audio_recording = is_wrapper and (f.name.startswith('audio_') or f.name.endswith('.wav'))
            
            if is_audio_recording:
                recorded_files.append(f)
            else:
                imported_files.append(f)

        # Procesar importados
        if imported_files:
            process_and_log_files(
                audit_id=audit_id,
                uploaded_files=imported_files,
                ai_selected_files_names=ai_selected,
                source_type="imported"
            )
            cleanup_temp_files(imported_files)
            
        # Procesar grabados
        if recorded_files:
            process_and_log_files(
                audit_id=audit_id,
                uploaded_files=recorded_files,
                ai_selected_files_names=ai_selected,
                source_type="recorded"
            )
            cleanup_temp_files(recorded_files)

        return audit_id
        
    except Exception as e:
        print(f"Error guardando auditoría: {e}")
        return None