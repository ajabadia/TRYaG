# path: src/services/triage_service.py
# Creado: 2025-11-23
"""
Servicio para la lógica de triaje con Gemini.
"""
import google.generativeai as genai
import json
from src.config import get_model_triage



def llamar_modelo_gemini(motivo, edad, dolor, imagen=None, prompt_content=None):
    """
    Llama al modelo Gemini de Google para obtener una sugerencia de triaje.
 
    Construye un prompt detallado con los datos del paciente y las instrucciones
    para que el modelo actúe como un experto en triaje. Pide al modelo que
    devuelva la respuesta en un formato JSON estructurado para facilitar su
    procesamiento.
 
    Args:
        motivo (str): Descripción en texto libre del motivo de la consulta.
        edad (int): Edad del paciente.
        dolor (int): Nivel de dolor del paciente en una escala de 0 a 10.
        imagen (PIL.Image, optional): Una imagen de la lesión. Por defecto es None.
        prompt_content (str, optional): Contenido del prompt a usar (para pruebas). Si es None, usa el activo.
 
    Returns:
        dict: Un diccionario con la respuesta del modelo ya parseada. En caso
              de error, devuelve un diccionario con el estado 'ERROR'.
    """
    # 1. Obtener modelo configurado
    model_name = get_model_triage()
    
    # 2. Configuración del modelo y de la generación
    generation_config = {
        "temperature": 0.2,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json",
    }
    
    try:
        model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
    except Exception as e:
        return {"status": "ERROR", "msg": f"Error al inicializar modelo ({model_name}): {e}"}, ""

    # 3. Obtener Prompt Dinámico (o usar el inyectado)
    if prompt_content:
        base_prompt = prompt_content
    else:
        from src.core.prompt_manager import PromptManager
        pm = PromptManager()
        prompt_data = pm.get_prompt("triage_gemini")
        
        if not prompt_data:
            return {"status": "ERROR", "msg": "No se ha encontrado un prompt activo para 'triage_gemini'. Configure uno en el panel."}, ""
            
        base_prompt = prompt_data.get("content", "")
    
    # Inyectar variables en el prompt
    # El prompt almacenado espera {motivo}, {edad}, {dolor}
    # Inyectar variables en el prompt
    # Usamos replace en lugar de format para evitar conflictos con las llaves de los ejemplos JSON
    final_prompt = base_prompt.replace("{motivo}", str(motivo))\
                              .replace("{edad}", str(edad))\
                              .replace("{dolor}", str(dolor))

    prompt_parts = [final_prompt]

    # --- Añadir la imagen al prompt si existe ---
    if imagen:
        prompt_parts.append("\nInput (Imagen):")
        prompt_parts.append(imagen)

    try:
        # 4. Llamada a la API de Gemini
        response = model.generate_content(prompt_parts)

        # 5. GESTIÓN DE RESPUESTA Y ERRORES DE SEGURIDAD
        if not response.parts:
            razon_bloqueo = response.prompt_feedback.block_reason.name
            return {
                "status": "ERROR",
                "msg": f"La solicitud fue bloqueada por los filtros de seguridad de la IA (Razón: {razon_bloqueo}). Esto puede ocurrir si el texto o las imágenes contienen contenido sensible."
            }, final_prompt

        # Caso 2: La respuesta es válida, se procesa el JSON.
        cleaned_text = response.text.strip()
        if cleaned_text.startswith("```"):
            # Eliminar primera línea (```json o ```) y última línea (```)
            lines = cleaned_text.split("\n")
            if len(lines) >= 2:
                cleaned_text = "\n".join(lines[1:-1])
        
        datos_json = json.loads(cleaned_text)

        # Post-procesamiento para manejar el Nivel 0 (exclusión)
        if datos_json.get("nivel_sugerido") == 0:
            return {
                "status": "EXCLUDED",
                "msg": f"⚠️ ALERTA: La IA ha clasificado el caso como no traumatológico. {datos_json.get('razonamiento', [''])[0]}"
            }, final_prompt

        return datos_json, final_prompt

    except Exception as e:
        # Caso 3: Ocurrió una excepción general durante la llamada a la API.
        # Devolvemos un diccionario de error en lugar de llamar a st.error
        return {"status": "ERROR", "msg": f"Ha ocurrido un error inesperado al contactar con el modelo Gemini ({model_name}): {e}"}, final_prompt
