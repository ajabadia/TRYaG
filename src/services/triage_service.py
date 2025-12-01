# path: src/services/triage_service.py
# Creado: 2025-11-23
"""
Servicio para la lógica de triaje con Gemini.
"""
import json
from services.gemini_client import get_gemini_service
from core.prompt_manager import PromptManager
from config import get_model_triage

def llamar_modelo_gemini(motivo, edad, dolor, vital_signs=None, imagen=None, prompt_content=None, triage_result=None, antecedentes=None, alergias=None, gender=None, criterio_geriatrico=False, criterio_inmunodeprimido=False, criterio_inmunodeprimido_det=None, user_id="system", extended_history=None, nursing_assessment=None):
    """
    Llama al modelo Gemini de Google para obtener una sugerencia de triaje.
    """
    # ... (rest of the function setup) ...
    # 1. Obtener Prompt y Configuración
    pm = PromptManager()
    prompt_data = None
    
    if prompt_content:
        base_prompt = prompt_content
        model_name = "gemini-1.5-flash-001" # Default for tests if not specified
        version_id = "test-override"
    else:
        # Obtener versión activa
        prompt_data = pm.get_prompt("triage_gemini")
        if not prompt_data:
            return {"status": "ERROR", "msg": "No se ha encontrado un prompt activo para 'triage_gemini'."}, ""
            
        base_prompt = prompt_data.get("content", "")
        version_id = prompt_data.get("version_id", "unknown")
        # Usar modelo de la versión o fallback a config global
        model_name = prompt_data.get("model") or get_model_triage()

    # 2. Formatear Signos Vitales
    vs_str = "No registrados"
    if vital_signs:
        vs_list = []
        for k, v in vital_signs.items():
            if v is not None:
                vs_list.append(f"{k.upper()}: {v}")
        
        if triage_result:
            vs_list.append("\n--- ANÁLISIS AUTOMÁTICO DE SIGNOS VITALES ---")
            vs_list.append(f"Clasificación Global: {triage_result.get('label', 'N/A')} (Prioridad {triage_result.get('final_priority', 'N/A')})")
            vs_list.append(f"Tiempo Máximo Sugerido: {triage_result.get('wait_time', 'N/A')}")
            
            if 'details' in triage_result:
                vs_list.append("Detalles:")
                for det in triage_result['details']:
                    icon = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴", "black": "⚫", "gray": "⚪"}.get(det.get('color'), "")
                    vs_list.append(f"- {det.get('metric', '').upper()}: {det.get('value')} -> {icon} {det.get('label', '')}")
        
        if vs_list:
            vs_str = "\n".join(vs_list)

    # 3. Inyectar variables
    motivo_completo = str(motivo)
    if antecedentes:
        motivo_completo += f"\n\n[ANTECEDENTES BÁSICOS]: {antecedentes}"
    if alergias:
        motivo_completo += f"\n\n[ALERGIAS]: {alergias}"
    
    # Inyectar Historia Extendida
    if extended_history:
        ext_lines = []
        if isinstance(extended_history, dict):
            for k, v in extended_history.items():
                if v:
                    label = k.replace('_', ' ').title()
                    ext_lines.append(f"- {label}: {v}")
        elif isinstance(extended_history, str):
            ext_lines.append(extended_history)
            
        if ext_lines:
            motivo_completo += "\n\n[HISTORIA CLÍNICA EXTENDIDA]:\n" + "\n".join(ext_lines)

    # Inyectar Valoración Enfermería
    if nursing_assessment:
        nur_lines = []
        for k, v in nursing_assessment.items():
            if v:
                label = k.replace('_', ' ').title()
                nur_lines.append(f"- {label}: {v}")
        if nur_lines:
            motivo_completo += "\n\n[VALORACIÓN ENFERMERÍA]:\n" + "\n".join(nur_lines)
    
    # Inyectar Contexto Clínico Avanzado
    contexto_clinico = []
    if criterio_geriatrico:
        contexto_clinico.append("PACIENTE GERIÁTRICO (Edad >= 65): Considerar taquicardia leve (>100) como riesgo moderado/alto. Umbrales de dolor pueden ser atípicos.")
    if criterio_inmunodeprimido:
        detalles = f" ({criterio_inmunodeprimido_det})" if criterio_inmunodeprimido_det else ""
        contexto_clinico.append(f"PACIENTE INMUNODEPRIMIDO/ONCOLÓGICO{detalles}: Fiebre (>38.0°C) es EMERGENCIA (Nivel 2/Naranja) inmediata. Ignorar ponderación estándar de temperatura.")
    
    if contexto_clinico:
        motivo_completo += "\n\n[CONTEXTO CLÍNICO CRÍTICO]:\n" + "\n".join(contexto_clinico)
    
    # Inyectar género en la edad para contexto
    edad_str = str(edad)
    if gender:
        edad_str += f" ({gender})"
        
    final_prompt = base_prompt.replace("{motivo}", motivo_completo)\
                              .replace("{edad}", edad_str)\
                              .replace("{dolor}", str(dolor))\
                              .replace("{signos_vitales}", vs_str)

    prompt_parts = [final_prompt]
    if imagen:
        prompt_parts.append("\nInput (Imagen):")
        prompt_parts.append(imagen)

    # 4. Llamar al Servicio Centralizado
    service = get_gemini_service()
    
    response_data, raw_prompt = service.generate_content(
        caller_id="triage_service",
        user_id=user_id,
        call_type="triage",
        prompt_type="triage_gemini",
        prompt_version_id=version_id,
        model_name=model_name,
        prompt_content=prompt_parts,
        generation_config={
            "temperature": 0.2,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
            "response_mime_type": "application/json",
        },
        metadata={
            "patient_age": edad,
            "has_image": bool(imagen)
        }
    )

    # 5. Post-procesamiento específico de Triaje
    if response_data.get("status") == "ERROR":
        return response_data, final_prompt

    # Manejar exclusión (Nivel 0)
    if response_data.get("nivel_sugerido") == 0:
        return {
            "status": "EXCLUDED",
            "msg": f"⚠️ ALERTA: La IA ha clasificado el caso como no traumatológico. {response_data.get('razonamiento', [''])[0]}"
        }, final_prompt

    return response_data, final_prompt
