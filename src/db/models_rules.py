from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional, Union, Dict, Any, Annotated
from datetime import datetime
from enum import Enum
from bson import ObjectId

# Helper for Pydantic V2 + MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class LogicOperator(str, Enum):
    AND = "AND"
    OR = "OR"

class ConditionOperator(str, Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"

class ActionType(str, Enum):
    ALERT = "ALERT"
    HIGHLIGHT = "HIGHLIGHT"
    SUGGEST = "SUGGEST"

class RuleCondition(BaseModel):
    field: Optional[str] = None # e.g., "vital_signs.temperature"
    operator: Optional[ConditionOperator] = None
    value: Optional[Any] = None # 38.0, "dolor", etc.
    logic: Optional[LogicOperator] = None # For nested groups
    rules: Optional[List['RuleCondition']] = None # Nested rules

class RuleAction(BaseModel):
    type: ActionType
    # For ALERT
    level: Optional[str] = "info" # info, warning, critical
    message: Optional[str] = None
    # For HIGHLIGHT
    fields: Optional[List[str]] = None
    # For SUGGEST
    protocol: Optional[str] = None

class RuleStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class UIRule(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    name: str 
    description: Optional[str] = ""
    version: int = 1
    status: RuleStatus = RuleStatus.DRAFT
    conditions: RuleCondition
    actions: List[RuleAction]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = "system"


class UIField(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    internal_name: str # The key used in code (e.g. "vital_signs.temperature")
    display_name: Dict[str, str] = Field(default_factory=dict) # e.g. {"es": "Temperatura"}
    help_text: Dict[str, str] = Field(default_factory=dict)
    modules: List[str] = Field(default_factory=list) # Which files use this field
    data_type: str = "text" # text, number, boolean
    status: str = "active" # active, deprecated
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
        arbitrary_types_allowed = True

