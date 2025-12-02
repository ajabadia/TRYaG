# path: tests/unit/test_ptr_logic.py
import pytest
from src.components.triage.ptr_logic import calculate_ptr_score

def test_ptr_score_normal():
    """Test con valores normales (Score 0)"""
    vital_signs = {
        'gcs': 15,
        'spo2': 98,
        'pas': 120,
        'fr': 16,
        'fc': 80,
        'temp': 36.5,
        'dolor': 0
    }
    context = {}
    
    result = calculate_ptr_score(vital_signs, context)
    assert result['score'] == 0
    assert result['color'] == 'green'

def test_ptr_score_critical():
    """Test con valores críticos (Score alto)"""
    vital_signs = {
        'gcs': 8,       # Base 3 * 4 = 12
        'spo2': 85,     # Base 3 * 3 = 9
    }
    context = {}
    
    result = calculate_ptr_score(vital_signs, context)
    assert result['score'] >= 21
    assert result['color'] == 'red'

def test_ptr_geriatric_context():
    """Test ajuste por contexto geriátrico (FC x2)"""
    vital_signs = {
        'fc': 105 # Base 1 (Taquicardia leve: 100-110)
    }
    
    # Sin contexto (x1)
    res_normal = calculate_ptr_score(vital_signs, {})
    assert res_normal['score'] == 1 # 1 * 1
    
    # Con contexto (x2)
    res_geriatric = calculate_ptr_score(vital_signs, {'criterio_geriatrico': True})
    assert res_geriatric['score'] == 2 # 1 * 2

def test_ptr_immuno_context():
    """Test ajuste por contexto inmuno (Temp x3)"""
    vital_signs = {
        'temp': 38.5 # Base 1 (Fiebre)
    }
    
    # Sin contexto (x1)
    res_normal = calculate_ptr_score(vital_signs, {})
    assert res_normal['score'] == 1
    
    # Con contexto (x3)
    res_immuno = calculate_ptr_score(vital_signs, {'criterio_inmunodeprimido': True})
    assert res_immuno['score'] == 3
