# path: src/services/transcription_service.py
# Creado: 2025-11-23
"""
Servicio para la lógica de transcripción de audio con Gemini.
"""
import json
from services.gemini_client import get_gemini_service
from core.prompt_manager import PromptManager
from core.config import get_model_transcription

def transcribir_audio(file_obj=None, prompt_content=None, text_input=None, user_id="system", prompt_type="transcription"):
    """
    Transcribe y traduce un fichero de audio o texto usando Gemini.
    """
    # 1. Obtener Prompt y Configuración
    pm = PromptManager()
    # 0. Verificar Modo Contingencia
    from services.contingency_service import is_contingency_active
    if is_contingency_active():
        return {"status": "ERROR", "msg": "Modo Contingencia activo: Transcripción IA desactivada.", "suggest_contingency": True}, ""

    if prompt_content:
        prompt = prompt_content
        model_name = "gemini-2.0-flash-exp" # Default for tests
        version_id = "test-override"
    else:
        prompt_data = pm.get_prompt(prompt_type)
        if not prompt_data:
            return {"status": "ERROR", "msg": "No se ha encontrado un prompt activo para 'transcription'."}, ""
            
        prompt = prompt_data.get("content", "")
        version_id = prompt_data.get("version_id", "unknown")
        model_name = prompt_data.get("model") or get_model_transcription()
    
    # 2. Preparar Contenido (Prompt + Audio/Texto)
    final_prompt_content = []
    
    if text_input:
        # Modo texto
        final_prompt_str = f"{prompt}\n\nTexto a procesar: {text_input}"
        final_prompt_content = final_prompt_str # GeminiService maneja str
    else:
        # Modo audio
        if not file_obj:
            return {"status": "ERROR", "msg": "Se requiere un archivo de audio o texto de entrada."}, prompt
            
        if hasattr(file_obj, 'getbuffer'):
            audio_data = bytes(file_obj.getbuffer())
        elif hasattr(file_obj, 'read'):
            file_obj.seek(0)
            audio_data = file_obj.read()
            file_obj.seek(0)
        else:
            return {"status": "ERROR", "msg": "Formato de archivo no soportado para lectura."}, prompt

        audio_part = {
            "mime_type": "audio/wav", 
            "data": audio_data
        }
        
        if hasattr(file_obj, 'type'):
            audio_part["mime_type"] = file_obj.type
        elif hasattr(file_obj, 'name') and file_obj.name.endswith('.mp3'):
                audio_part["mime_type"] = "audio/mp3"
        
        final_prompt_content = [prompt, audio_part]
        final_prompt_str = prompt # Para devolver como "prompt usado" (sin el binario)

    # 3. Llamar al Servicio Centralizado
    service = get_gemini_service()
    
    response_data, _ = service.generate_content(
        caller_id="transcription_service",
        user_id=user_id,
        call_type="transcription",
        prompt_type=prompt_type,
        prompt_version_id=version_id,
        model_name=model_name,
        prompt_content=final_prompt_content,
        generation_config={
            "temperature": 0.2,
            "response_mime_type": "application/json",
        },
        metadata={
            "input_type": "text" if text_input else "audio",
            "file_name": getattr(file_obj, 'name', 'unknown') if file_obj else None
        }
    )

    # 4. Post-Procesado de Respuesta
    # Si el prompt era "transcription" (JSON complex), extraer el texto traducido.
    # Si es "clinical_dictation" (Texto plano o JSON simple), devolver texto.
    
    final_text_result = None
    
    if isinstance(response_data, dict):
        if "translated_ia_text" in response_data:
            final_text_result = response_data["translated_ia_text"]
        elif "transcription" in response_data:
             final_text_result = response_data["transcription"]
        elif "original_text" in response_data:
             final_text_result = response_data["original_text"]
        else:
             # Fallback JSON dump
             final_text_result = json.dumps(response_data, ensure_ascii=False)
    else:
        final_text_result = str(response_data)

    # Devolver TUPLA: (Respuesta Completa API, Texto Extraído)
    return response_data, final_text_result
