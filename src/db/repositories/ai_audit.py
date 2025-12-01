# path: src/db/repositories/ai_audit.py
from typing import Optional
from db.repositories.base import BaseRepository
from db.models import AIAuditLog

class AIAuditRepository(BaseRepository[AIAuditLog]):
    def __init__(self):
        super().__init__(collection_name="ai_audit_logs")

    def log_call(self, log_entry: AIAuditLog) -> str:
        """
        Registra una llamada a la IA.
        """
        return self.create(log_entry.model_dump(by_alias=True, exclude={"id"}))

_repo_instance = None

def get_ai_audit_repository() -> AIAuditRepository:
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = AIAuditRepository()
    return _repo_instance
