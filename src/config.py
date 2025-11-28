# path: src/config.py
# Creado: 2025-11-22
# Última modificación: 2025-11-23
"""
Archivo de configuración para constantes y parámetros globales de la aplicación.
Ahora usa MongoDB para almacenar la configuración.
"""
import json
import os
import sys
import streamlit as st

# Añadir directorio raíz al path para imports
if os.path.dirname(os.path.dirname(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importar repositorio de configuración
try:
    from db.repositories.config import get_config_repository
except ImportError:
    # Fallback si no se puede importar
    get_config_repository = None

# Configuración de Validación
def get_min_chars_motivo():
    """
    Obtiene MIN_CHARS_MOTIVO desde session_state, MongoDB o valor por defecto.
    Prioridad: session_state > MongoDB > JSON (fallback) > default
    """
    # 1. Intentar desde session_state (más reciente)
    if hasattr(st, 'session_state') and 'general_config' in st.session_state:
        return st.session_state.general_config.get('min_chars_motivo', 3)
    
    # 2. Intentar desde MongoDB
    try:
        repo = get_config_repository()
        config_item = repo.get_by_key('min_chars_motivo')
        if config_item:
            return config_item['value']
    except Exception:
        pass
    
    # 3. Fallback: intentar desde archivo JSON de configuración general
    config_file = os.path.join('data', 'config_general.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('min_chars_motivo', 3)
        except Exception:
            pass
    
    # 4. Valor por defecto
    return 3

# Esta constante ahora es una función para obtener el valor dinámicamente
MIN_CHARS_MOTIVO = get_min_chars_motivo()

def get_model_triage():
    """
    Obtiene el nombre del modelo para triaje desde MongoDB.
    Default: gemini-2.5-flash
    """
    # 1. Intentar desde MongoDB
    try:
        repo = get_config_repository()
        config_item = repo.get_by_key('model_triage')
        if config_item:
            return config_item['value']
    except Exception:
        pass
    
    # 2. Fallback: intentar desde archivo JSON
    config_file = os.path.join('data', 'config_general.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('model_triage', 'gemini-2.5-flash')
        except Exception:
            pass
    
    # 3. Valor por defecto
    return 'gemini-2.5-flash'

def get_model_transcription():
    """
    Obtiene el nombre del modelo para transcripción desde MongoDB.
    Default: gemini-2.0-flash-exp
    """
    # 1. Intentar desde MongoDB
    try:
        repo = get_config_repository()
        config_item = repo.get_by_key('model_transcription')
        if config_item:
            return config_item['value']
    except Exception:
        pass
    
    # 2. Fallback: intentar desde archivo JSON
    config_file = os.path.join('data', 'config_general.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('model_transcription', 'gemini-2.0-flash-exp')
        except Exception:
            pass
    
    # 3. Valor por defecto
    return 'gemini-2.0-flash-exp'

def get_model_simulation():
    """
    Obtiene el nombre del modelo para simulación desde MongoDB.
    Default: gemini-2.5-flash
    """
    # 1. Intentar desde MongoDB
    try:
        repo = get_config_repository()
        config_item = repo.get_by_key('model_simulation')
        if config_item:
            return config_item['value']
    except Exception:
        pass
    
    # 2. Fallback: intentar desde archivo JSON
    config_file = os.path.join('data', 'config_general.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('model_simulation', 'gemini-2.5-flash')
        except Exception:
            pass
    
    # 3. Valor por defecto
    return 'gemini-2.5-flash'
