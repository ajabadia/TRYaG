# path: scripts/test_vital_signs_logic.py
import sys
import os
import streamlit as st

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock session state
if 'datos_paciente' not in st.session_state:
    st.session_state.datos_paciente = {'vital_signs': {}}

from src.components.triage.vital_signs_form import get_vital_sign_config, get_color_and_alert

def test_logic():
    print("Testing Vital Signs Logic...")
    
    # Test FC for Adult (40 years)
    age = 40
    metric = "fc"
    config = get_vital_sign_config(metric, age)
    
    if not config:
        print("❌ Config not found for FC age 40")
        return

    print(f"✅ Config found for FC age 40: Normal {config.normal_min}-{config.normal_max}, Limits {config.val_min}-{config.val_max}")
    
    # Test Normal
    val = 80
    color, alert = get_color_and_alert(val, config)
    print(f"Value {val}: Color={color}, Alert={alert}")
    assert color == "green"
    assert alert is None
    
    # Test Abnormal but Valid (Tachycardia)
    val = 120
    color, alert = get_color_and_alert(val, config)
    print(f"Value {val}: Color={color}, Alert={alert}")
    assert color == "orange"
    assert "Valor anormal" in alert
    
    # Test Invalid (Error)
    val = 400
    color, alert = get_color_and_alert(val, config)
    print(f"Value {val}: Color={color}, Alert={alert}")
    assert color == "red"
    assert "fuera de rango" in alert
    
    print("✅ All logic tests passed!")

if __name__ == "__main__":
    test_logic()
