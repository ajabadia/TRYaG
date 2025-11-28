import google.generativeai as genai

def configure_gemini(api_key):
    """
    Configura la API de Google Gemini con la clave proporcionada.

    Args:
        api_key (str): La clave de API para autenticarse.

    Returns:
        tuple: Una tupla (bool, str) donde el primer elemento es True si la
               configuración fue exitosa, y el segundo es un mensaje de
               error si falló.
    """
    try:
        genai.configure(api_key=api_key)
        return True, None
    except Exception as e:
        return False, str(e)
