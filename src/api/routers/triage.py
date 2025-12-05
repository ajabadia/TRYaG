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
        # Mapear input a estructura esperada por TriageService
        vitals_dict = request.signos_vitales.dict() if request.signos_vitales else {}
        
        # Instanciar servicio (stateless por ahora para la API)
        service = TriageService()
        
        # Llamar al método de análisis (adaptar según firma real de analyze_case)
        # Nota: TriageService.analyze_case espera un objeto TriageRecord o similar.
        # Para esta fase inicial, usaremos una lógica simplificada o wrapper si es necesario.
        # Asumiremos que podemos llamar a la lógica interna.
        
        # SIMULACIÓN para la Fase 12.1 hasta refactorizar TriageService para aceptar DTOs puros
        # TODO: Refactorizar TriageService para separar lógica de modelos de BD
        
        # Lógica temporal (Mock inteligente basado en reglas para no romper)
        priority = 5
        reason = "Consulta estándar"
        
        if request.dolor > 7:
            priority = 3
            reason = "Dolor severo indica urgencia."
        
        if request.signos_vitales:
            if request.signos_vitales.saturacion and request.signos_vitales.saturacion < 90:
                priority = 2
                reason = "Hipoxia detectada."
        
        return {
            "nivel_sugerido": priority,
            "razonamiento": reason,
            "color_hex": "#0000FF" if priority == 5 else "#FF0000", # Simplificado
            "protocolo_aplicado": "Standard-API-v1"
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
