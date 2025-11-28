# path: src/db/repositories/funciones.py
# Creado: 2025-11-25
# Modificado: 2025-11-27 (Persistencia DB)
"""
Repositorio de Funciones del personal.
Maneja la colección 'funciones' en MongoDB, con fallback a valores por defecto.
"""
from typing import List, Dict, Optional
from src.db.connection import get_database
from datetime import datetime

DEFAULT_FUNCIONES = [
    {
        "code": "administrativo",
        "nombre": "Administrativo",
        "descripcion": "Personal administrativo de admisión",
        "color": "#6C757D",
        "icon": "badge",
        "tipos_sala_compatibles": ["admision", "espera"]
    },
    {
        "code": "enfermero",
        "nombre": "Enfermero/a",
        "descripcion": "Personal de enfermería",
        "color": "#17A2B8",
        "icon": "medical_services",
        "tipos_sala_compatibles": ["triaje", "box", "consulta_ingreso"]
    },
    {
        "code": "medico",
        "nombre": "Médico/a",
        "descripcion": "Personal médico",
        "color": "#28A745",
        "icon": "health_and_safety",
        "tipos_sala_compatibles": ["triaje", "box", "consulta_ingreso", "observacion"]
    },
    {
        "code": "analista_datos",
        "nombre": "Analista de Datos",
        "descripcion": "Análisis y auditoría",
        "color": "#FFC107",
        "icon": "analytics",
        "tipos_sala_compatibles": []
    }
]

class FuncionesRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.funciones
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Inicializa las funciones por defecto si la colección está vacía."""
        if self.collection.count_documents({}) == 0:
            for func in DEFAULT_FUNCIONES:
                func_data = func.copy()
                func_data["created_at"] = datetime.now()
                func_data["updated_at"] = datetime.now()
                self.collection.insert_one(func_data)

    def get_all_funciones(self) -> List[Dict]:
        """Retorna todas las funciones."""
        return list(self.collection.find({}))

    def get_funcion_by_code(self, code: str) -> Optional[Dict]:
        """Obtiene una función por su código."""
        return self.collection.find_one({"code": code})

    def create_funcion(self, funcion_data: Dict) -> bool:
        """Crea una nueva función."""
        if self.get_funcion_by_code(funcion_data.get("code")):
            return False
        
        funcion_data["created_at"] = datetime.now()
        funcion_data["updated_at"] = datetime.now()
        self.collection.insert_one(funcion_data)
        return True

_funciones_repo = None

def get_funciones_repository() -> FuncionesRepository:
    global _funciones_repo
    if _funciones_repo is None:
        _funciones_repo = FuncionesRepository()
    return _funciones_repo

# Funciones helper para mantener compatibilidad
def get_all_funciones() -> List[Dict]:
    return get_funciones_repository().get_all_funciones()

def get_funcion_by_code(code: str) -> Optional[Dict]:
    return get_funciones_repository().get_funcion_by_code(code)
