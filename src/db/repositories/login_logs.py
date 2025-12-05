# path: src/db/repositories/login_logs.py
from db.repositories.base import BaseRepository
from db.models import LoginLog

class LoginLogsRepository(BaseRepository[LoginLog]):
    """Repositorio para logs de inicio de sesión."""
    
    def __init__(self):
        super().__init__(collection_name="login_logs")

    def log_login(self, user_id: str, username: str, success: bool = True, ip_address: str = None, details: dict = None):
        """Registra un evento de login."""
        log = LoginLog(
            user_id=str(user_id),
            username=username,
            action="login",
            success=success,
            ip_address=ip_address,
            details=details or {}
        )
        # Convert Pydantic model to dict for BaseRepository
        return self.create(log.model_dump(by_alias=True, exclude={"id"}))

    def log_logout(self, user_id: str, username: str, ip_address: str = None):
        """Registra un evento de logout."""
        log = LoginLog(
            user_id=str(user_id),
            username=username,
            action="logout",
            success=True,
            ip_address=ip_address
        )
        # Convert Pydantic model to dict for BaseRepository
        return self.create(log.model_dump(by_alias=True, exclude={"id"}))

_login_logs_repo = None

def get_login_logs_repository() -> LoginLogsRepository:
    global _login_logs_repo
    if _login_logs_repo is None:
        _login_logs_repo = LoginLogsRepository()
    return _login_logs_repo
