# path: src/services/transcription_service.py
# Creado: 2025-11-23
"""
Servicio para la lógica de transcripción de audio con Gemini.
"""
import google.generativeai as genai
import json
from src.config import get_model_transcription

def transcribir_audio(file_obj=None, prompt_content=None, text_input=None):
    """
    Transcribe y traduce un fichero de audio o texto usando Gemini.
    
    Args:
        file_obj: Objeto de archivo (UploadedFile o similar) con método getbuffer() o read().
        prompt_content (str, optional): Contenido del prompt a usar (para pruebas).
        text_input (str, optional): Texto directo a procesar (para pruebas sin audio).
        
    Returns:
        tuple: (response_dict, final_prompt_str)
        response_dict: {
            "original_text": str,
            "language_code": str,
            "language_name": str,
            "translated_ia_text": str,
            "emotional_prosody": str (optional),
            "relevance": int (optional)
        } o {"status": "ERROR", "msg": str}
    """
    # 1. Obtener modelo configurado
    model_name = get_model_transcription()

    try:
        # Configuración específica para Flash (más rápido y barato para esto)
        generation_config = {
            "temperature": 0.2,
            "response_mime_type": "application/json",
        }
        
        try:
            model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
        except Exception as e:
             return {"status": "ERROR", "msg": f"Error al inicializar modelo ({model_name}): {e}"}, ""

        # 2. Obtener Prompt Dinámico (o usar el inyectado)
        if prompt_content:
            prompt = prompt_content
        else:
            from src.core.prompt_manager import PromptManager
            pm = PromptManager()
            prompt_data = pm.get_prompt("transcription")
            
            if not prompt_data:
                return {"status": "ERROR", "msg": "No se ha encontrado un prompt activo para 'transcription'."}, ""
                
            prompt = prompt_data.get("content", "")
        
        # 3. Preparar contenido según el tipo de entrada
        if text_input:
            # Modo texto: enviar solo el prompt + texto
            final_prompt = f"{prompt}\n\nTexto a procesar: {text_input}"
            response = model.generate_content(final_prompt)
        else:
            # Modo audio: leer bytes y enviar multimodal
            if not file_obj:
                return {"status": "ERROR", "msg": "Se requiere un archivo de audio o texto de entrada."}, prompt
                
            if hasattr(file_obj, 'getbuffer'):
                audio_data = bytes(file_obj.getbuffer())
            elif hasattr(file_obj, 'read'):
                file_obj.seek(0)
                audio_data = file_obj.read()
                file_obj.seek(0) # Restaurar puntero
            else:
                return {"status": "ERROR", "msg": "Formato de archivo no soportado para lectura."}, prompt

            # Preparar contenido multimodal (Prompt + Audio)
            audio_part = {
                "mime_type": "audio/wav", # Asumimos wav o mp3, genai suele ser flexible o requerir mime correcto.
                "data": audio_data
            }
            
            # Intentar deducir mime si es posible
            if hasattr(file_obj, 'type'):
                audio_part["mime_type"] = file_obj.type
            elif hasattr(file_obj, 'name') and file_obj.name.endswith('.mp3'):
                 audio_part["mime_type"] = "audio/mp3"
            
            final_prompt = prompt  # En modo audio, el prompt no se modifica
            response = model.generate_content([prompt, audio_part])
        
        if response.text:
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```"):
                lines = cleaned_text.split("\n")
                if len(lines) >= 2:
                    cleaned_text = "\n".join(lines[1:-1])
            return json.loads(cleaned_text), final_prompt
        else:
             return {"status": "ERROR", "msg": "Respuesta vacía del modelo."}, final_prompt
             
    except Exception as e:
        return {"status": "ERROR", "msg": f"Error en transcripción ({model_name}): {str(e)}"}, prompt if 'prompt' in locals() else ""
