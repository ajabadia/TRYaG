import streamlit as st
import urllib.parse
from datetime import datetime
import json

def render_ticket_modal(patient_data):
    """
    Renderiza un ticket/pulsera de identificación para el paciente.
    Usa una API pública para generar el QR.
    """
    # Preparar datos para el QR
    qr_payload = {
        "id": patient_data.get("_id", "unknown"),
        "nhc": patient_data.get("identification_number", ""),
        "name": f"{patient_data.get('nombre', '')} {patient_data.get('apellidos', '')}",
        "arrival": datetime.now().isoformat()
    }
    qr_data = json.dumps(qr_payload)
    qr_quoted = urllib.parse.quote(qr_data)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_quoted}"

    # Estilos CSS para el ticket
    st.markdown("""
        <style>
        .ticket-container {
            border: 2px dashed #333;
            padding: 20px;
            background-color: #fff;
            color: #000;
            font-family: 'Courier New', Courier, monospace;
            max_width: 400px;
            margin: 0 auto;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
        }
        .ticket-header {
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        .ticket-body {
            font-size: 14px;
            line-height: 1.4;
        }
        .ticket-field {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }
        .ticket-highlight {
            font-weight: bold;
            font-size: 16px;
        }
        .ticket-allergies {
            color: white;
            background-color: black;
            padding: 5px;
            margin-top: 10px;
            text-align: center;
            font-weight: bold;
        }
        .ticket-footer {
            text-align: center;
            margin-top: 15px;
            font-size: 10px;
            border-top: 1px dotted #000;
            padding-top: 5px;
        }
        .cut-line {
            border-top: 1px dashed red;
            margin-top: 20px;
            position: relative;
        }
        .cut-line::after {
            content: "✂️ Cortar aquí";
            position: absolute;
            top: -10px;
            right: 0;
            background: white;
            color: red;
            font-size: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Renderizar Ticket
    st.markdown('<div class="ticket-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="ticket-header">
            <h3>HOSPITAL GENERAL</h3>
            <p>ADMISIÓN DE URGENCIAS</p>
        </div>
    """, unsafe_allow_html=True)

    # QR y Datos Principales
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(qr_url, width=100)
    with c2:
        st.markdown(f"**Nombre:**<br>{patient_data.get('nombre', 'Desc.')} {patient_data.get('apellidos', '')}", unsafe_allow_html=True)
        st.markdown(f"**NHC:** <code>{patient_data.get('identification_number', '---')}</code>", unsafe_allow_html=True)
        st.markdown(f"**Edad:** {patient_data.get('edad', '?')} años", unsafe_allow_html=True)

    # Alergias (Crítico)
    alergias = patient_data.get('medical_background', {}).get('allergies', [])
    if alergias:
        alergias_str = ", ".join(alergias) if isinstance(alergias, list) else str(alergias)
        st.markdown(f'<div class="ticket-allergies">⚠️ ALERGIAS: {alergias_str.upper()}</div>', unsafe_allow_html=True)
    else:
         st.markdown(f'<div style="text-align:center; margin-top:10px; border:1px solid #ccc;">Sin Alergias Conocidas</div>', unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
        <div class="ticket-footer">
            Entrada: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
            Conserve este ticket durante toda su estancia.
        </div>
        <div class="cut-line"></div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Botón de "Imprimir" (Simulado)
    if st.button("🖨️ Enviar a Impresora", use_container_width=True, key="print_ticket_job"):
        st.toast("Enviando trabajo de impresión... (Simulado)", icon="🖨️")

