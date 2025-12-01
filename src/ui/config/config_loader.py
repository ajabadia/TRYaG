# path: src/ui/config/config_loader.py
import streamlit as st
from db.repositories.general_config import get_general_config_repository
from db.repositories.centros import get_centros_repository
from db.repositories.salas import get_salas_by_centro

def load_general_config():
    """Carga la configuración general desde MongoDB."""
    repo = get_general_config_repository()
    return repo.get_config()

def save_general_config(config):
    """Guarda la configuración general en MongoDB."""
    repo = get_general_config_repository()
    return repo.save_config(config)

def load_centro_config():
    """Carga la configuración del centro desde MongoDB.
    
    Normalización:
    - Carga datos del centro (sin salas incrustadas).
    - Carga salas desde la colección 'salas' usando SalasRepository.
    - Combina ambos para mantener compatibilidad con la UI.
    """
    try:
        centros_repo = get_centros_repository()
        centro = centros_repo.get_centro_principal()
        
        if centro:
            if '_id' in centro:
                centro['_id'] = str(centro['_id'])
            
            # Cargar salas desde colección normalizada
            salas = get_salas_by_centro(centro['_id'])
            # Ordenar por código para consistencia
            salas.sort(key=lambda x: x.get('codigo', ''))
            
            centro['salas'] = salas
            return centro
            
    except Exception as e:
        st.error(f"Error al cargar configuración del centro: {e}")
    # Valores por defecto
    return {
        "codigo": "",
        "denominacion": "",
        "cif": "",
        "direccion": "",
        "email": "",
        "telefono": "",
        "logo_path": "",
        "mensaje": "",
        "salas": [],
    }


def save_centro_config(config):
    """Guarda la configuración del centro en MongoDB.
    
    Normalización:
    - NO guarda el array 'salas' en la colección 'centros'.
    - Las salas se gestionan independientemente vía SalasRepository.
    """
    try:
        centros_repo = get_centros_repository()
        
        # Crear copia para no modificar el original en session_state
        config_to_save = config.copy()
        
        # Eliminar 'salas' para evitar guardarlo en 'centros'
        if 'salas' in config_to_save:
            del config_to_save['salas']
            
        centros_repo.create_or_update_centro(
            codigo=config_to_save.get('codigo', ''),
            denominacion=config_to_save.get('denominacion', ''),
            cif=config_to_save.get('cif'),
            direccion=config_to_save.get('direccion'),
            email=config_to_save.get('email'),
            telefono=config_to_save.get('telefono'),
            logo_path=config_to_save.get('logo_path'),
            mensaje=config_to_save.get('mensaje'),
            salas=[], # Pasamos lista vacía explícitamente
            updated_by="admin",
        )
        return True
    except Exception as e:
        st.error(f"Error al guardar configuración del centro: {e}")
        return False
