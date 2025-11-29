# path: src/services/report_service.py
from fpdf import FPDF
from datetime import datetime
import os
import tempfile
from typing import Dict, Any, Optional

class TriageReportGenerator(FPDF):
    def __init__(self, triage_record: Dict[str, Any]):
        super().__init__()
        self.record = triage_record
        self.patient = triage_record.get('patient_data', {})
        self.vitals = triage_record.get('vital_signs', {})
        self.result = triage_record.get('triage_result', {})
        
        # Configuración básica
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        
    def header(self):
        # Logo (placeholder) y Título
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Informe de Triaje Clínico', ln=True, align='C')
        
        # Subtítulo con fecha
        self.set_font('Helvetica', 'I', 10)
        timestamp = self.record.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except:
                pass
        date_str = timestamp.strftime("%d/%m/%Y %H:%M") if isinstance(timestamp, datetime) else str(timestamp)
        
        self.cell(0, 5, f'Fecha: {date_str} | ID: {self.record.get("audit_id", "N/A")}', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, title, ln=True, fill=True)
        self.ln(2)

    def field(self, label, value):
        self.set_font('Helvetica', 'B', 10)
        self.cell(40, 6, f"{label}:", align='L')
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 6, str(value) if value else "N/A")
        self.ln(1)

    def generate(self):
        # 1. Datos del Paciente
        self.section_title("Datos del Paciente")
        name = f"{self.patient.get('nombre', '')} {self.patient.get('apellido1', '')} {self.patient.get('apellido2', '')}"
        self.field("Nombre", name.strip())
        self.field("ID / DNI", self.patient.get('id_number', 'N/A')) # Ajustar según modelo real
        self.field("Edad", f"{self.patient.get('age', 'N/A')} años")
        self.field("Género", self.patient.get('gender', 'N/A'))
        self.ln(5)

        # 2. Motivo de Consulta
        self.section_title("Motivo de Consulta")
        self.set_font('Helvetica', '', 10)
        motivo = self.record.get('motivo_consulta', 'No especificado')
        self.multi_cell(0, 6, motivo)
        self.ln(5)

        # 3. Signos Vitales
        self.section_title("Signos Vitales")
        # Tabla simple
        self.set_font('Helvetica', 'B', 9)
        cols = ["Métrica", "Valor", "Estado"]
        col_widths = [40, 40, 60]
        
        for w, h in zip(col_widths, cols):
            self.cell(w, 7, h, border=1, align='C', fill=True)
        self.ln()
        
        self.set_font('Helvetica', '', 9)
        
        # Mapeo de nombres
        metrics_map = {
            "fc": "Frecuencia Cardíaca", "spo2": "Saturación O2", "temp": "Temperatura",
            "pas": "Presión Sistólica", "pad": "Presión Diastólica", "fr": "Frec. Respiratoria",
            "gcs": "Glasgow", "eva": "Dolor (EVA)", "pupilas": "Pupilas"
        }
        
        # Detalles del cálculo (si existen) para obtener colores/labels
        details = self.result.get('details', [])
        details_dict = {d['metric']: d for d in details}
        
        for key, val in self.vitals.items():
            if key in ['oxigeno_suplementario', 'notas']: continue
            
            label = metrics_map.get(key, key.upper())
            det = details_dict.get(key, {})
            status = det.get('label', '-')
            
            self.cell(col_widths[0], 7, label, border=1)
            self.cell(col_widths[1], 7, str(val), border=1, align='C')
            self.cell(col_widths[2], 7, status, border=1)
            self.ln()
            
        self.ln(5)

        # 4. Antecedentes (Resumen)
        self.section_title("Antecedentes Relevantes")
        bg = self.record.get('patient_background', {})
        
        if not bg:
            self.multi_cell(0, 6, "No registrados.")
        else:
            if bg.get('allergies'):
                self.field("Alergias", ", ".join([a.get('agent', '') for a in bg.get('allergies', [])]))
            if bg.get('pathologies'):
                self.field("Patologías", ", ".join([p.get('name', '') for p in bg.get('pathologies', [])]))
            if bg.get('medications'):
                self.field("Medicación", bg.get('medications'))
        self.ln(5)

        # 5. Resultado del Triaje
        self.section_title("Clasificación de Triaje")
        
        level = self.result.get('final_priority', 0)
        color_name = self.result.get('final_color', 'gray')
        wait_time = self.result.get('wait_time', '-')
        
        # Color visual (cuadro relleno)
        r, g, b = 200, 200, 200
        if color_name == 'red': r, g, b = 220, 53, 69
        elif color_name == 'orange': r, g, b = 253, 126, 20
        elif color_name == 'yellow': r, g, b = 255, 193, 7
        elif color_name == 'green': r, g, b = 40, 167, 69
        elif color_name == 'black': r, g, b = 52, 58, 64
        
        self.set_fill_color(r, g, b)
        self.set_text_color(255 if color_name in ['red', 'green', 'black'] else 0)
        self.set_font('Helvetica', 'B', 14)
        
        level_text = f"NIVEL {level} - {color_name.upper()}"
        if level == 0: level_text = "NO CLASIFICADO"
        
        self.cell(0, 15, level_text, ln=True, align='C', fill=True, border=1)
        
        self.set_text_color(0)
        self.ln(2)
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, f"Tiempo Máximo de Espera: {wait_time}", ln=True, align='C')
        
        dest = self.record.get('destination', 'Sala de Espera')
        self.cell(0, 8, f"Destino: {dest}", ln=True, align='C')
        
        self.ln(10)
        
        # Firma
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font('Helvetica', 'I', 8)
        evaluator = self.record.get('evaluator_id', 'Sistema')
        self.cell(0, 5, f"Evaluado por: {evaluator}", ln=True, align='R')
        self.cell(0, 5, "Este documento es un registro clínico. Confidencial.", ln=True, align='C')

    def get_pdf_bytes(self):
        return self.output(dest='S').encode('latin-1')

def generate_triage_pdf(triage_record: Dict[str, Any]) -> bytes:
    """Genera el PDF del triaje y retorna los bytes."""
    pdf = TriageReportGenerator(triage_record)
    pdf.generate()
    return pdf.get_pdf_bytes()
