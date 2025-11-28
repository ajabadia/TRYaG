# path: src/db/models.py
"""
Modelos Pydantic para validación de datos de MongoDB.

Estos modelos definen la estructura de los documentos en cada colección
y proporcionan validación automática de datos.
"""
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Tipo personalizado para ObjectId de MongoDB compatible con Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, *args):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# ============================================================================
# PROMPTS
# ============================================================================

class PromptVersion(BaseModel):
    """Versión individual de un prompt."""
    version_id: str = Field(..., description="ID de la versión (ej: v1, v2)")
    content: str = Field(..., description="Contenido del prompt")
    author: str = Field(default="admin", description="Autor de la versión")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    updated_by: str = Field(default="admin", description="Usuario de última modificación")
    notes: str = Field(default="", description="Notas sobre esta versión")
    status: Literal["draft", "active", "deprecated"] = Field(default="draft")
    
    class Config:
        json_schema_extra = {
            "example": {
                "version_id": "v1",
                "content": "Actúa como un experto...",
                "author": "admin",
                "notes": "Versión inicial",
                "status": "active"
            }
        }


class Prompt(BaseModel):
    """Documento de prompt con todas sus versiones."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    prompt_type: Literal["triage_gemini", "triage_sim", "transcription"]
    active_version: Optional[str] = Field(default=None, description="ID de la versión activa")
    versions: List[PromptVersion] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# TRIAGE RECORDS (antes audit_records)
# ============================================================================

class TriageRecord(BaseModel):
    """Registro de un triaje realizado."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    audit_id: str = Field(..., description="ID único del registro (ej: AUD-20251123-001)")
    timestamp: datetime = Field(default_factory=datetime.now)
    sugerencia_ia: Dict[str, Any] = Field(..., description="Respuesta completa de la IA")
    nivel_corregido: Optional[int] = Field(default=None, ge=0, le=5)
    decision_humana: Optional[str] = Field(default=None)
    justificacion: Optional[str] = Field(default=None)
    prompt_type: str = Field(default="triage_gemini")
    prompt_version: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# FILE IMPORTS RECORDS
# ============================================================================

class FileImportRecord(BaseModel):
    """Registro de un archivo importado."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    file_id: str = Field(..., description="ID único del archivo")
    timestamp: datetime = Field(default_factory=datetime.now)
    filename: str
    file_type: str = Field(..., description="MIME type del archivo")
    file_size: int = Field(..., ge=0, description="Tamaño en bytes")
    audit_id: Optional[str] = Field(default=None, description="Referencia al registro de auditoría")
    thumbnail_base64: Optional[str] = Field(default=None, description="Miniatura en base64")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# TRANSCRIPTIONS RECORDS
# ============================================================================

class TranscriptionRecord(BaseModel):
    """Registro de una transcripción de audio."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    transcription_id: str = Field(..., description="ID único de la transcripción")
    timestamp: datetime = Field(default_factory=datetime.now)
    original_text: str
    language_code: str = Field(..., max_length=10)
    language_name: str
    translated_text: str
    emotional_prosody: Optional[str] = Field(default=None, description="Tono emocional detectado por la IA")
    relevance: Optional[int] = Field(default=None, ge=0, le=9, description="Relevancia clínica (0-9)")
    audio_duration: Optional[float] = Field(default=None, ge=0, description="Duración en segundos")
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# PROMPT TESTS
# ============================================================================

class PromptTest(BaseModel):
    """Registro de una prueba de prompt."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    test_id: str = Field(..., description="ID único de la prueba")
    timestamp: datetime = Field(default_factory=datetime.now)
    user: str = Field(default="admin")
    prompt_type: str
    version_id: str
    model: str
    rating: int = Field(..., ge=0, le=1, description="0=dislike, 1=like")
    prompt_content: str = Field(..., description="Prompt completo enviado a la IA")
    test_input: str = Field(..., description="Input de prueba usado")
    response: Dict[str, Any] = Field(..., description="Respuesta completa de la IA")
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# CONFIG
# ============================================================================

class ConfigItem(BaseModel):
    """Item de configuración general."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    key: str = Field(..., description="Clave única de configuración")
    value: Any = Field(..., description="Valor de la configuración")
    description: Optional[str] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: str = Field(default="admin")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# PATIENTS & ADMISSION
# ============================================================================

class ContactInfo(BaseModel):
    """Información de contacto del paciente."""
    type: Literal["email", "phone", "mobile", "emergency_contact"] = Field(..., description="Tipo de contacto")
    value: str = Field(..., description="Valor del contacto (email, teléfono, etc.)")
    primary: bool = Field(default=False, description="Si es el contacto principal")
    notes: Optional[str] = Field(default=None, description="Notas adicionales")



class Identificacion(BaseModel):
    """Documento de identificación."""
    type: Literal["DNI", "NIE", "PASAPORTE", "OTRO"] = Field(..., description="Tipo de documento")
    value: str = Field(..., description="Número de documento")
    created_at: datetime = Field(default_factory=datetime.now)
    inactive_at: Optional[datetime] = Field(default=None, description="Fecha de baja si está inactivo")

class Person(BaseModel):
    """
    Modelo unificado de Persona (Pacientes + Usuarios + Empleados).
    Sustituye a la antigua colección 'patients'.
    """
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    
    # Datos Personales Básicos
    nombre: str = Field(..., min_length=1)
    apellido1: str = Field(..., min_length=1)
    apellido2: Optional[str] = Field(default=None)
    fecha_nacimiento: Optional[datetime] = Field(default=None)
    gender: Optional[str] = Field(default=None)
    
    # Identificación (Múltiple)
    identificaciones: List[Identificacion] = Field(default_factory=list)
    
    # Datos de Contacto
    contact_info: List[ContactInfo] = Field(default_factory=list)
    
    # Datos Clínicos / Paciente
    patient_code: Optional[str] = Field(default=None, description="Código único de paciente (si aplica)")
    num_ss: Optional[str] = Field(default=None, description="Número SS")
    
    # Datos Corporativos (si es empleado)
    internal_id: Optional[str] = Field(default=None, description="ID de empleado")
    
    # Metadata
    activo: bool = Field(default=True, description="Si el registro está activo")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @field_validator('patient_code')
    @classmethod
    def validate_patient_code(cls, v):
        if v:
            return v.upper()
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class PatientFlow(BaseModel):
    """Modelo de flujo de paciente (un documento por cada paso/movimiento)."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    flow_id: str = Field(..., description="ID único del flujo completo (compartido por todos los pasos)")
    patient_code: str = Field(..., description="Código del paciente")
    secuencia: int = Field(..., description="Número de secuencia del paso (1, 2, 3...)")
    
    sala_code: str = Field(..., description="Código de la sala actual")
    sala_tipo: str = Field(..., description="Tipo de sala (admision, triaje, box, etc.)")
    sala_subtipo: Optional[str] = Field(default=None, description="Subtipo (espera, atencion)")
    
    estado: str = Field(..., description="Estado en este paso (EN_ADMISION, EN_ESPERA_TRIAJE, etc.)")
    activo: bool = Field(default=True, description="Si es el paso actual del paciente")
    
    entrada: datetime = Field(default_factory=datetime.now, description="Fecha/hora de entrada a este paso")
    salida: Optional[datetime] = Field(default=None, description="Fecha/hora de salida de este paso")
    duracion_minutos: Optional[int] = Field(default=None, description="Duración en minutos")
    
    notas: Optional[str] = Field(default=None)
    usuario: str = Field(default="admin")
    motivo_rechazo: Optional[str] = Field(default=None)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


# ============================================================================
# TURNOS
# ============================================================================

class Turno(BaseModel):
    """Modelo de turno de trabajo."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str = Field(..., description="ID del usuario (ObjectId string)")
    sala_code: str = Field(..., description="Código de la sala asignada")
    fecha_desde: datetime = Field(..., description="Fecha inicio turno")
    fecha_hasta: datetime = Field(..., description="Fecha fin turno")
    horario_inicio: str = Field(..., description="Hora inicio (HH:MM)")
    horario_fin: str = Field(..., description="Hora fin (HH:MM)")
    notas: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
