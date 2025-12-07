import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
import re
import unicodedata

from db.repositories.triage import get_triage_repository

def get_report_filename(patient_data: dict, prefix: str = "Informe") -> str:
    """
    Genera un nombre de archivo seguro y estandarizado para los reportes PDF.
    Formato: {Prefix}_{Nombre}_{Apellido}_{YYYYMMDD_HHMM}.pdf
    """
    try:
        # Obtener nombre y apellido de forma robusta
        nombre = patient_data.get('nombre', 'Paciente')
        apellido = patient_data.get('apellido1', '')
        
        # Si viene en un dict anidado (ej. patient_snapshot)
        if isinstance(nombre, dict): 
            nombre = "Paciente"
        
        raw_name = f"{nombre}_{apellido}".strip("_")
        if not raw_name:
            raw_name = "Paciente_Desconocido"
            
        # Normalizar caracteres (tildes, ñ, etc)
        normalized = unicodedata.normalize('NFKD', raw_name).encode('ASCII', 'ignore').decode('ASCII')
        
        # Sanitizar (solo letras, números, guiones y guiones bajos)
        safe_name = re.sub(r'[^\w\-_]', '_', normalized)
        
        # Timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        return f"{prefix}_{safe_name}_{timestamp}.pdf"
    except Exception as e:
        print(f"Error generating filename: {e}")
        return f"{prefix}_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"


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

    # --- 7. RECOMENDACIONES Y CUIDADOS (NUEVO) ---
    recs = data.get('recommendations', [])
    if recs:
        story.append(Paragraph("6. Recomendaciones y Cuidados", styles['SectionHeader']))
        for rec in recs:
            story.append(Paragraph(f"• {rec}", styles['NormalJustified'], bulletText="•"))
        story.append(Spacer(1, 20))
    
    # --- 8. PIE DE PÁGINA / VALIDACIÓN ---
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
    try:
        # Determinar fuente de datos (snapshot o root)
        source = record.get('patient_snapshot', record) if not is_draft else record
        if not source: source = {}
        
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
            
            "motivo_consulta": str(source.get('texto_medico', source.get('motivo_consulta', 'No especificado'))),
            "guided_interview": str(source.get('guided_interview_summary', '')),
            "hda": hda,
            
            "vital_signs": source.get('vital_signs', {}),
            "pain_level": source.get('dolor', 0),
            
            "clinical_context": ctx,
            
            "alergias": str(source.get('alergias_info_completa', source.get('alergias', ''))),
            "antecedentes": str(source.get('antecedentes', '')),
            "extended_history": str(source.get('historia_integral', '')),
            
            "triage_level_text": ia_res.get('nivel', {}).get('text', 'PENDIENTE'),
            "triage_level_color": ia_res.get('nivel', {}).get('color', 'gray'),
            "wait_time": ia_res.get('wait_time', ''),
            "wait_time": ia_res.get('wait_time', ''),
            "ai_reasons": ia_res.get('razones', []),
            "recommendations": record.get('recommendations', source.get('recommendations', [])),
            
            "status": record.get('status', 'Borrador').upper(),
            "disposition": record.get('disposition', '-'),
            "validator": record.get('validator_id', 'Sistema'),
            "signature_hash": str(record.get('_id', ''))[-8:].upper() # Mock signature
        }
    except Exception as e:
        print(f"Error extracting clinical data: {e}")
        return {
            "patient_name": "ERROR DE DATOS",
            "motivo_consulta": f"Error al extraer datos: {str(e)}",
            "triage_level_text": "ERROR",
            "triage_level_color": "red",
            "status": "ERROR"
        }

def generate_triage_report(triage_id: str) -> bytes:
    """Genera reporte final desde DB con manejo robusto de errores."""
    try:
        repo = get_triage_repository()
        record = repo.get_by_audit_id(triage_id)
        
        if not record:
            # En lugar de fallar, creamos un registro dummy de error
            print(f"Warning: Record {triage_id} not found. Generating error report.")
            record = {
                "_id": "ERROR",
                "patient_id": "UNKNOWN",
                "patient_snapshot": {
                    "nombre": "ERROR: REGISTRO NO ENCONTRADO",
                    "apellido1": "",
                    "motivo_consulta": f"No se encontró el registro de triaje con ID: {triage_id}. Es posible que no se haya guardado correctamente en la base de datos."
                },
                "status": "ERROR",
                "ia_result": {
                    "nivel": {"text": "DATOS NO DISPONIBLES", "color": "gray"}
                }
            }
        
        data = _extract_clinical_data(record, is_draft=False)
        return generate_report(data)
        
    except Exception as e:
        print(f"Critical error generating report: {e}")
        # Fallback de último recurso
        try:
            return generate_report({
                "patient_name": "ERROR CRÍTICO",
                "motivo_consulta": f"Fallo total en generación de reporte: {str(e)}",
                "triage_level_text": "SYSTEM ERROR",
                "triage_level_color": "black"
            })
        except:
            # Si incluso el fallback falla, devolvemos un PDF vacío válido o bytes de error
            return b"%PDF-1.4\n%Error generating PDF"

def generate_triage_pdf(triage_record: dict) -> bytes:
    """Genera reporte borrador desde diccionario (Frontend)."""
    try:
        # triage_record aquí suele ser una mezcla de datos del paciente y estado del borrador
        data = _extract_clinical_data(triage_record, is_draft=True)
        return generate_report(data)
    except Exception as e:
        print(f"Error generating draft PDF: {e}")
        return generate_report({
            "patient_name": "ERROR BORRADOR",
            "motivo_consulta": f"Error generando borrador: {str(e)}",
            "is_draft": True
        })

def generate_second_opinion_report(patient_info: dict, context: dict, analysis_result: dict) -> bytes:
    """
    Genera un informe detallado de Segunda Opinión (Reasoning ++) usando ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = _get_styles()
    story = []
    
    # 1. HEADER
    story.append(Paragraph("INFORME DE SEGUNDA OPINIÓN (IA AVANZADA)", styles['ReportTitle']))
    
    # 2. PATIENT INFO (Compact)
    p_profile = context.get('patient_profile', {})
    admin_data = [
        [Paragraph(f"<b>Paciente:</b> {patient_info.get('nombre', 'Desconocido')} {patient_info.get('apellido1', '')}", styles['Normal']),
         Paragraph(f"<b>ID:</b> {patient_info.get('patient_code', 'N/A')}", styles['Normal'])],
        [Paragraph(f"<b>Edad/Sexo:</b> {p_profile.get('age', 'N/A')} / {p_profile.get('gender', 'N/A')}", styles['Normal']),
         Paragraph(f"<b>Fecha Análisis:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal'])]
    ]
    t_admin = Table(admin_data, colWidths=[3.5*inch, 3*inch])
    t_admin.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), colors.aliceblue),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_admin)
    story.append(Spacer(1, 15))

    # 3. CONTEXTO ANALIZADO
    story.append(Paragraph("1. Contexto Analizado", styles['SectionHeader']))
    
    # Antecedentes
    hist = p_profile.get('background', 'No registrado')
    if isinstance(hist, list): hist = ", ".join(hist)
    story.append(Paragraph("<b>Antecedentes Clínicos:</b>", styles['SubSectionHeader']))
    story.append(Paragraph(str(hist), styles['NormalJustified']))
    
    # Triage History (Summary)
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Historial de Episodios Recientes (Resumen):</b>", styles['SubSectionHeader']))
    history = context.get('triage_history', [])
    if history:
        for item in history:
            date_str = item.get('date', '')[:10]
            complaint = item.get('main_complaint', 'Sin motivo')
            level = item.get('ai_level', '?')
            story.append(Paragraph(f"• [{date_str}] Nivel {level}: {complaint}", styles['Normal'], bulletText="•"))
    else:
        story.append(Paragraph("Sin historial reciente relevante.", styles['Normal']))

    story.append(Spacer(1, 15))

    # Archivos Adjuntos Analizados
    attached_files = context.get('analyzed_files', [])
    if attached_files:
        story.append(Paragraph("<b>Archivos de Soporte Analizados:</b>", styles['SubSectionHeader']))
        for f_meta in attached_files:
            # f_meta is like "[IMAGEN: filename.jpg]" or "[TEXTO: filename.txt]"
            story.append(Paragraph(f"• {f_meta}", styles['Normal'], bulletText="•"))
        story.append(Spacer(1, 15))
        
    # Protocolos RAG
    protocols = context.get("rag_protocols", [])
    if protocols:
        story.append(Paragraph("<b>Protocolos Institucionales Consultados:</b>", styles['SubSectionHeader']))
        for p in protocols:
            snippet = p[:200] + "..." if len(p) > 200 else p
            story.append(Paragraph(f"- {snippet}", styles['Normal']))
        story.append(Spacer(1, 15))

    # 4. ANÁLISIS DE IA (Estructurado)
    story.append(Paragraph("2. Análisis Clínico de Inteligencia Artificial", styles['SectionHeader']))
    
    # Parseo de la respuesta
    data = analysis_result
    parsed = None
    if isinstance(data, dict):
        if "diagnostic_hypothesis" in data: 
             parsed = data
        elif "text" in data:
            try:
                import json
                cleaned = data["text"].strip().replace("```json", "").replace("```", "")
                parsed = json.loads(cleaned)
            except:
                parsed = None

    if parsed:
        # A. Resumen
        if "clinical_summary" in parsed:
            story.append(Paragraph("<b>Resumen del Caso:</b>", styles['SubSectionHeader']))
            story.append(Paragraph(parsed["clinical_summary"], styles['NormalJustified']))
        
        # B. Red Flags
        if "red_flags" in parsed and parsed["red_flags"]:
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>Alertas Clínicas (Red Flags):</b>", styles['SubSectionHeader']))
            for flag in parsed["red_flags"]:
                story.append(Paragraph(f"⚠️ {flag}", styles['WarningText']))
                
        # C. Diagnóstico Diferencial
        if "diagnostic_hypothesis" in parsed and parsed["diagnostic_hypothesis"]:
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>Hipótesis Diagnósticas:</b>", styles['SubSectionHeader']))
            for diag in parsed["diagnostic_hypothesis"]:
                d_name = diag.get("diagnosis", "Unknown")
                d_prob = diag.get("probability", "")
                d_just = diag.get("justification", "")
                
                # Bold title with probability
                story.append(Paragraph(f"<b>{d_name}</b> ({d_prob})", styles['Normal']))
                story.append(Paragraph(f"<i>Justificación:</i> {d_just}", styles['NormalJustified']))
                story.append(Spacer(1, 5))
        
        # D. Plan de Acción
        if "recommended_actions" in parsed and parsed["recommended_actions"]:
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>Plan de Acción Recomendado:</b>", styles['SubSectionHeader']))
            for act in parsed["recommended_actions"]:
                story.append(Paragraph(f"• {act}", styles['NormalJustified'], bulletText="•"))
                
        # E. Chain of Thought (Opcional, en nueva página)
        if "thought_process" in parsed:
            story.append(PageBreak())
            story.append(Paragraph("Anexo: Razonamiento Detallado (Chain of Thought)", styles['SectionHeader']))
            # Use smaller font for lengthy thought process
            styles.add(ParagraphStyle(name='CodeText', parent=styles['Normal'], fontName='Courier', fontSize=9, leading=11))
            story.append(Paragraph(parsed["thought_process"].replace('\n', '<br/>'), styles['CodeText']))
            
    else:
        # Fallback raw text
        raw_text = data.get("text", str(data)) if isinstance(data, dict) else str(data)
        story.append(Paragraph(raw_text.replace('\n', '<br/>'), styles['NormalJustified']))

    # 5. CONTROL DE CALIDAD / FEEDBACK HUMANO (NUEVO)
    import streamlit as st
    feedback_data = st.session_state.get("sec_op_feedback_data")
    
    if feedback_data:
        story.append(Spacer(1, 20))
        story.append(Paragraph("VALIDACIÓN HUMANA (Feedback)", styles['SectionHeader']))
        
        rating = feedback_data.get("rating")
        reason = feedback_data.get("reason")
        
        # Icono visual
        icon_html = "✅ <font color='green'>CORRECTO</font>" if rating == "positive" else "❌ <font color='red'>INCORRECTO</font>"
        
        story.append(Paragraph(f"<b>Calificación del Profesional:</b> {icon_html}", styles['Normal']))
        
        if reason:
             story.append(Spacer(1, 5))
             story.append(Paragraph(f"<b>Observaciones / Corrección:</b>", styles['SubSectionHeader']))
             story.append(Paragraph(f"<i>{reason}</i>", styles['Normal']))
             
    # 6. FOOTER / DISCLAIMER
    story.append(Spacer(1, 30))
    story.append(Paragraph("AVISO LEGAL: Este informe es generado por un sistema de Inteligencia Artificial (Gemini 2.5) como herramienta de soporte a la decisión clínica. NO SUSTITUYE el juicio profesional médico. El facultativo es responsable de verificar toda la información.", styles['SmallText']))
    
    # Build
    try:
        doc.build(story)
    except Exception as e:
        # Fallback simple
        print(f"ReportLab Build Error: {e}")
        return b"%PDF-Error"
        
    buffer.seek(0)
    return buffer.getvalue()
