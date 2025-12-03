import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

from db.repositories.triage import get_triage_repository

# --- CONSTANTS & STYLES ---
HEADER_COLOR = colors.HexColor("#0056b3") # Blue
SUBHEADER_COLOR = colors.HexColor("#333333") # Dark Gray
BORDER_COLOR = colors.HexColor("#dddddd")

def _get_styles():
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(name='ReportTitle', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18, spaceAfter=20, textColor=HEADER_COLOR))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], fontSize=14, spaceBefore=12, spaceAfter=6, textColor=HEADER_COLOR, borderWidth=1, borderColor=BORDER_COLOR, borderPadding=4, borderRadius=2))
    styles.add(ParagraphStyle(name='SubSectionHeader', parent=styles['Heading3'], fontSize=12, spaceBefore=6, spaceAfter=4, textColor=SUBHEADER_COLOR))
    styles.add(ParagraphStyle(name='NormalJustified', parent=styles['Normal'], alignment=TA_JUSTIFY, spaceAfter=6))
    styles.add(ParagraphStyle(name='WarningText', parent=styles['Normal'], textColor=colors.red, fontSize=10, spaceAfter=6))
    styles.add(ParagraphStyle(name='SmallText', parent=styles['Normal'], fontSize=8, textColor=colors.gray))
    
    return styles

def generate_report(data: dict) -> bytes:
    """
    Genera un informe clínico completo en PDF (Unificado para Borrador y Final).
    
    Args:
        data (dict): Diccionario plano con todos los datos clínicos y administrativos.
        
    Returns:
        bytes: Contenido del PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = _get_styles()
    story = []
    
    # --- 1. CABECERA ---
    title_text = "INFORME DE TRIAJE CLÍNICO"
    if data.get('is_draft'):
        title_text += " (BORRADOR)"
        
    story.append(Paragraph(title_text, styles['ReportTitle']))
    
    # Datos Administrativos (Tabla)
    admin_data = [
        [Paragraph(f"<b>Paciente:</b> {data.get('patient_name', 'Desconocido')}", styles['Normal']),
         Paragraph(f"<b>ID:</b> {data.get('patient_code', 'N/A')}", styles['Normal'])],
        [Paragraph(f"<b>Edad/Sexo:</b> {data.get('age_gender', 'N/A')}", styles['Normal']),
         Paragraph(f"<b>Fecha:</b> {data.get('timestamp', '-')}", styles['Normal'])],
        [Paragraph(f"<b>Centro:</b> {data.get('center', 'Hospital General')}", styles['Normal']),
         Paragraph(f"<b>Episodio:</b> {data.get('episode_id', 'N/A')}", styles['Normal'])]
    ]
    
    t_admin = Table(admin_data, colWidths=[3.5*inch, 3*inch])
    t_admin.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), colors.aliceblue),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_admin)
    story.append(Spacer(1, 15))
    
    # --- 2. CLASIFICACIÓN DE TRIAJE ---
    story.append(Paragraph("1. Clasificación y Prioridad", styles['SectionHeader']))
    
    level_text = data.get('triage_level_text', 'No clasificado')
    level_color = data.get('triage_level_color', 'gray')
    
    # Mapeo de colores
    color_map = {
        "red": colors.HexColor("#dc3545"), "orange": colors.HexColor("#fd7e14"), 
        "yellow": colors.HexColor("#ffc107"), "green": colors.HexColor("#28a745"), 
        "blue": colors.HexColor("#007bff"), "black": colors.HexColor("#343a40"), 
        "gray": colors.HexColor("#6c757d")
    }
    bg_color = color_map.get(level_color, colors.gray)
    text_color = colors.black if level_color in ['yellow', 'white'] else colors.white
    
    # Tabla de Nivel
    level_data = [[
        Paragraph(f"<font color='white'><b>{level_text}</b></font>", 
                  ParagraphStyle('LevelStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, textColor=text_color))
    ]]
    t_level = Table(level_data, colWidths=[7*inch])
    t_level.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 10),
        ('rx', (0,0), (-1,-1), 5), # Rounded corners (not supported in standard Table, but kept for future)
    ]))
    story.append(t_level)
    
    if data.get('wait_time'):
        story.append(Spacer(1, 5))
        story.append(Paragraph(f"<b>Tiempo Máximo de Espera Sugerido:</b> {data.get('wait_time')}", styles['Normal']))
    
    story.append(Spacer(1, 15))
    
    # --- 3. ANAMNESIS Y MOTIVO ---
    story.append(Paragraph("2. Anamnesis", styles['SectionHeader']))
    
    # Motivo Principal
    story.append(Paragraph("<b>Motivo de Consulta:</b>", styles['SubSectionHeader']))
    story.append(Paragraph(data.get('motivo_consulta', 'No especificado').replace('\n', '<br/>'), styles['NormalJustified']))
    
    # Entrevista Guiada (Resumen)
    if data.get('guided_interview'):
        story.append(Spacer(1, 5))
        story.append(Paragraph("<b>Resumen Entrevista Guiada:</b>", styles['SubSectionHeader']))
        story.append(Paragraph(data.get('guided_interview').replace('\n', '<br/>'), styles['NormalJustified']))
        
    # HDA (Alicia)
    hda = data.get('hda', {})
    if any(hda.values()):
        story.append(Spacer(1, 5))
        story.append(Paragraph("<b>Historia de la Enfermedad Actual (HDA):</b>", styles['SubSectionHeader']))
        
        hda_rows = []
        if hda.get('aparicion'): hda_rows.append(f"<b>Aparición:</b> {hda['aparicion']}")
        if hda.get('localizacion'): hda_rows.append(f"<b>Localización:</b> {hda['localizacion']}")
        if hda.get('intensidad'): hda_rows.append(f"<b>Intensidad:</b> {hda['intensidad']}/10")
        if hda.get('caracteristicas'): hda_rows.append(f"<b>Características:</b> {', '.join(hda['caracteristicas']) if isinstance(hda['caracteristicas'], list) else hda['caracteristicas']}")
        if hda.get('irradiacion'): hda_rows.append(f"<b>Irradiación:</b> {hda['irradiacion']}")
        if hda.get('alivio'): hda_rows.append(f"<b>Alivio/Agravantes:</b> {hda['alivio']}")
        if hda.get('sintomas_asoc'): hda_rows.append(f"<b>Síntomas Asoc.:</b> {hda['sintomas_asoc']}")
        
        # Renderizar como lista compacta
        for row in hda_rows:
            story.append(Paragraph(f"• {row}", styles['Normal']))
            
    story.append(Spacer(1, 15))

    # --- 4. SIGNOS VITALES Y CONTEXTO ---
    story.append(Paragraph("3. Exploración y Contexto", styles['SectionHeader']))
    
    # Signos Vitales
    vs = data.get('vital_signs', {})
    if vs:
        vs_data = [
            [Paragraph("<b>Frecuencia Cardíaca</b>", styles['Normal']), f"{vs.get('heart_rate', '-')} bpm",
             Paragraph("<b>Sat. Oxígeno</b>", styles['Normal']), f"{vs.get('oxygen_saturation', '-')} %"],
            [Paragraph("<b>Presión Arterial</b>", styles['Normal']), f"{vs.get('systolic_bp', '-')}/{vs.get('diastolic_bp', '-')} mmHg",
             Paragraph("<b>Temperatura</b>", styles['Normal']), f"{vs.get('temperature', '-')} °C"],
            [Paragraph("<b>Frecuencia Resp.</b>", styles['Normal']), f"{vs.get('respiratory_rate', '-')} rpm",
             Paragraph("<b>Nivel de Dolor</b>", styles['Normal']), f"{data.get('pain_level', '-')} / 10"],
            [Paragraph("<b>Nivel Conciencia</b>", styles['Normal']), f"{vs.get('consciousness', 'Alert')}",
             Paragraph("<b>Glucemia</b>", styles['Normal']), f"{vs.get('blood_glucose', '-') if vs.get('blood_glucose') else '-'}"]
        ]
        
        t_vs = Table(vs_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
        t_vs.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke), # Labels col 1
            ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke), # Labels col 3
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_vs)
    else:
        story.append(Paragraph("No se registraron signos vitales.", styles['Normal']))
        
    # Contexto Clínico (Alertas)
    ctx = data.get('clinical_context', {})
    alerts = []
    if ctx.get('geriatric'): alerts.append("PACIENTE GERIÁTRICO (Edad ≥ 65)")
    if ctx.get('immuno'): 
        det = f" ({', '.join(ctx.get('immuno_det', []))})" if ctx.get('immuno_det') else ""
        alerts.append(f"PACIENTE INMUNODEPRIMIDO/ONCOLÓGICO{det}")
        
    if alerts:
        story.append(Spacer(1, 8))
        for alert in alerts:
            story.append(Paragraph(f"⚠️ <b>ALERTA CLÍNICA:</b> {alert}", styles['WarningText']))
            
    story.append(Spacer(1, 15))
    
    # --- 5. HISTORIA CLÍNICA ---
    story.append(Paragraph("4. Historia Clínica Integral", styles['SectionHeader']))
    
    # Alergias
    alergias = data.get('alergias', 'No conocidas')
    story.append(Paragraph(f"<b>Alergias:</b> {alergias}", styles['Normal']))
    
    # Antecedentes (Legacy + Extended)
    ant_legacy = data.get('antecedentes', '')
    ant_extended = data.get('extended_history', '')
    
    if ant_extended:
        story.append(Spacer(1, 5))
        story.append(Paragraph("<b>Antecedentes Detallados:</b>", styles['SubSectionHeader']))
        story.append(Paragraph(ant_extended.replace('\n', '<br/>'), styles['Normal']))
    elif ant_legacy:
        story.append(Spacer(1, 5))
        story.append(Paragraph(f"<b>Antecedentes:</b> {ant_legacy}", styles['Normal']))
    else:
        story.append(Paragraph("Sin antecedentes registrados.", styles['Normal']))
        
    story.append(Spacer(1, 15))
    
    # --- 6. ANÁLISIS IA (RAZONAMIENTO) ---
    story.append(Paragraph("5. Análisis del Asistente (IA)", styles['SectionHeader']))
    
    reasons = data.get('ai_reasons', [])
    if reasons:
        for r in reasons:
            r_text = r.get('text', str(r)) if isinstance(r, dict) else str(r)
            story.append(Paragraph(f"• {r_text}", styles['NormalJustified'], bulletText="•"))
    else:
        story.append(Paragraph("No hay análisis disponible.", styles['Normal']))
        
    story.append(Spacer(1, 20))
    
    # --- 7. PIE DE PÁGINA / VALIDACIÓN ---
    story.append(Paragraph("Validación y Cierre", styles['SectionHeader']))
    
    val_data = [
        [Paragraph(f"<b>Estado:</b> {data.get('status', 'Borrador')}", styles['Normal']),
         Paragraph(f"<b>Destino:</b> {data.get('disposition', '-')}", styles['Normal'])],
        [Paragraph(f"<b>Validado por:</b> {data.get('validator', 'Sistema')}", styles['Normal']),
         Paragraph(f"<b>Firma Digital:</b> {data.get('signature_hash', '-')}", styles['SmallText'])]
    ]
    t_val = Table(val_data, colWidths=[3.5*inch, 3.5*inch])
    story.append(t_val)
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("Documento generado automáticamente por TRYaG AI System. Uso exclusivo clínico.", styles['SmallText']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _extract_clinical_data(record: dict, is_draft: bool = False) -> dict:
    """
    Extrae y normaliza los datos clínicos de un registro (final o borrador).
    """
    # Determinar fuente de datos (snapshot o root)
    source = record.get('patient_snapshot', record) if not is_draft else record
    
    # Datos básicos
    patient_name = f"{source.get('nombre', '')} {source.get('apellido1', '')}"
    if not source.get('nombre'): patient_name = "Paciente Desconocido"
    
    age = source.get('edad', '?')
    gender = source.get('gender', '')
    age_gender = f"{age} años" + (f" ({gender})" if gender else "")
    
    # HDA
    hda = {
        "aparicion": source.get('hda_aparicion'),
        "localizacion": source.get('hda_localizacion'),
        "intensidad": source.get('hda_intensidad'),
        "caracteristicas": source.get('hda_caracteristicas'),
        "irradiacion": source.get('hda_irradiacion'),
        "alivio": source.get('hda_alivio'),
        "sintomas_asoc": source.get('hda_sintomas_asoc')
    }
    
    # Contexto
    ctx = {
        "geriatric": source.get('criterio_geriatrico', False),
        "immuno": source.get('criterio_inmunodeprimido', False),
        "immuno_det": source.get('criterio_inmunodeprimido_det', [])
    }
    
    # IA Results
    ia_res = record.get('ia_result', {})
    # Si es borrador, puede que ia_result esté en el root o no exista
    if not ia_res and is_draft:
        ia_res = {} # En borrador a veces no hay resultado IA aún
        
    return {
        "is_draft": is_draft,
        "episode_id": str(record.get('_id', 'N/A')),
        "patient_code": record.get('patient_id', 'N/A'),
        "patient_name": patient_name,
        "age_gender": age_gender,
        "timestamp": record.get('created_at', datetime.now()).strftime("%Y-%m-%d %H:%M") if isinstance(record.get('created_at'), datetime) else str(record.get('created_at', '-')),
        
        "motivo_consulta": source.get('texto_medico', source.get('motivo_consulta', '')),
        "guided_interview": source.get('guided_interview_summary', ''),
        "hda": hda,
        
        "vital_signs": source.get('vital_signs', {}),
        "pain_level": source.get('dolor', 0),
        
        "clinical_context": ctx,
        
        "alergias": source.get('alergias_info_completa', source.get('alergias', '')),
        "antecedentes": source.get('antecedentes', ''),
        "extended_history": source.get('historia_integral', ''),
        
        "triage_level_text": ia_res.get('nivel', {}).get('text', 'PENDIENTE'),
        "triage_level_color": ia_res.get('nivel', {}).get('color', 'gray'),
        "wait_time": ia_res.get('wait_time', ''),
        "ai_reasons": ia_res.get('razones', []),
        
        "status": record.get('status', 'Borrador').upper(),
        "disposition": record.get('disposition', '-'),
        "validator": record.get('validator_id', 'Sistema'),
        "signature_hash": str(record.get('_id', ''))[-8:].upper() # Mock signature
    }

def generate_triage_report(triage_id: str) -> bytes:
    """Genera reporte final desde DB."""
    repo = get_triage_repository()
    record = repo.get_by_audit_id(triage_id)
    if not record:
        raise ValueError("Record not found")
    
    data = _extract_clinical_data(record, is_draft=False)
    return generate_report(data)

def generate_triage_pdf(triage_record: dict) -> bytes:
    """Genera reporte borrador desde diccionario (Frontend)."""
    # triage_record aquí suele ser una mezcla de datos del paciente y estado del borrador
    data = _extract_clinical_data(triage_record, is_draft=True)
    return generate_report(data)
