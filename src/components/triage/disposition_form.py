# path: src/components/triage/disposition_form.py
# Creado: 2025-12-04
"""
Formulario para la gestión de órdenes médicas y planificación (Paso 4).
Permite solicitar pruebas complementarias, medicación y otras órdenes.
"""
import streamlit as st

def render_disposition_form():
    """
    Renderiza el formulario de órdenes médicas y planificación.
    """
    st.markdown("#### 📋 Órdenes Médicas y Planificación")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Pruebas Diagnósticas**")
            st.checkbox("Analítica Sanguínea (Hemograma, Bioquímica)", key="order_labs")
            st.checkbox("Gasometría Arterial/Venosa", key="order_gasometry")
            st.checkbox("Electrocardiograma (ECG)", key="order_ecg")
            st.checkbox("Radiografía de Tórax", key="order_xray_chest")
            
        with col2:
            st.markdown("**Otras Pruebas / Imagen**")
            st.text_area("Otras pruebas de imagen o específicas:", height=100, key="order_other_tests", placeholder="Ej: TAC Craneal, Ecografía Abdominal...")

    with st.container(border=True):
        st.markdown("**Medicación y Tratamiento Inmediato**")
        st.text_area("Órdenes de tratamiento:", height=100, key="order_medication", placeholder="Ej: Paracetamol 1g IV, Salbutamol nebulizado...")
    
    with st.container(border=True):
        st.markdown("**Observaciones / Plan**")
        st.text_area("Plan de actuación:", height=100, key="order_plan", placeholder="Observaciones para enfermería o médico responsable...")

    st.markdown('<div class="debug-footer">src/components/triage/disposition_form.py</div>', unsafe_allow_html=True)
