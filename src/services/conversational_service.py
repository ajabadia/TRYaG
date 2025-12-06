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
            system_prompt_template = """Actúa como un Enfermero de Triaje experto y empático.
            Tu objetivo es realizar una entrevista clínica breve para clasificar al paciente.

            CONTEXTO:
            - Estás dialogando con un paciente en un servicio de urgencias.
            - Debes ser conciso, una pregunta a la vez.
            - NO des diagnósticos médicos, solo evalúa síntomas.

            HISTORIAL DE CONVERSACIÓN:
            {history_text}

            INSTRUCCIONES DE SALIDA:
            Debes responder SIEMPRE en formato JSON válido con la siguiente estructura:
            {
                "response": "Tu respuesta al paciente en texto plano (amable y breve).",
                "extracted_data": {
                    "sintomas": ["lista", "de", "sintomas", "detectados"],
                    "critical_alert": "Mensaje de alerta si detectas gravedad extrema (o null)",
                    "vital_signs_suggestion": "Sugerencia de constantes a medir (ej. 'Tomar tensión') (o null)"
                },
                "interview_status": "CONTINUE" (o "COMPLETED" si ya tienes info suficiente: motivo + síntomas + gravedad)
            }
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

    @staticmethod
    def analyze_clinical_text(text: str) -> Dict[str, Any]:
        """
        Analiza texto clínico (dictado por profesional) para extraer datos estructurados.
        No mantiene conversación, solo extrae.
        """
        from services.gemini_client import get_gemini_service
        import streamlit as st
        
        # Prompt Específico para Análisis de Texto Clínico
        system_prompt = """Actúa como un Asistente de Documentación Clínica.
        Analiza el siguiente texto dictado por un profesional sanitario.
        Tu objetivo es EXTRAER información estructurada para rellenar la historia clínica.
        
        TEXTO DEL PROFESIONAL:
        "{input_text}"
        
        INSTRUCCIONES:
        1. Identifica el 'Motivo de Consulta' principal.
        2. Extrae signos vitales si se mencionan (FC, TA, Temp, SatO2).
        3. Identifica antecedentes (Alergias, Patologías).
        4. NO inventes información. Si no está en el texto, déjalo null.
        
        FORMATO DE SALIDA (JSON):
        {
            "motivo_consulta": "Texto resumen del motivo",
            "historia_actual": "Texto detallado de la historia actual",
            "vital_signs": {
                "fc": valor_numerico_o_null,
                "spo2": valor_numerico_o_null,
                "temp": valor_numerico_o_null,
                "tas": valor_numerico_o_null,
                "tad": valor_numerico_o_null
            },
            "antecedentes": {
                "alergias": ["lista", "alergias"],
                "patologias": ["lista", "enfermedades"]
            },
            "suggestion": "Sugerencia breve si hay algo crítico (o null)"
        }
        """
        
        formatted_prompt = system_prompt.replace("{input_text}", text)
        
        try:
            service = get_gemini_service()
            # Usamos un modelo rápido y barato para esto (Flash)
            response_data, _ = service.generate_content(
                caller_id="clinical_dictation_analysis",
                user_id=st.session_state.get('current_user', {}).get('username', 'system'),
                call_type="dictation_analysis",
                prompt_type="clinical_dictation", # ID lógico, aunque usamos prompt hardcoded por ahora
                prompt_version_id="v1_hardcoded",
                model_name="gemini-2.5-flash", 
                prompt_content=formatted_prompt,
                generation_config={
                    "temperature": 0.1, # Muy determinista
                    "response_mime_type": "application/json"
                }
            )
            
            # El servicio ya devuelve el JSON parseado en response_data['parsed_response'] 
            # o response_data si es directo, dependiendo de la implementación de GeminiService.
            # Asumimos que generate_content devuelve una estructura limpia o el raw parseado.
            # Verificamos la estructura de retorno de generate_content en gemini_client.py
            
            # Si generate_content devuelve un dict con 'status', 'response', 'parsed_response'...
            if isinstance(response_data, dict) and "parsed_response" in response_data:
                return response_data["parsed_response"]
            elif isinstance(response_data, dict) and "motivo_consulta" in response_data:
                 return response_data
            
            # Fallback si no está parseado
            return {}

        except Exception as e:
            print(f"Dictation Analysis Error: {e}")
            return {}
