# path: src/services/triage_service.py
# Creado: 2025-11-23
"""
Servicio para la lógica de triaje con Gemini.
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    # Attempt relative imports (Package context)
    from .gemini_client import get_gemini_service
    from .rag_service import get_rag_service
    from ..core.prompt_manager import PromptManager
    from ..core.config import get_model_triage
    from ..db.repositories.triage import get_triage_repository
    from ..db.models import TriageRecord, AIReason, AIResponse
except ImportError:
    # Fallback for Streamlit (Script context where src is root)
    from services.gemini_client import get_gemini_service
    from services.rag_service import get_rag_service
    from core.prompt_manager import PromptManager
    from core.config import get_model_triage
    from db.repositories.triage import get_triage_repository
    from db.models import TriageRecord, AIReason, AIResponse

def _parse_ai_reasons(razones_raw: Any) -> List[AIReason]:
    """
    Parsea las razones de la IA usando una estrategia robusta:
    1. JSON Array
    2. Separado por pipes (|)
    3. Texto único
    """
    reasons_text = []
    
    # Estrategia 1: JSON Array
    if isinstance(razones_raw, list):
        reasons_text = [str(r) for r in razones_raw]
    elif isinstance(razones_raw, str):
        razones_raw = razones_raw.strip()
        # Intentar detectar JSON en markdown
        if "```json" in razones_raw:
            try:
                import re
                match = re.search(r'```json\s*(\[.*?\])\s*```', razones_raw, re.DOTALL)
                if match:
                    reasons_text = json.loads(match.group(1))
            except:
                pass
        
        # Intentar JSON directo
        if not reasons_text and razones_raw.startswith("[") and razones_raw.endswith("]"):
            try:
                reasons_text = json.loads(razones_raw)
            except:
                pass
        
        # Estrategia 2: Pipe separator
        if not reasons_text and "|" in razones_raw:
            reasons_text = [r.strip() for r in razones_raw.split("|") if r.strip()]
            
        # Estrategia 3: Fallback a texto único
        if not reasons_text and razones_raw:
            reasons_text = [razones_raw]
            
    # Convertir a objetos AIReason
    return [AIReason(text=r, included_in_decision=True) for r in reasons_text]

def create_draft_triage(patient_id: str, user_id: str) -> str:
    """Crea un borrador de triaje para un paciente."""
    repo = get_triage_repository()
    # Verificar si ya existe uno activo
    existing = repo.find_one({"patient_id": patient_id, "status": "draft"})
    if existing:
        return str(existing["_id"])
        
    record = TriageRecord(
        audit_id=f"DRAFT-{datetime.now().strftime('%Y%m%d%H%M%S')}", # ID temporal
        patient_id=patient_id,
        evaluator_id=user_id,
        status="draft",
        sugerencia_ia={}, # Vacío inicial
        timestamp=datetime.now()
    )
    # Guardar como dict para evitar validación estricta inicial si faltan campos
    return repo.create(record.model_dump(by_alias=True, exclude_none=True))

def get_active_draft(patient_id: str) -> Optional[Dict]:
    """Obtiene el borrador activo de un paciente."""
    repo = get_triage_repository()
    return repo.find_one({"patient_id": patient_id, "status": "draft"})

def update_triage_draft(triage_id: str, data: Dict[str, Any]):
    """Actualiza un borrador de triaje."""
    repo = get_triage_repository()
    repo.update(triage_id, data)

def finalize_triage_draft(triage_id: str, final_data: Dict[str, Any]):
    """Finaliza un borrador convirtiéndolo en completado."""
    repo = get_triage_repository()
    final_data["status"] = "completed"
    final_data["timestamp"] = datetime.now() # Actualizar fecha al finalizar
    repo.update(triage_id, final_data)

def discard_draft(patient_id: str):
    """Descarta (invalida) el borrador activo de un paciente."""
    repo = get_triage_repository()
    draft = repo.find_one({"patient_id": patient_id, "status": "draft"})
    if draft:
        # Opción A: Soft delete (cambiar estado) - Preferido para auditoría
        repo.update(str(draft["_id"]), {"status": "discarded", "discarded_at": datetime.now()})
        # Opción B: Hard delete
        # repo.delete(str(draft["_id"]))

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
        model_name = "gemini-2.5-flash" # Default for tests if not specified
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
    
    # ---------------------------------------------------------
    # RAG: Recuperación de Contexto (Memoria Institucional)
    # ---------------------------------------------------------
    try:
        rag = get_rag_service()
        # Buscamos contexto usando el motivo y signos vitales como query
        query_rag = f"{motivo} {vs_str}"
        context_docs = rag.search_context(query_rag, n_results=3)
        
        if context_docs:
            rag_context_str = "\n".join([f"- {doc}" for doc in context_docs])
            motivo_completo += f"\n\n[MEMORIA INSTITUCIONAL / PROTOCOLOS INTERNOS]:\n{rag_context_str}\n\nINSTRUCCIÓN RAG: Usa la información anterior para fundamentar tu respuesta. Si el protocolo interno contradice tu conocimiento general, PRIORIZA EL PROTOCOLO INTERNO."
            print(f"RAG Context injected ({len(context_docs)} chunks)")
    except Exception as e:
        print(f"RAG Error: {e}")
    # ---------------------------------------------------------

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
    
    # Check Contingency
    from services.contingency_service import is_contingency_active
    if is_contingency_active():
        return {
            "status": "ERROR",
            "msg": "Modo Contingencia Activo: Servicio de IA no disponible.",
            "nivel_sugerido": 0
        }, "Offline Mode"

    service = get_gemini_service()
    
    # Configuración de Seguridad
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
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
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        },
        safety_settings=safety_settings,
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

    # PARSEO DE RAZONES (NUEVO)
    # Convertir razones raw a objetos AIReason
    raw_reasons = response_data.get("razones", [])
    parsed_reasons = _parse_ai_reasons(raw_reasons)
    
    # Serializar para devolver al frontend (que espera dicts, no pydantic models directamente)
    response_data["razones"] = [r.model_dump() for r in parsed_reasons]

    # --- VERSIONADO DE RESPUESTAS (PHASE 8.7) ---
    # Crear objeto AIResponse
    new_ai_response = AIResponse(
        timestamp=datetime.now(),
        sugerencia_ia=response_data,
        razones_parsed=parsed_reasons,
        model_version=version_id,
        status="accepted" # Por defecto la última es la aceptada (activa) hasta que se regenere
    )

    # Si hay un triage_id activo (estamos editando un borrador), actualizar historial
    # Nota: llamar_modelo_gemini es stateless, pero si se usa en contexto de un record existente,
    # el caller debería encargarse de guardar. Sin embargo, aquí devolvemos los datos para que el caller (input_form)
    # actualice el estado.
    
    # Inyectamos el objeto AIResponse serializado en la respuesta para que input_form lo pueda usar
    response_data["_ai_response_object"] = new_ai_response.model_dump(mode='json')

    return response_data, final_prompt

class TriageService:
    """
    Wrapper class for Triage Logic to be used by API and other services.
    Enables dependency injection and standardized interface.
    """
    def __init__(self):
        pass

    def analyze_case(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza un caso clínico usando la lógica central de Gemini.
        Mapea el input de la API a los argumentos de llamar_modelo_gemini.
        """
        # Extraer datos del request mapping
        motivo = request_data.get("motivo_consulta", "")
        edad = request_data.get("edad", 0)
        dolor = request_data.get("dolor", 0)
        antecedentes = request_data.get("antecedentes", "")
        
        # Signos vitales
        vital_signs = request_data.get("signos_vitales", {})
        if hasattr(vital_signs, 'dict'):
             vital_signs = vital_signs.dict() # Handle Pydantic model input if passed directly
        if not isinstance(vital_signs, dict):
            vital_signs = {}
            
        # Llamar a la función core
        # Nota: llamar_modelo_gemini devuelve (response_data, final_prompt)
        response_data, _ = llamar_modelo_gemini(
            motivo=motivo,
            edad=edad,
            dolor=dolor,
            vital_signs=vital_signs,
            antecedentes=antecedentes,
            user_id="api_user"
        )
        
        # Validar error
        if response_data.get("status") == "ERROR":
            raise ValueError(response_data.get("msg", "Unknown error in AI Service"))
            
        # Devolver estructura limpia
        return {
            "nivel_sugerido": response_data.get("nivel_sugerido", 5),
            "razonamiento": response_data.get("razonamiento", "Sin razonamiento"),
            "color_hex": response_data.get("color_hex", "#gray"),
            "protocolo_aplicado": response_data.get("protocolo", "Gemini-Standard"),
            "razones": response_data.get("razones", [])
        }
