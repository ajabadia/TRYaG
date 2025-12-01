"""
Servicio para descubrir y actualizar modelos de IA desde la API de Google.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from db.repositories.ai_models import get_ai_models_repository

# Cargar variables de entorno si no están cargadas
load_dotenv()

def fetch_and_update_models():
    """
    Conecta con la API de Google, obtiene los modelos disponibles
    y actualiza la base de datos local.
    Retorna: (success: bool, message: str, count: int)
    """
    api_key = None
    
    # 1. Try Streamlit Secrets (Best for Cloud)
    try:
        import streamlit as st
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass # Not running in streamlit or secrets not loaded

    # 2. Try Environment Variables
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    # 3. Fallback: Try loading from .streamlit/secrets.toml manually (Local script execution)
    if not api_key:
        try:
            import toml
            secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".streamlit", "secrets.toml")
            if os.path.exists(secrets_path):
                secrets = toml.load(secrets_path)
                api_key = secrets.get("GOOGLE_API_KEY")
        except Exception as e:
            print(f"Warning: Could not load secrets.toml: {e}")

    if not api_key:
        return False, "GOOGLE_API_KEY no encontrada en st.secrets, variables de entorno ni en secrets.toml.", 0

    try:
        genai.configure(api_key=api_key)
        
        valid_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                name = m.name
                if name.startswith("models/"):
                    name = name.replace("models/", "")
                
                valid_models.append(name)
        
        if not valid_models:
            return False, "No se encontraron modelos compatibles con generateContent.", 0
            
        # Actualizar DB
        repo = get_ai_models_repository()
        count = repo.update_models(valid_models)
        
        return True, f"Se han actualizado {count} modelos correctamente.", count

    except Exception as e:
        return False, f"Error al conectar con Google API: {str(e)}", 0
