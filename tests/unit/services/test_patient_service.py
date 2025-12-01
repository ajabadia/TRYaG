import pytest
from datetime import datetime
from src.services.patient_service import (
    validar_dni, 
    generar_codigo_paciente, 
    crear_paciente, 
    buscar_paciente_existente
)
from unittest.mock import MagicMock, patch

def test_validar_dni():
    assert validar_dni("12345678Z") == True  # 12345678 % 23 = 14 -> Z
    assert validar_dni("12345678A") == False # Incorrect letter
    assert validar_dni("12345") == False     # Too short
    assert validar_dni(None) == False

def test_generar_codigo_paciente():
    codigo = generar_codigo_paciente(
        nombre="Juan",
        apellido1="Perez",
        apellido2="Garcia",
        num_ss="1234567890",
        num_identificacion="12345678Z"
    )
    # J (Juan) + P (Perez) + G (Garcia) + 2 digits
    assert len(codigo) == 5
    assert codigo.startswith("JPG")
    assert codigo[3:].isdigit()

@pytest.fixture(autouse=True)
def patch_patient_service_db(mock_db):
    with patch('src.services.patient_service.get_database', return_value=mock_db):
        yield

def test_crear_paciente_success(mock_db):
    # No need to mock return_value, mongomock handles it
    
    person_data, warning = crear_paciente(
        nombre="Test",
        apellido1="User",
        apellido2=None,
        fecha_nacimiento=datetime(1990, 1, 1),
        num_ss="1111111111",
        num_identificacion="12345678Z",
        tipo_identificacion="DNI"
    )

    assert person_data["nombre"] == "Test"
    assert person_data["activo"] == True
    assert warning is None
    
    # Verify insertion in mock db
    saved_person = mock_db.people.find_one({"num_ss": "1111111111"})
    assert saved_person is not None
    assert saved_person["nombre"] == "Test"

def test_crear_paciente_duplicate_ss(mock_db):
    # Insert existing patient
    mock_db.people.insert_one({
        "nombre": "Existing",
        "num_ss": "1111111111",
        "activo": True
    })

    with pytest.raises(ValueError, match="Ya existe un paciente con el número de SS"):
        crear_paciente(
            nombre="Test",
            apellido1="User",
            apellido2=None,
            fecha_nacimiento=datetime(1990, 1, 1),
            num_ss="1111111111",
            num_identificacion="12345678Z",
            tipo_identificacion="DNI"
        )

def test_buscar_paciente_existente(mock_db):
    # Insert patient to find
    mock_db.people.insert_one({
        "nombre": "Found",
        "num_ss": "123",
        "activo": True,
        "identificaciones": [] 
    })
    
    result = buscar_paciente_existente(num_ss="123")
    assert result is not None
    assert result["nombre"] == "Found"
