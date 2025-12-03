import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from db.repositories.triage import get_triage_repository
from db.repositories.people import get_people_repository

def generate_triage_report(triage_id: str) -> bytes:
    """
    Genera un informe clínico completo en formato PDF para un episodio de triaje.
    
    Args:
        triage_id (str): ID del registro de triaje.
        
    Returns:
        bytes: Contenido del archivo PDF.
    """
    # 1. Obtener datos
    data = _fetch_triage_data(triage_id)
    if not data:
        raise ValueError(f"No se encontró el registro de triaje con ID: {triage_id}")
        
    # 2. Generar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=1))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], spaceAfter=6, textColor=colors.HexColor("#007bff")))
    
    story = []
    
    # --- CABECERA ---
    story.append(Paragraph(f"Informe Clínico de Triaje", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Datos Administrativos
    admin_data = [
        ["Paciente:", data.get('patient_name', 'Desconocido')],
        ["ID Paciente:", data.get('patient_code', 'N/A')],
        ["Fecha/Hora:", data.get('timestamp', datetime.now().isoformat())],
        ["Centro:", "Hospital General (Simulado)"] # TODO: Obtener del config
    ]
    t_admin = Table(admin_data, colWidths=[1.5*inch, 4*inch])
    t_admin.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_admin)
    story.append(Spacer(1, 24))
    
    # --- MOTIVO DE CONSULTA ---
    story.append(Paragraph("1. Motivo de Consulta", styles['SectionHeader']))
    story.append(Paragraph(data.get('motivo_consulta', 'No especificado'), styles['Normal']))
    story.append(Spacer(1, 12))
    
    # --- SIGNOS VITALES ---
    if data.get('vital_signs'):
        story.append(Paragraph("2. Signos Vitales", styles['SectionHeader']))
        vs = data.get('vital_signs', {})
        vs_data = [
            ["FC", f"{vs.get('heart_rate', '-')} bpm", "SatO2", f"{vs.get('oxygen_saturation', '-')} %"],
            ["TA", f"{vs.get('systolic_bp', '-')}/{vs.get('diastolic_bp', '-')} mmHg", "Temp", f"{vs.get('temperature', '-')} °C"],
            ["FR", f"{vs.get('respiratory_rate', '-')} rpm", "Dolor", f"{data.get('pain_level', '-')} / 10"]
        ]
        t_vs = Table(vs_data, colWidths=[1*inch, 1.5*inch, 1*inch, 1.5*inch])
        t_vs.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_vs)
        story.append(Spacer(1, 12))
        
    # --- ANTECEDENTES ---
    story.append(Paragraph("3. Antecedentes Clínicos", styles['SectionHeader']))
    ant_text = data.get('antecedentes', 'Sin antecedentes relevantes registrados.')
    story.append(Paragraph(ant_text.replace('\n', '<br/>'), styles['Normal']))
    
    if data.get('alergias'):
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Alergias:</b> {data.get('alergias')}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # --- ANÁLISIS IA ---
    story.append(Paragraph("4. Análisis Asistido (IA)", styles['SectionHeader']))
    
    # Nivel
    level_text = data.get('triage_level_text', 'No clasificado')
    level_color = data.get('triage_level_color', 'grey')
    
    # Convertir nombre de color a Hex si es necesario para ReportLab
    color_map = {
        "red": "#dc3545", "orange": "#fd7e14", "yellow": "#ffc107", 
        "green": "#28a745", "blue": "#007bff", "black": "#343a40", "gray": "#6c757d"
    }
    hex_color = color_map.get(level_color, level_color) if level_color in color_map else "#6c757d"
    
    story.append(Paragraph(f"<b>Nivel Sugerido:</b> <font color='{hex_color}'>{level_text}</font>", styles['Normal']))
    
    # Razones
    if data.get('ai_reasons'):
        story.append(Paragraph("<b>Justificación Clínica:</b>", styles['Normal']))
        for reason in data.get('ai_reasons', []):
            r_text = reason.get('text', str(reason)) if isinstance(reason, dict) else str(reason)
            story.append(Paragraph(f"• {r_text}", styles['Normal'], bulletText="•"))
            
    story.append(Spacer(1, 12))
    
    # --- VALIDACIÓN HUMANA ---
    story.append(Paragraph("5. Validación y Cierre", styles['SectionHeader']))
    val_data = [
        ["Decisión:", data.get('human_decision', 'Pendiente')],
        ["Nivel Final:", data.get('final_level', level_text)],
        ["Validado por:", data.get('validator_user', 'Sistema')],
        ["Destino:", data.get('disposition', 'No asignado')]
    ]
    t_val = Table(val_data)
    t_val.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
    ]))
    story.append(t_val)
    
    # Build
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def _fetch_triage_data(triage_id: str) -> dict:
    """
    Recupera y consolida los datos de un registro de triaje.
    """
    repo = get_triage_repository()
    record = repo.get_by_audit_id(triage_id)
    
    if not record:
        return None
        
    # Mapeo de datos del registro a estructura plana para el reporte
    snapshot = record.get('patient_snapshot', {})
    
    data = {
        "patient_name": f"{snapshot.get('nombre', '')} {snapshot.get('apellido1', '')}",
        "patient_code": record.get('patient_id'),
        "timestamp": record.get('created_at', datetime.now()).strftime("%Y-%m-%d %H:%M:%S") if isinstance(record.get('created_at'), datetime) else str(record.get('created_at')),
        "motivo_consulta": snapshot.get('texto_medico', ''),
        "vital_signs": snapshot.get('vital_signs', {}),
        "pain_level": snapshot.get('dolor', 0),
        "antecedentes": snapshot.get('antecedentes', ''),
        "alergias": snapshot.get('alergias_info_completa', ''),
        
        # IA Data
        "triage_level_text": record.get('ia_result', {}).get('nivel', {}).get('text', 'N/A'),
        "triage_level_color": record.get('ia_result', {}).get('nivel', {}).get('color', 'black'),
        "ai_reasons": record.get('ia_result', {}).get('razones', []),
        
        # Human Data
        "human_decision": record.get('status', 'Borrador'), 
        "final_level": record.get('final_priority', 'N/A'),
        "validator_user": record.get('validator_id', 'N/A'),
        "disposition": record.get('disposition', 'N/A')
    }
    
    return data

def generate_triage_pdf(triage_record: dict) -> bytes:
    """
    Genera el PDF del triaje a partir de un diccionario de registro (para borradores o compatibilidad).
    
    Args:
        triage_record (dict): Diccionario con datos del triaje.
        
    Returns:
        bytes: Contenido del archivo PDF.
    """
    # Crear una instancia temporal del generador usando el diccionario directamente
    # Nota: TriageReportGenerator no existe como clase exportada en esta versión refactorizada,
    # así que adaptamos la lógica para usar generate_triage_report si tuviéramos ID,
    # o reconstruimos la lógica para dicts.
    
    # Para mantenerlo simple y robusto, usamos la misma lógica de generación de reportlab
    # pero mapeando el dict de entrada a la estructura esperada por el generador.
    
    # Mapeo rápido de triage_record (que puede venir de session_state) a 'data' plano
    snapshot = triage_record.get('patient_snapshot', triage_record) # Si no hay snapshot, usar el record mismo
    patient_data = triage_record.get('patient_data', {})
    
    data = {
        "patient_name": f"{patient_data.get('nombre', '')} {patient_data.get('apellido1', '')}",
        "patient_code": triage_record.get('patient_id'),
        "timestamp": datetime.now().isoformat(), # Borrador
        "motivo_consulta": patient_data.get('texto_medico', ''),
        "vital_signs": patient_data.get('vital_signs', {}),
        "pain_level": patient_data.get('dolor', 0),
        "antecedentes": patient_data.get('antecedentes', ''),
        "alergias": patient_data.get('alergias_info_completa', ''),
        
        # IA Data
        "triage_level_text": triage_record.get('ia_result', {}).get('nivel', {}).get('text', 'N/A'),
        "triage_level_color": triage_record.get('ia_result', {}).get('nivel', {}).get('color', 'black'),
        "ai_reasons": triage_record.get('ia_result', {}).get('razones', []),
        
        # Human Data
        "human_decision": "BORRADOR", 
        "final_level": triage_record.get('final_priority', 'N/A'),
        "validator_user": "Usuario Actual",
        "disposition": "En Proceso"
    }
    
    # Reutilizar lógica de generación (copiada por ahora para evitar refactor mayor, 
    # idealmente extraer _build_pdf a función separada)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=1))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], spaceAfter=6, textColor=colors.HexColor("#007bff")))
    
    story = []
    story.append(Paragraph(f"Borrador de Informe Clínico", styles['Title']))
    story.append(Spacer(1, 12))
    
    # ... (Versión simplificada para borrador)
    story.append(Paragraph(f"Paciente: {data['patient_name']}", styles['Normal']))
    story.append(Paragraph(f"Motivo: {data['motivo_consulta']}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    if data['vital_signs']:
        story.append(Paragraph("Signos Vitales (Borrador)", styles['SectionHeader']))
        vs = data['vital_signs']
        story.append(Paragraph(f"FC: {vs.get('heart_rate','-')} | SatO2: {vs.get('oxygen_saturation','-')} | TA: {vs.get('systolic_bp','-')}/{vs.get('diastolic_bp','-')}", styles['Normal']))
    
    story.append(Spacer(1, 12))
    story.append(Paragraph("Nivel Sugerido IA: " + str(data['triage_level_text']), styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
