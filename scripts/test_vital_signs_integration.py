# path: scripts/test_vital_signs_integration.py
import sys
import os
from unittest.mock import MagicMock

# Añadir el directorio raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.triage_service import llamar_modelo_gemini
from src.components.triage.vital_signs_form import get_color_for_value

def test_color_logic():
    print("--- Testing Color Logic ---")
    # Test FC
    assert get_color_for_value(80, "fc") == "green"
    assert get_color_for_value(130, "fc") == "orange"
    assert get_color_for_value(150, "fc") == "red"
    print("FC Colors: OK")
    
    # Test SpO2
    assert get_color_for_value(98, "spo2") == "green"
    assert get_color_for_value(91, "spo2") == "orange"
    assert get_color_for_value(85, "spo2") == "red"
    print("SpO2 Colors: OK")

def test_service_integration():
    print("\n--- Testing Service Integration ---")
    
    # Mock get_model_triage and PromptManager
    import src.services.triage_service as service
    service.get_model_triage = MagicMock(return_value="gemini-pro")
    
    # Mock GenerativeModel
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.parts = True
    mock_response.text = '{"nivel_sugerido": 2, "razonamiento": ["SpO2 bajo"]}'
    mock_model.generate_content.return_value = mock_response
    
    import google.generativeai as genai
    genai.GenerativeModel = MagicMock(return_value=mock_model)
    
    # Mock PromptManager
    sys.modules['src.core.prompt_manager'] = MagicMock()
    mock_pm = MagicMock()
    mock_pm.get_prompt.return_value = {"content": "Analiza: {motivo}, {edad}, {dolor}. Signos: {signos_vitales}"}
    sys.modules['src.core.prompt_manager'].PromptManager = MagicMock(return_value=mock_pm)
    
    # Call service
    vital_signs = {"fc": 120, "spo2": 88}
    result, prompt = llamar_modelo_gemini("Dolor pecho", 50, 8, vital_signs=vital_signs)
    
    print(f"Generated Prompt: {prompt}")
    
    # Verify prompt contains vital signs
    if "FC: 120" in prompt and "SPO2: 88" in prompt:
        print("Vital signs successfully injected into prompt.")
    else:
        print("ERROR: Vital signs NOT found in prompt.")

if __name__ == "__main__":
    try:
        test_color_logic()
        test_service_integration()
        print("\nIntegration tests completed.")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
