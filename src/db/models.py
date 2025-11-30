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
    model: Optional[str] = Field(default=None, description="Modelo de IA asociado a esta versión")
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
                "model": "gemini-1.5-flash",
                "author": "admin",
                "notes": "Versión inicial",
                "status": "active"
            }
        }


class AIAuditLog(BaseModel):
    """Registro de auditoría de llamadas a la IA."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    timestamp_start: datetime = Field(default_factory=datetime.now)
    timestamp_end: Optional[datetime] = None
    duration_ms: Optional[float] = None
    
    # Contexto de llamada
    caller_id: str = Field(..., description="Identificador del proceso llamante (ej: triage_service)")
    user_id: str = Field(default="system", description="Usuario que inició la acción")
    call_type: str = Field(..., description="Tipo de llamada (triage, transcription, predictive, simulation, test)")
    
    # Configuración usada
    prompt_type: str = Field(..., description="Tipo de prompt usado")
    prompt_version_id: Optional[str] = None
    model_name: str = Field(..., description="Modelo de IA utilizado")
    
    # Payload
    raw_prompt: str = Field(..., description="Prompt enviado (crudo)")
    raw_response: str = Field(..., description="Respuesta recibida (cruda)")
    
    # Resultado
    status: Literal["success", "error"] = Field(..., description="Estado de la llamada")
    error_msg: Optional[str] = None
    
    # Metadata extra
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}



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
# TRIAGE MODELS
# ============================================================================

class VitalSignSeverityRange(BaseModel):
    """Rango de gravedad para un signo vital."""
    min_val: float = Field(..., description="Valor mínimo del rango (inclusive)")
    max_val: float = Field(..., description="Valor máximo del rango (inclusive)")
    color: str = Field(..., description="Color asociado (green, yellow, orange, red, black)")
    priority: int = Field(..., description="Prioridad numérica (0=Baja, 4=Extrema)")
    label: str = Field(..., description="Etiqueta (ej: Normal, Taquicardia Leve)")

class VitalSignAgeConfig(BaseModel):
    """Configuración de rangos para un grupo de edad específico."""
    min_age: int = Field(..., description="Edad mínima (años)")
    max_age: int = Field(..., description="Edad máxima (años)")
    
    # Límites absolutos (Validación de entrada)
    val_min: float = Field(..., description="Valor mínimo posible (para detectar errores)")
    val_max: float = Field(..., description="Valor máximo posible (para detectar errores)")
    
    # Rango Normal (Clínico - Verde) - Redundante con ranges pero útil para referencia rápida
    normal_min: float = Field(..., description="Mínimo considerado normal")
    normal_max: float = Field(..., description="Máximo considerado normal")
    
    # Valor por defecto (Media)
    default_value: float = Field(..., description="Valor medio por defecto")
    
    # Rangos de Gravedad Detallados
    ranges: List[VitalSignSeverityRange] = Field(default_factory=list, description="Lista de rangos de gravedad")

class VitalSignReference(BaseModel):
    """Referencia completa para un signo vital."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(..., description="Nombre del signo vital (ej: FC)")
    key: str = Field(..., description="Clave interna (ej: fc)")
    unit: str = Field(..., description="Unidad de medida (ej: ppm)")
    configs: List[VitalSignAgeConfig] = Field(default_factory=list, description="Configuraciones por edad")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class VitalSigns(BaseModel):
    """Signos vitales del paciente."""
    fc: Optional[int] = Field(default=None, description="Frecuencia Cardíaca (ppm)")
    pas: Optional[int] = Field(default=None, description="Presión Arterial Sistólica (mmHg)")
    pad: Optional[int] = Field(default=None, description="Presión Arterial Diastólica (mmHg)")
    spo2: Optional[int] = Field(default=None, description="Saturación de Oxígeno (%)")
    temp: Optional[float] = Field(default=None, description="Temperatura (°C)")
    fr: Optional[int] = Field(default=None, description="Frecuencia Respiratoria (rpm)")
    gcs: Optional[int] = Field(default=None, description="Escala de Coma de Glasgow (3-15)")
    eva: Optional[int] = Field(default=None, description="Escala Visual Analógica de Dolor (0-10)")
    pupilas: Optional[Literal["Normal", "Lenta", "Fijas", "Anisocoria", "Puntiformes"]] = Field(default=None)
    oxigeno_suplementario: bool = Field(default=False, description="¿Usa oxígeno suplementario?")
    
    # Metadata adicional
    notas: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.now)

class TriageRangeConfig(BaseModel):
    """Configuración de rangos para un signo vital."""
    metric: str = Field(..., description="Nombre de la métrica (fc, pas, spo2, etc.)")
    red_min: Optional[float] = None
    red_max: Optional[float] = None
    orange_min: Optional[float] = None
    orange_max: Optional[float] = None
    yellow_min: Optional[float] = None
    yellow_max: Optional[float] = None
    green_min: Optional[float] = None
    green_max: Optional[float] = None
    
    # Para valores discretos (ej: pupilas)
    red_values: List[str] = Field(default_factory=list)
    orange_values: List[str] = Field(default_factory=list)
    yellow_values: List[str] = Field(default_factory=list)


# ============================================================================
# TRIAGE RECORDS (antes audit_records)
# ============================================================================

class TriageRecord(BaseModel):
    """Registro de un triaje realizado."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    audit_id: str = Field(..., description="ID único del registro (ej: AUD-20251123-001)")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Datos del Paciente (Snapshot)
    patient_id: Optional[str] = Field(default=None, description="ID del paciente (si existe)")
    patient_age: Optional[int] = Field(default=None)
    
    # Datos Clínicos
    vital_signs: Optional[VitalSigns] = Field(default=None, description="Signos vitales registrados")
    sintomas_detectados: List[str] = Field(default_factory=list)
    
    # Resultado Triaje
    sugerencia_ia: Dict[str, Any] = Field(..., description="Respuesta completa de la IA")
    nivel_sugerido: Optional[int] = Field(default=None, ge=1, le=5, description="Nivel sugerido por IA (1-5)")
    color_sugerido: Optional[str] = Field(default=None, description="Color sugerido (Rojo, Naranja, etc.)")
    
    # Decisión Final
    nivel_final: Optional[int] = Field(default=None, ge=1, le=5)
    color_final: Optional[str] = Field(default=None)
    motivo_urgencia: Optional[str] = Field(default=None, description="Motivo principal de la clasificación")
    
    # Auditoría y Control
    decision_humana: Optional[str] = Field(default=None, description="Si hubo cambio manual")
    justificacion: Optional[str] = Field(default=None)
    evaluator_id: Optional[str] = Field(default=None, description="ID del usuario que realiza el triaje")
    
    # Reevaluación
    is_reevaluation: bool = Field(default=False)
    parent_triage_id: Optional[str] = Field(default=None, description="ID del triaje anterior si es reevaluación")
    
    # Metadata IA
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


# ============================================================================
# CLINICAL OPTIONS
# ============================================================================

class ClinicalOption(BaseModel):
    """Opción clínica configurable (Alergias, Patologías, etc.)."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    category: str = Field(..., description="Categoría (allergy_agent, pathology, etc.)")
    value: str = Field(..., description="Valor interno")
    label: str = Field(..., description="Etiqueta visible")
    risk_level: Optional[str] = Field(default=None, description="Nivel de riesgo asociado (ej: high)")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="Metadatos adicionales")
    active: bool = Field(default=True)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# SALAS
# ============================================================================

class Sala(BaseModel):
    """Modelo de Sala (normalizado)."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    codigo: str = Field(..., description="Código único de la sala (ej: ADM-01)")
    centro_id: str = Field(..., description="ID del centro al que pertenece")
    nombre: str = Field(..., description="Nombre descriptivo")
    tipo: Literal["admision", "triaje", "box", "consulta_ingreso", "espera", "otro"] = Field(..., description="Tipo de sala")
    subtipo: Optional[Literal["atencion", "espera"]] = Field(default="atencion")
    
    # Capacidad y Estado
    capacidad: int = Field(default=1, ge=0)
    activa: bool = Field(default=True)
    
    # Detalles adicionales (migrados del array incrustado)
    horario_inicio: Optional[str] = Field(default="00:00")
    horario_fin: Optional[str] = Field(default="23:59")
    equipamiento: List[str] = Field(default_factory=list)
    notas: Optional[str] = Field(default=None)
    
    # Relaciones
    salas_espera_asociadas: List[str] = Field(default_factory=list, description="Códigos de salas de espera asociadas")
    salas_atencion_asociadas: List[str] = Field(default_factory=list, description="Códigos de salas de atención asociadas")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: str = Field(default="admin")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

