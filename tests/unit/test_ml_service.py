# path: tests/unit/test_ml_service.py
import pytest
from datetime import date
from src.services.ml_predictive_service import MLPredictiveService

@pytest.fixture
def ml_service():
    return MLPredictiveService()

def test_predict_demand_structure(ml_service):
    """Verifica que la predicción de demanda devuelva la estructura correcta."""
    fecha = date.today()
    hora = 10
    sala = "SALA_01"
    
    result = ml_service.predict_demand(sala, fecha, hora)
    
    assert 'demanda_predicha' in result
    assert 'confianza' in result
    assert 'intervalo_min' in result
    assert 'intervalo_max' in result
    assert isinstance(result['demanda_predicha'], int)

def test_predict_wait_time_structure(ml_service):
    """Verifica la estructura de predicción de tiempo de espera."""
    sala = "SALA_01"
    pacientes = 5
    
    result = ml_service.predict_wait_time(sala, pacientes)
    
    assert 'tiempo_predicho_min' in result
    assert 'nivel_carga' in result
    assert result['pacientes_en_espera'] == 5

def test_load_level_logic(ml_service):
    """Verifica la lógica de niveles de carga."""
    assert ml_service._get_load_level(2) == 'baja'
    assert ml_service._get_load_level(8) == 'media'
    assert ml_service._get_load_level(15) == 'alta'
