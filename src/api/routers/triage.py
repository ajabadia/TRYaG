from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.services.triage_service import TriageService
from src.services.predictive_service import PredictiveService

router = APIRouter()

# --- Schemas ---
class VitalSignsInput(BaseModel):
    sistolica: Optional[int] = None
    diastolica: Optional[int] = None
    frecuencia_cardiaca: Optional[int] = None
    saturacion: Optional[int] = None
    temperatura: Optional[float] = None
    glasgow: Optional[int] = 15

class TriageAnalysisRequest(BaseModel):
    motivo_consulta: str
    signos_vitales: Optional[VitalSignsInput] = None
    edad: int
    dolor: int = Field(..., ge=0, le=10)
    antecedentes: Optional[str] = ""

class TriageAnalysisResponse(BaseModel):
    nivel_sugerido: int
    razonamiento: str
    color_hex: str
    protocolo_aplicado: str

class RiskPredictionRequest(BaseModel):
    signos_vitales: VitalSignsInput
    edad: int

class RiskPredictionResponse(BaseModel):
    ptr_score: float
    risk_level: str
    recommendation: str

# --- Endpoints ---

@router.post("/analyze", response_model=TriageAnalysisResponse)
async def analyze_triage(request: TriageAnalysisRequest):
    """
    Analiza un caso de triaje utilizando la lógica del TriageService.
    Ahora incluye simulaciones de IA si no está disponible el modelo real en este contexto.
    """
    try:
        # Prepare request dictionary
        request_dict = request.model_dump() # Pydantic v2
        
        # Instantiate service
        service = TriageService()
        
        # Execute analysis using Real logic
        result = service.analyze_case(request_dict)
        
        # Map result to response schema
        return {
            "nivel_sugerido": result.get("nivel_sugerido"),
            "razonamiento": result.get("razonamiento"),
            "color_hex": result.get("color_hex"),
            "protocolo_aplicado": result.get("protocolo_aplicado", "Gemini-Standard")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/risk", response_model=RiskPredictionResponse)
async def calculate_risk(request: RiskPredictionRequest):
    """
    Calcula el PTR (Patient Triage Risk) basado en signos vitales.
    """
    try:
        service = PredictiveService()
        # Convertir a dict para el servicio
        data = {
            "sistolica": request.signos_vitales.sistolica,
            "frecuencia_cardiaca": request.signos_vitales.frecuencia_cardiaca,
            "saturacion": request.signos_vitales.saturacion,
            "edad": request.edad
        }
        
        # Calcular
        score = service.calculate_ptr(data)
        
        level = "Bajo"
        rec = "Monitorización estándar"
        if score > 15:
            level = "Alto"
            rec = "Atención inmediata requerida"
        elif score > 5:
            level = "Medio"
            rec = "Reevaluación frecuente"
            
        return {
            "ptr_score": score,
            "risk_level": level,
            "recommendation": rec
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
