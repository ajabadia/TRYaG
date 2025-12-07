import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

# Services
from services.gemini_client import get_gemini_service
from db.repositories.prompts import get_prompts_repository
from db.repositories.people import get_people_repository
from db import get_database

class SecondOpinionService:
    """
    Servicio de Segunda Opinión (Reasoning ++).
    Agrega contexto masivo y consulta a modelos de IA avanzados.
    """

    def __init__(self):
        self.gemini = get_gemini_service()
        self.prompts_repo = get_prompts_repository()
        self.people_repo = get_people_repository()
        self.db = get_database()

    def _build_patient_context(self, patient_code: str, target_audit_ids: List[str] = None) -> Dict[str, Any]:
        """
        Construye el contexto clínico completo agregando fuentes de datos.
        """
        context = {}

        # 1. Datos Filiación (Basic)
        patient = self.people_repo.get_by_patient_code(patient_code)
        if patient:
            context["patient_profile"] = {
                "age": patient.get("edad"),
                "gender": patient.get("gender"),
                "background": patient.get("clinical_history", "No registrado")
            }

        # 3. Historial de Triajes (Vitals + Complaints + Files)
        # Si target_audit_ids es None, NO traemos ninguno por defecto (o lógica de UI)
        # Aunque la UI pasa la lista. Si es lista vacía, no trae nada.
        # Modificación: Filtro por IDs
        
        query = {"patient_id": patient_code}
        if target_audit_ids is not None:
             # Si pasamos una lista (vacía o llena), filtramos por ella.
             # Si no pasamos nada (None), comportamiento legacy? 
             # Mejor ser explícitos: la UI manda la lista.
             query["audit_id"] = {"$in": target_audit_ids}

        cursor = self.db["triage_records"].find(query).sort("timestamp", -1)
        
        triage_history = []
        for record in cursor:
            # Buscar archivos adjuntos (metadata)
            audit_id = record.get("audit_id")
            files_meta = []
            if audit_id:
                f_cursor = self.db["file_imports"].find({"audit_id": audit_id})
                for f in f_cursor:
                    files_meta.append(f"{f.get('filename')} ({f.get('file_type')})")
            
            triage_history.append({
                "audit_id": audit_id, # Needed for tracking
                "date": record.get("timestamp").isoformat(),
                "main_complaint": record.get("triage_result", {}).get("resumen_clinico", ""),
                "medical_text": record.get("patient_snapshot", {}).get("texto_medico", ""),
                "pain_level": record.get("patient_snapshot", {}).get("dolor", 0),
                "vitals": record.get("vital_signs", {}),
                "ai_level": record.get("triage_result", {}).get("nivel_triaje"),
                "ai_reasoning": record.get("triage_result", {}).get("razonamiento", ""),
                "ai_analysis_full": record.get("triage_result", {}), # Full AI object
                "allergies": record.get("patient_snapshot", {}).get("alergias", ""),
                "background_snapshot": record.get("patient_snapshot", {}).get("antecedentes", ""),
                "attached_files": files_meta
            })
        context["triage_history"] = triage_history

        # 4. Flujo Activo (Estado actual)
        active_flow = self.db["patient_flow"].find_one({"patient_code": patient_code, "activo": True})
        if active_flow:
            context["current_status"] = {
                "location": active_flow.get("sala_code"),
                "state": active_flow.get("estado"),
                "entry_time": active_flow.get("entrada").isoformat()
            }

        return context

    def get_available_triages(self, patient_code: str) -> List[Dict[str, Any]]:
        """
        Retorna lista ligera de triajes disponibles para selección.
        """
        cursor = self.db["triage_records"].find(
            {"patient_id": patient_code},
            {"audit_id": 1, "timestamp": 1, "triage_result.resumen_clinico": 1, "triage_result.nivel_triaje": 1}
        ).sort("timestamp", -1)
        
        results = []
        for doc in cursor:
            results.append({
                "audit_id": doc.get("audit_id"),
                "date": doc.get("timestamp"), # datetime object
                "summary": doc.get("triage_result", {}).get("resumen_clinico", "Sin motivo"),
                "level": doc.get("triage_result", {}).get("nivel_triaje", "?")
            })
        return results

    def request_analysis(self, patient_code: str, query_notes: str = "", include_rag: bool = False) -> Dict[str, Any]:
        """
        Solicita una análisis de segunda opinión, opcionalmente con RAG.
        Esta función centraliza la lógica para ser usada por API y UI.
        """
        from core.prompt_manager import PromptManager
        from services.rag_service import get_rag_service
        
        # 1. Recuperar contexto
        context = self._build_patient_context(patient_code)
        
        # 2. Configuración del Prompt
        pm = PromptManager()
        prompt_config = pm.get_active_prompt("second_opinion_reasoning")
        if not prompt_config:
             prompt_config = {"content": "Actúa como experto clínico...", "model": "gemini-1.5-flash"}
             
        system_instruction = prompt_config.get("content")
        model_name = prompt_config.get("model", "gemini-1.5-flash")
        
        # 3. RAG Lookup (si solicitado)
        rag_context = ""
        if include_rag and query_notes:
            rag_service = get_rag_service()
            docs = rag_service.search_context(query_notes, n_results=3)
            if docs:
                rag_context = "\n[MEMORIA INSTITUCIONAL (Protocolos Local)]:\n" + "\n".join(docs)
        
        # 4. Construir Prompt Final (Simplificado para API, la UI hace el suyo propio multimodal)
        # Nota: Para la API, asumimos texto. Si hay multimodalidad, se debe gestionar via API con archivos.
        full_prompt = f"{system_instruction}\n\nCONTEXTO:\n{json.dumps(context, default=str)}\n\nNOTA CLINICA:\n{query_notes}\n{rag_context}"
        
        # 5. Llamada a Gemini
        response = self.gemini.generate_content(model_name, full_prompt)
        
        return {
            "analysis": response if isinstance(response, str) else "Error format", # Simplificación, real sería parsear JSON
            "rag_used": bool(rag_context),
            "model_used": model_name
        }

    def get_active_configuration(self):
        """
        Recupera el prompt y modelo activos desde PromptManager.
        """
        from core.prompt_manager import PromptManager
        pm = PromptManager()
        prompt_config = pm.get_active_prompt("second_opinion_reasoning")
        
        if prompt_config:
            return {
                "content": prompt_config.get("content"),
                "model": prompt_config.get("model", "gemini-1.5-flash")
            }
        else:
            return {
                "content": "Actúa como experto clínico...",
                "model": "gemini-1.5-flash"
            }

# Singleton
_service = None
def get_second_opinion_service():
    global _service
    if _service is None:
        _service = SecondOpinionService()
    return _service
