from typing import List, Dict, Any
import random
import time

class ConversationalService:
    """
    Servicio para manejar el Triaje Conversacional.
    Simula una interacción médico-paciente para extraer información.
    """

    @staticmethod
    def get_initial_greeting() -> str:
        return "Hola, soy tu asistente de triaje. ¿Cuál es el motivo principal de la consulta hoy? Cuéntame los síntomas."

    @staticmethod
    def process_message(user_message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Procesa el mensaje del usuario utilizando Google Gemini (Phase 11.4).
        Mantiene el contexto de la conversación y extrae datos estructurados.
        """
        from services.gemini_client import get_gemini_service
        import streamlit as st
        
        # Construir prompt con historial
        history_text = ""
        for msg in history:
            role = "Asistente" if msg["role"] == "assistant" else "Paciente"
            history_text += f"{role}: {msg['content']}\n"
        
        history_text += f"Paciente: {user_message}\n"
        
        # 1. Verificar Contingencia
        from services.contingency_service import is_contingency_active
        if is_contingency_active():
             return {
                "response": "⚠️ El sistema está en Modo Contingencia (Sin IA). Por favor use el formulario manual.",
                "extracted_data": {}
             }

        # 2. Obtener Prompt desde Configuración (DB)
        from db.repositories.prompts import get_prompts_repository
        prompt_repo = get_prompts_repository()
        
        # Recuperar prompt activo
        prompt_config = prompt_repo.get_active_version("triage_chat")
        
        system_prompt_template = ""
        model_name = "gemini-2.5-flash"
        
        if prompt_config:
            system_prompt_template = prompt_config.get("content", "")
            if prompt_config.get("model"):
                model_name = prompt_config.get("model")
        
        # Fallback si BD falla o está vacío
        if not system_prompt_template:
            system_prompt_template = """Actúa como un Enfermero de Triaje experto...
            HISTORIAL: {history_text}
            ... (Fallback hardcoded) ...
            """
            
        # 3. Inyectar Historial
        system_prompt = system_prompt_template.replace("{history_text}", history_text)
        
        try:
            service = get_gemini_service()
            response_data, _ = service.generate_content(
                caller_id="conversational_triage",
                user_id=st.session_state.get('current_user', {}).get('username', 'anonymous'),
                call_type="chat_interaction",
                prompt_type="triage_chat",
                prompt_version_id=prompt_config.get("version_id", "fallback") if prompt_config else "fallback",
                model_name=model_name, 
                prompt_content=system_prompt
            )
            
            if response_data.get("status") == "ERROR":
                return {
                    "response": "Lo siento, he tenido un problema de conexión. ¿Podrías repetirlo?",
                    "extracted_data": {}
                }
                
            return response_data
            
        except Exception as e:
            print(f"Chat Error: {e}")
            return {
                "response": "Ha ocurrido un error interno. Por favor, utiliza el formulario estándar.",
                "extracted_data": {}
            }
