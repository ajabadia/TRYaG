# path: src/services/gemini_client.py
import google.generativeai as genai
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, Union, Tuple
import streamlit as st
from db.models import AIAuditLog
from db.repositories.ai_audit import get_ai_audit_repository

class GeminiService:
    """
    Servicio centralizado para interactuar con Google Gemini.
    Maneja configuración, llamadas, parsing y auditoría.
    """
    
    def __init__(self):
        # Configurar API Key globalmente si no está ya
        api_key = None
        
        # 1. Intentar desde st.secrets
        try:
            if "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except FileNotFoundError:
            pass
        except Exception:
            pass
            
        # 2. Fallback a variables de entorno
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
            
        if api_key:
            genai.configure(api_key=api_key)
        else:
            print("WARNING: GOOGLE_API_KEY not found in secrets or env vars.")
            
        self.audit_repo = get_ai_audit_repository()

    def generate_content(
        self,
        caller_id: str,
        user_id: str,
        call_type: str,
        prompt_type: str,
        prompt_version_id: str,
        model_name: str,
        prompt_content: Union[str, list],
        generation_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], str]:
        """
        Realiza una llamada a Gemini y registra la auditoría.

        Args:
            caller_id: Identificador del proceso (ej: 'triage_service').
            user_id: Usuario que inicia la acción.
            call_type: Tipo de llamada (triage, transcription, etc.).
            prompt_type: Tipo de prompt (triage_gemini, etc.).
            prompt_version_id: Versión del prompt usada.
            model_name: Nombre del modelo (gemini-1.5-flash, etc.).
            prompt_content: String o lista (para multimodal) con el contenido.
            generation_config: Configuración específica (temp, tokens).
            metadata: Datos extra para el log.

        Returns:
            Tuple[Dict, str]: (Respuesta parseada JSON o Error, Raw Prompt String)
        """
        start_time = datetime.now()
        
        # Configuración por defecto
        if generation_config is None:
            generation_config = {
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
            
        # Preparar raw_prompt para log (sanitizar binarios)
        if isinstance(prompt_content, str):
            raw_prompt_log = prompt_content
        elif isinstance(prompt_content, list):
            log_parts = []
            for part in prompt_content:
                if isinstance(part, dict) and "data" in part:
                    # Es un blob de datos (imagen/audio)
                    mime = part.get("mime_type", "unknown")
                    size = len(part["data"]) if hasattr(part["data"], "__len__") else "unknown"
                    log_parts.append(f"[{mime} DATA, size={size}]")
                elif hasattr(part, "read"):
                     log_parts.append("[FILE OBJECT]")
                else:
                    log_parts.append(str(part))
            raw_prompt_log = str(log_parts)
        else:
            raw_prompt_log = str(prompt_content)
        
        response_data = {"status": "ERROR", "msg": "Unknown error"}
        raw_response_log = ""
        status = "error"
        error_msg = None

        try:
            # Configuración de seguridad permisiva para evitar bloqueos en contexto médico
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            model = genai.GenerativeModel(
                model_name=model_name, 
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Retry logic for transient errors
            import time
            from google.api_core import exceptions as google_exceptions
            
            max_retries = 3
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    # Llamada a la API
                    response = model.generate_content(prompt_content)
                    break # Success
                except (google_exceptions.ServiceUnavailable, 
                        google_exceptions.DeadlineExceeded, 
                        google_exceptions.ResourceExhausted,
                        google_exceptions.Aborted,
                        google_exceptions.InternalServerError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt # 1s, 2s, 4s
                        print(f"⚠️ Gemini API Error ({e}). Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise last_error
            
            # Procesar respuesta
            if not response.parts:
                # Intentar obtener más detalles del error
                finish_reason = "UNKNOWN"
                if response.candidates:
                    finish_reason = response.candidates[0].finish_reason.name
                
                if response.prompt_feedback:
                    block_reason = response.prompt_feedback.block_reason.name
                    error_msg = f"Blocked: {block_reason}"
                    response_data = {"status": "ERROR", "msg": error_msg}
                else:
                    error_msg = f"Empty response parts. Finish Reason: {finish_reason}"
                    response_data = {"status": "ERROR", "msg": error_msg}
            else:
                raw_response_log = response.text
                cleaned_text = response.text.strip()
                
                # Limpiar markdown code blocks
                if cleaned_text.startswith("```"):
                    lines = cleaned_text.split("\n")
                    if len(lines) >= 2:
                        cleaned_text = "\n".join(lines[1:-1])
                
                try:
                    response_data = json.loads(cleaned_text)
                    status = "success"
                except json.JSONDecodeError:
                    error_msg = "Invalid JSON response"
                    response_data = {"status": "ERROR", "msg": error_msg, "raw": cleaned_text}
                    
        except Exception as e:
            error_msg = str(e)
            # Detectar si es error de conexión para sugerir contingencia
            if "503" in error_msg or "deadline" in error_msg.lower() or "connection" in error_msg.lower():
                response_data = {
                    "status": "ERROR", 
                    "msg": f"Error de Conexión con IA: {error_msg}", 
                    "suggest_contingency": True
                }
            else:
                response_data = {"status": "ERROR", "msg": f"Exception: {error_msg}"}
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000

        # Registrar Auditoría
        try:
            log_entry = AIAuditLog(
                timestamp_start=start_time,
                timestamp_end=end_time,
                duration_ms=duration,
                caller_id=caller_id,
                user_id=user_id,
                call_type=call_type,
                prompt_type=prompt_type,
                prompt_version_id=prompt_version_id or "unknown",
                model_name=model_name,
                raw_prompt=raw_prompt_log,
                raw_response=raw_response_log or str(response_data),
                status=status,
                error_msg=error_msg,
                metadata=metadata or {}
            )
            self.audit_repo.log_call(log_entry)
        except Exception as log_err:
            print(f"CRITICAL: Failed to log AI audit: {log_err}")

        return response_data, raw_prompt_log

# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
