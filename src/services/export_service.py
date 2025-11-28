# path: src/services/export_service.py
# Creado: 2025-11-26
"""
Servicio para la generación y exportación de reportes (PDF, Excel).
"""
import pandas as pd
from io import BytesIO
from datetime import datetime
from fpdf import FPDF
from typing import Dict, List, Any
from services.room_metrics_service import obtener_metricas_errores, obtener_historial_errores

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Reporte de Gestión de Salas - Triaje IA', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}} - Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'C')

def generate_metrics_pdf(periodo_dias: int = 7) -> bytes:
    """
    Genera un reporte PDF con las métricas de errores.
    
    Args:
        periodo_dias: Días del periodo a reportar
        
    Returns:
        bytes: Contenido del archivo PDF
    """
    metricas = obtener_metricas_errores(dias=periodo_dias)
    errores = obtener_historial_errores(limit=50, solo_pendientes=False)
    
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Título del periodo
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Período del reporte: Últimos {periodo_dias} días', 0, 1)
    pdf.ln(5)
    
    # Sección de KPIs
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Resumen Ejecutivo (KPIs)', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    # Dibujar una "tabla" simple para los KPIs
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(95, 10, f"Total Errores: {metricas['total_errores']}", 1, 0, 'L', 1)
    pdf.cell(95, 10, f"Tasa Resolución: {metricas['tasa_resolucion']}%", 1, 1, 'L', 1)
    pdf.cell(95, 10, f"Pendientes: {metricas['pendientes']}", 1, 0, 'L', 1)
    pdf.cell(95, 10, f"Tiempo Promedio: {metricas['tiempo_promedio_minutos']} min", 1, 1, 'L', 1)
    pdf.ln(10)
    
    # Sección de Desglose
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Desglose por Motivo', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    if metricas['por_motivo']:
        for motivo, count in metricas['por_motivo'].items():
            pdf.cell(0, 8, f"- {motivo}: {count}", 0, 1)
    else:
        pdf.cell(0, 8, "No hay datos registrados.", 0, 1)
    pdf.ln(10)
    
    # Tabla de últimos errores
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Últimos 50 Registros', 0, 1)
    pdf.ln(5)
    
    # Encabezados de tabla
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(35, 8, 'Fecha', 1, 0, 'C', 1)
    pdf.cell(25, 8, 'ID Paciente', 1, 0, 'C', 1)
    pdf.cell(25, 8, 'Sala', 1, 0, 'C', 1)
    pdf.cell(45, 8, 'Motivo', 1, 0, 'C', 1)
    pdf.cell(30, 8, 'Estado', 1, 0, 'C', 1)
    pdf.cell(30, 8, 'Resolución', 1, 1, 'C', 1)
    
    # Filas
    pdf.set_font('Arial', '', 9)
    for error in errores:
        fecha = error.get('detected_at', datetime.now()).strftime("%d/%m %H:%M")
        paciente = str(error.get('patient_code', 'N/A'))[:10]
        sala = str(error.get('sala_erronea', 'N/A'))[:8]
        motivo = str(error.get('motivo_error', 'N/A'))[:20]
        estado = "Resuelto" if error.get('resolved') else "Pendiente"
        resolucion = str(error.get('resolution_type', '-'))[:15] if error.get('resolved') else '-'
        
        pdf.cell(35, 8, fecha, 1, 0, 'C')
        pdf.cell(25, 8, paciente, 1, 0, 'C')
        pdf.cell(25, 8, sala, 1, 0, 'C')
        pdf.cell(45, 8, motivo, 1, 0, 'L')
        pdf.cell(30, 8, estado, 1, 0, 'C')
        pdf.cell(30, 8, resolucion, 1, 1, 'C')
        
    return bytes(pdf.output())

def generate_excel_export(periodo_dias: int = 7) -> bytes:
    """
    Genera un archivo Excel con las métricas y el historial detallado.
    
    Args:
        periodo_dias: Días del periodo a reportar
        
    Returns:
        bytes: Contenido del archivo Excel
    """
    metricas = obtener_metricas_errores(dias=periodo_dias)
    errores = obtener_historial_errores(limit=1000, solo_pendientes=False)
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Resumen
        resumen_data = [{
            "Periodo (Días)": periodo_dias,
            "Fecha Generación": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total Errores": metricas['total_errores'],
            "Resueltos": metricas['resueltos'],
            "Pendientes": metricas['pendientes'],
            "Tasa Resolución (%)": metricas['tasa_resolucion'],
            "Tiempo Promedio (min)": metricas['tiempo_promedio_minutos']
        }]
        df_resumen = pd.DataFrame(resumen_data)
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Sheet 2: Detalle Errores
        if errores:
            df_errores = pd.DataFrame(errores)
            # Limpiar/Formatear columnas si es necesario
            if '_id' in df_errores.columns:
                df_errores['_id'] = df_errores['_id'].astype(str)
            if 'detected_at' in df_errores.columns:
                df_errores['detected_at'] = df_errores['detected_at'].dt.strftime("%Y-%m-%d %H:%M:%S")
            if 'resolved_at' in df_errores.columns:
                df_errores['resolved_at'] = df_errores['resolved_at'].dt.strftime("%Y-%m-%d %H:%M:%S")
                
            df_errores.to_excel(writer, sheet_name='Detalle Errores', index=False)
        else:
            pd.DataFrame(["No hay datos"]).to_excel(writer, sheet_name='Detalle Errores', index=False)
            
        # Sheet 3: Desglose Motivos
        if metricas['por_motivo']:
            df_motivos = pd.DataFrame(list(metricas['por_motivo'].items()), columns=['Motivo', 'Cantidad'])
            df_motivos.to_excel(writer, sheet_name='Por Motivo', index=False)
            
    output.seek(0)
    return output.read()
