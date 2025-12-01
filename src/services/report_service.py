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

    def _sanitize(self, text):
        """Sanitiza el texto para ser compatible con latin-1 (FPDF standard)."""
        if not isinstance(text, str):
            text = str(text)
        # Reemplazar caracteres problemáticos comunes
        replacements = {
            "€": "EUR",
            "–": "-",
            "—": "-",
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'"
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
            
        # Intentar codificar a latin-1, reemplazando errores con ?
        return text.encode('latin-1', 'replace').decode('latin-1')

    def field(self, label, value):
        self.set_font('Helvetica', 'B', 10)
        self.cell(40, 6, self._sanitize(f"{label}:"), align='L')
        self.set_font('Helvetica', '', 10)
        val_str = str(value) if value else "No disponible"
        self.multi_cell(0, 6, self._sanitize(val_str))
        self.ln(1)

    def generate(self):
        # 1. Datos del Paciente
        self.section_title("Datos del Paciente")
        name = f"{self.patient.get('nombre', '')} {self.patient.get('apellido1', '')} {self.patient.get('apellido2', '')}"
        self.field("Nombre", name.strip())
        self.field("ID / DNI", self.patient.get('id_number', 'No disponible')) # Ajustar según modelo real
        self.field("Edad", f"{self.patient.get('age', 'No disponible')} años")
        self.field("Género", self.patient.get('gender', 'No disponible'))
        self.ln(5)

        # 2. Motivo de Consulta y HDA
        self.section_title("Motivo de Consulta y Enfermedad Actual")
        self.set_font('Helvetica', '', 10)
        motivo = self.record.get('motivo_consulta', 'No disponible')
        self.multi_cell(0, 6, self._sanitize(f"Motivo: {motivo}"))
        
        # HDA (ALICIA)
        hda = []
        if self.patient.get('hda_aparicion'): hda.append(f"Aparición: {self.patient.get('hda_aparicion')}")
        if self.patient.get('hda_localizacion'): hda.append(f"Localización: {self.patient.get('hda_localizacion')}")
        if self.patient.get('hda_intensidad'): hda.append(f"Intensidad: {self.patient.get('hda_intensidad')}")
        if self.patient.get('hda_caracter'): hda.append(f"Carácter: {self.patient.get('hda_caracter')}")
        if self.patient.get('hda_irradiacion'): hda.append(f"Irradiación: {self.patient.get('hda_irradiacion')}")
        if self.patient.get('hda_atenuantes'): hda.append(f"Atenuantes/Agravantes: {self.patient.get('hda_atenuantes')}")
        
        if hda:
            self.ln(2)
            self.set_font('Helvetica', 'B', 10)
            self.cell(0, 6, "Historia de la Enfermedad Actual (ALICIA):", ln=True)
            self.set_font('Helvetica', '', 10)
            for line in hda:
                self.multi_cell(0, 6, self._sanitize(f"- {line}"))
                
        # Datos Administrativos
        admin_data = []
        if self.patient.get('fuente_informacion'): admin_data.append(f"Fuente: {self.patient.get('fuente_informacion')}")
        if self.patient.get('referencia'): admin_data.append(f"Referencia: {self.patient.get('referencia')}")
        if self.patient.get('seguro'): admin_data.append(f"Seguro: {self.patient.get('seguro')}")
        
        if admin_data:
            self.ln(2)
            self.set_font('Helvetica', 'I', 9)
            self.multi_cell(0, 6, self._sanitize(" | ".join(admin_data)))

        self.ln(5)

        # 3. Signos Vitales
        self.section_title("Signos Vitales y Escalas")
        
        if not self.vitals:
            self.set_font('Helvetica', 'I', 10)
            self.cell(0, 6, "No disponible", ln=True)
        else:
            # Tabla simple
            self.set_font('Helvetica', 'B', 9)
            cols = ["Métrica", "Valor", "Estado"]
            col_widths = [40, 40, 60]
            
            for w, h in zip(col_widths, cols):
                self.cell(w, 7, self._sanitize(h), border=1, align='C', fill=True)
            self.ln()
            
            self.set_font('Helvetica', '', 9)
            
            # Mapeo de nombres
            metrics_map = {
                "fc": "Frecuencia Cardíaca", "spo2": "Saturación O2", "temp": "Temperatura",
                "pas": "Presión Sistólica", "pad": "Presión Diastólica", "fr": "Frec. Respiratoria",
                "gcs": "Glasgow", "eva": "Dolor (EVA)", "pupilas": "Pupilas",
                "oxigeno_suplementario": "Oxígeno Supl.", "hidratacion": "Hidratación"
            }
            
            # Detalles del cálculo (si existen) para obtener colores/labels
            details = self.result.get('details', [])
            details_dict = {d['metric']: d for d in details}
            
            for key, val in self.vitals.items():
                if key in ['notas']: continue
                
                label = metrics_map.get(key, key.upper())
                det = details_dict.get(key, {})
                status = det.get('label', '-')
                
                # Formateo especial booleanos
                if isinstance(val, bool):
                    val = "Sí" if val else "No"
                
                self.cell(col_widths[0], 7, self._sanitize(label), border=1)
                self.cell(col_widths[1], 7, self._sanitize(str(val)), border=1, align='C')
                self.cell(col_widths[2], 7, self._sanitize(status), border=1)
                self.ln()
            
        self.ln(5)

        # 4. Historia Clínica Integral
        self.section_title("Historia Clínica Integral")
        
        # Antecedentes (Legacy + Extended)
        bg = self.record.get('patient_background', {})
        
        # Combinar legacy con extended si existen
        allergies = bg.get('allergies', [])
        pathologies = bg.get('pathologies', [])
        medications = bg.get('medications', '')
        
        if allergies: self.field("Alergias", ", ".join([a.get('agent', '') for a in allergies]))
        if pathologies: self.field("Antecedentes Personales", ", ".join([p.get('name', '') for p in pathologies]))
        if medications: self.field("Medicación Habitual", medications)
        
        # Campos extendidos (extended_history.py)
        ext_fields = {
            "ant_familiares": "Antecedentes Familiares",
            "ant_psiquiatricos": "Psiquiatría/Salud Mental",
            "ant_quirurgicos": "Antecedentes Quirúrgicos",
            "habitos_toxicos": "Hábitos Tóxicos",
            "nutricion_dieta": "Nutrición y Dieta",
            "viajes_recientes": "Viajes/Exposición",
            "sensorial_ayudas": "Déficits Sensoriales",
            "dolor_cronico": "Historia de Dolor",
            "hospitalizaciones_previas": "Hospitalizaciones Previas",
            "situacion_legal": "Situación Legal/Social"
        }
        
        for key, label in ext_fields.items():
            val = self.patient.get(key)
            if val:
                self.field(label, val)
                
        self.ln(5)

        # 5. Valoración de Enfermería
        self.section_title("Valoración de Enfermería")
        
        nursing_data = []
        if self.patient.get('skin_integrity'): nursing_data.append(f"Piel: {self.patient.get('skin_integrity')} ({self.patient.get('skin_color', '')})")
        if self.patient.get('fall_risk'): nursing_data.append(f"Riesgo Caídas: {self.patient.get('fall_risk')}")
        if self.patient.get('nut_disfagia'): nursing_data.append("Riesgo Aspiración: Sí")
        if self.patient.get('id_bracelet'): nursing_data.append("Pulsera ID: Colocada")
        
        if nursing_data:
            for item in nursing_data:
                self.multi_cell(0, 6, self._sanitize(f"- {item}"))
        else:
            self.multi_cell(0, 6, "No registrada")
            
        if self.patient.get('belongings'):
            self.ln(2)
            self.field("Pertenencias", self.patient.get('belongings'))

        self.ln(5)

        # 6. Resultado del Triaje
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
        if level == 0: level_text = "PENDIENTE / NO DISPONIBLE"
        
        self.cell(0, 15, self._sanitize(level_text), ln=True, align='C', fill=True, border=1)
        
        self.set_text_color(0)
        self.ln(2)
        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, self._sanitize(f"Tiempo Máximo de Espera: {wait_time}"), ln=True, align='C')
        
        dest = self.record.get('destination', 'Sala de Espera')
        self.cell(0, 8, self._sanitize(f"Destino: {dest}"), ln=True, align='C')
        
        # Órdenes Iniciales
        orders = []
        if self.patient.get('order_diet'): orders.append(f"Dieta: {self.patient.get('order_diet')}")
        if self.patient.get('order_iv'): orders.append("Acceso IV: Sí")
        if self.patient.get('order_labs'): orders.append(f"Labs: {', '.join(self.patient.get('order_labs'))}")
        if self.patient.get('order_meds_stat'): orders.append(f"Meds STAT: {self.patient.get('order_meds_stat')}")
        
        if orders:
            self.ln(5)
            self.set_font('Helvetica', 'B', 10)
            self.cell(0, 6, "Órdenes Iniciales:", ln=True)
            self.set_font('Helvetica', '', 10)
            for o in orders:
                self.multi_cell(0, 6, self._sanitize(f"- {o}"))

        self.ln(10)
        
        # Firma
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font('Helvetica', 'I', 8)
        evaluator = self.record.get('evaluator_id', 'Sistema')
        self.cell(0, 5, self._sanitize(f"Evaluado por: {evaluator}"), ln=True, align='R')
        self.cell(0, 5, "Este documento es un registro clínico. Confidencial.", ln=True, align='C')

    def get_pdf_bytes(self):
        return self.output(dest='S').encode('latin-1')

def generate_triage_pdf(triage_record: Dict[str, Any]) -> bytes:
    """Genera el PDF del triaje y retorna los bytes."""
    pdf = TriageReportGenerator(triage_record)
    pdf.generate()
    return pdf.get_pdf_bytes()
