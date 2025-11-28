"""
Módulo de utilidades para la generación de informes en PDF.
"""
from fpdf import FPDF
import pandas as pd

class PDF(FPDF):
    """Clase personalizada para generar PDFs con cabecera y pie de página."""
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Informe de Auditoría - Asistente de Triaje IA', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_audit_pdf(df):
    """
    Genera un PDF con los datos del DataFrame de auditoría.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos a exportar.
        
    Returns:
        bytes: Contenido del PDF en bytes.
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    if df.empty:
        pdf.cell(0, 10, "No hay datos para mostrar.", 0, 1)
        return pdf.output(dest='S').encode('latin-1')

    # Columnas a mostrar (ajustar según necesidad)
    cols_to_show = [col for col in df.columns if col in ['timestamp', 'decision_humana', 'audit_id', 'file_name', 'original_text', 'type', 'module']]
    if not cols_to_show:
        cols_to_show = df.columns[:5] # Fallback a las primeras 5

    # Cabecera de tabla
    pdf.set_font("Arial", 'B', 10)
    for col in cols_to_show:
        pdf.cell(40, 10, str(col)[:15], 1)
    pdf.ln()
    
    # Filas
    pdf.set_font("Arial", size=8)
    for _, row in df.iterrows():
        for col in cols_to_show:
            val = str(row[col])
            pdf.cell(40, 10, val[:20], 1) # Truncar para que quepa
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1', errors='replace')