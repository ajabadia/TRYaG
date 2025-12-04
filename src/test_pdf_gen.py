import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import streamlit as st
from unittest.mock import MagicMock

# Mock streamlit session state
if not hasattr(st, 'session_state'):
    st.session_state = {}

# Populate session state with dummy data similar to what the app has
st.session_state['triage_patient'] = {
    'nombre': 'Juan',
    'apellido1': 'Perez',
    'edad': 45,
    'sexo': 'Hombre',
    'patient_code': 'P12345'
}
st.session_state['datos_paciente'] = {
    'vital_signs': {'heart_rate': 80, 'systolic_bp': 120, 'diastolic_bp': 80},
    'texto_medico': 'Dolor de cabeza intenso',
    'alergias': ['Penicilina'],
    'patologias': ['Hipertension'],
    'medicacion': 'Enalapril',
    'hda': {'aparicion': 'Brusca', 'intensidad': 8}
}
st.session_state['resultado'] = {
    'nivel_texto': 'Nivel 3 - Urgente',
    'nivel_color': 'yellow',
    'tiempo_espera': '60 min',
    'razonamiento': ['Dolor intenso', 'Hipertension']
}
st.session_state['recommendations'] = ['Reposo', 'Control BP']
st.session_state['current_audit_id'] = 'TEST_AUDIT_ID'
st.session_state['username'] = 'Dr. Test'

# Import functions to test
from utils.triage_utils import get_current_triage_record
from services.report_service import generate_triage_pdf

try:
    print("Generating record...")
    record = get_current_triage_record()
    print("Record generated successfully.")
    # print(record)
    
    print("Generating PDF...")
    pdf_bytes = generate_triage_pdf(record)
    
    if pdf_bytes and len(pdf_bytes) > 0:
        print(f"PDF generated successfully. Size: {len(pdf_bytes)} bytes")
    else:
        print("Error: PDF bytes are empty.")
        sys.exit(1)

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
