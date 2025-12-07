from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
from src.services.rag_service import RAGService
# from src.services.transcription_service import TranscriptionService # Import cuando esté listo para consumo externo

router = APIRouter()

class RAGQueryRequest(BaseModel):
    query: str
    limit: int = 3

class RAGContextResponse(BaseModel):
    documents: List[str]
    metadata: List[Dict[str, Any]] = []

@router.post("/rag/search", response_model=RAGContextResponse)
async def search_knowledge_base(request: RAGQueryRequest):
    """
    Busca contexto relevante en la base de conocimiento vectorial (RAG).
    """
    try:
        service = RAGService()
        
        # Usamos el método search_documents que devuelve metadata también
        results = service.search_documents(request.query, n_results=request.limit)
        
        docs = [r['content'] for r in results]
        metas = [r['metadata'] for r in results]
        
        return {
            "documents": docs,
            "metadata": metas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe un archivo de audio subido.
    (Placeholder para futura implementación con TranscriptionService)
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    return {
        "filename": file.filename,
        "transcription": "[Simulación] Paciente refiere dolor abdominal desde hace 3 horas...",
        "status": "simulated" # Marcar como simulado hasta conectar el servicio real que requiere API Keys
    }

class ReasoningRequest(BaseModel):
    patient_id: str
    query: str
    include_rag: bool = False

@router.post("/reasoning")
async def request_second_opinion(request: ReasoningRequest):
    """
    Solicita un análisis de segunda opinión (Reasoning ++).
    """
    try:
        from src.services.second_opinion_service import get_second_opinion_service
        service = get_second_opinion_service()
        
        result = service.request_analysis(
            patient_code=request.patient_id, 
            query_notes=request.query,
            include_rag=request.include_rag
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
