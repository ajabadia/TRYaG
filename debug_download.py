import streamlit as st
from fpdf import FPDF
from datetime import datetime
import re

def generate_dummy_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF Content", ln=1, align="C")
    return pdf.output(dest='S').encode('latin-1')

st.title("Debug PDF Download")

if st.button("Generate PDF"):
    pdf_bytes = generate_dummy_pdf()
    
    # Logic from the app
    raw_name = "Paciente_Prueba_Áéíóú"
    safe_name = re.sub(r'[^\w\-_]', '_', raw_name)
    file_name = f"Borrador_{safe_name}_{datetime.now().strftime('%H%M')}.pdf"
    
    st.write(f"Generated filename: {file_name}")
    
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name=file_name,
        mime="application/pdf",
        key="debug_dl_btn"
    )
