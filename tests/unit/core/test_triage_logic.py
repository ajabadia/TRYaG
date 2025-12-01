import pytest
from unittest.mock import MagicMock, patch
from src.services.triage_service import llamar_modelo_gemini

@pytest.fixture
def mock_dependencies():
    with patch('src.services.triage_service.PromptManager') as mock_pm, \
         patch('src.services.triage_service.get_gemini_service') as mock_gemini:
        yield mock_pm, mock_gemini

def test_llamar_modelo_gemini_basic(mock_dependencies):
    mock_pm, mock_gemini = mock_dependencies
    
    # Setup PromptManager
    mock_pm.return_value.get_prompt.return_value = {
        "content": "Analiza: {motivo}, Edad: {edad}, Dolor: {dolor}, VS: {signos_vitales}",
        "version_id": "v1",
        "model": "gemini-test"
    }
    
    # Setup Gemini Service
    mock_gemini.return_value.generate_content.return_value = ({"nivel_sugerido": 3}, "raw_prompt")
    
    response, final_prompt = llamar_modelo_gemini(
        motivo="Dolor de cabeza",
        edad=30,
        dolor=5
    )
    
    # Verify prompt construction
    assert "Analiza: Dolor de cabeza" in final_prompt
    assert "Edad: 30" in final_prompt
    assert "Dolor: 5" in final_prompt
    assert "VS: No registrados" in final_prompt
    
    # Verify service call
    mock_gemini.return_value.generate_content.assert_called_once()
    call_kwargs = mock_gemini.return_value.generate_content.call_args[1]
    assert call_kwargs["model_name"] == "gemini-test"

def test_llamar_modelo_gemini_with_vitals(mock_dependencies):
    mock_pm, mock_gemini = mock_dependencies
    mock_pm.return_value.get_prompt.return_value = {"content": "{signos_vitales}", "version_id": "v1"}
    mock_gemini.return_value.generate_content.return_value = ({}, "")
    
    vital_signs = {"tension": "120/80", "fc": 80}
    triage_result = {"label": "Normal", "final_priority": 4}
    
    _, final_prompt = llamar_modelo_gemini(
        motivo="Checkup", edad=30, dolor=0,
        vital_signs=vital_signs,
        triage_result=triage_result
    )
    
    assert "TENSION: 120/80" in final_prompt
    assert "FC: 80" in final_prompt
    assert "Clasificación Global: Normal" in final_prompt

def test_llamar_modelo_gemini_contexto_critico(mock_dependencies):
    mock_pm, mock_gemini = mock_dependencies
    mock_pm.return_value.get_prompt.return_value = {"content": "{motivo}", "version_id": "v1"}
    mock_gemini.return_value.generate_content.return_value = ({}, "")
    
    _, final_prompt = llamar_modelo_gemini(
        motivo="Fiebre", edad=70, dolor=0,
        criterio_geriatrico=True,
        criterio_inmunodeprimido=True
    )
    
    assert "PACIENTE GERIÁTRICO" in final_prompt
    assert "PACIENTE INMUNODEPRIMIDO" in final_prompt

def test_llamar_modelo_gemini_exclusion(mock_dependencies):
    mock_pm, mock_gemini = mock_dependencies
    mock_pm.return_value.get_prompt.return_value = {"content": "...", "version_id": "v1"}
    
    # Simulate exclusion response (Level 0)
    mock_gemini.return_value.generate_content.return_value = (
        {"nivel_sugerido": 0, "razonamiento": ["No es trauma"]}, 
        ""
    )
    
    response, _ = llamar_modelo_gemini("Dolor", 20, 0)
    
    assert response["status"] == "EXCLUDED"
    assert "No es trauma" in response["msg"]
