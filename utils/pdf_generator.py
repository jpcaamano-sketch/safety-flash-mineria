"""
Safety_Flash Pro - PDF Generator
Formato: REPORTE FLASH según especificación
"""

import io
from datetime import datetime
from typing import Optional, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def generate_flash_report_pdf(
    report: Dict,
    photo_bytes: Optional[bytes] = None
) -> bytes:
    """
    Genera PDF con formato REPORTE FLASH

    Franjas:
    1. Título y subtítulo
    2. Datos quien reporta | Datos ubicación
    3. Foto del incidente | Transcripción del audio
    4. Descripción del incidente (IA) | Acciones inmediatas (IA)
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a1a"),
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor("#666666")
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#333333"),
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_JUSTIFY,
        leading=12
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#333333")
    )

    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#000000")
    )

    elements = []

    # Extraer datos
    worker = report.get("worker_info", {})
    location = report.get("location_info", {})
    transcription = report.get("transcripcion_audio", "") or report.get("audio_transcription", "")
    descripcion_ia = report.get("descripcion_tecnica", "") or report.get("ai_description", "")
    acciones_ia = report.get("acciones_inmediatas", []) or report.get("ai_immediate_actions", [])

    # ========== FRANJA 1: TÍTULO ==========
    elements.append(Paragraph("REPORTE FLASH", title_style))
    elements.append(Paragraph("Reporte de Incidentes de Seguridad", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#333333")))
    elements.append(Spacer(1, 0.2 * inch))

    # ========== FRANJA 2: DATOS QUIEN REPORTA | DATOS UBICACIÓN ==========
    # Crear tabla de 2 columnas
    col_width = 3.5 * inch

    # Columna izquierda: Datos quien reporta
    left_data = [
        [Paragraph("<b>Datos quien reporta</b>", section_header_style)],
        [Paragraph(f"<b>Nombre:</b> {worker.get('name', 'N/A')}", value_style)],
        [Paragraph(f"<b>Cargo:</b> {worker.get('cargo', 'N/A')}", value_style)],
        [Paragraph(f"<b>Antigüedad:</b> {worker.get('antiguedad', 'N/A')}", value_style)],
    ]

    # Columna derecha: Datos ubicación
    right_data = [
        [Paragraph("<b>Datos de ubicación</b>", section_header_style)],
        [Paragraph(f"<b>Ubicación:</b> {location.get('name', 'N/A')}", value_style)],
        [Paragraph(f"<b>Nivel:</b> {location.get('nivel', 'N/A')}", value_style)],
        [Paragraph(f"<b>Sector:</b> {location.get('sector', 'N/A')}", value_style)],
    ]

    # Combinar en una tabla de 2 columnas
    franja2_data = []
    for i in range(len(left_data)):
        franja2_data.append([left_data[i][0], right_data[i][0]])

    franja2_table = Table(franja2_data, colWidths=[col_width, col_width])
    franja2_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#cccccc")),
    ]))
    elements.append(franja2_table)
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 0.15 * inch))

    # ========== FRANJA 3: FOTO | TRANSCRIPCIÓN ==========
    # Preparar foto
    photo_element = Paragraph("[Sin foto]", body_style)
    if photo_bytes:
        try:
            from PIL import Image as PILImage
            img_buffer = io.BytesIO(photo_bytes)
            pil_img = PILImage.open(img_buffer)

            # Tamaño máximo para la foto
            max_width = 3 * inch
            max_height = 2.5 * inch

            img_width, img_height = pil_img.size
            ratio = min(max_width / img_width, max_height / img_height)
            new_width = img_width * ratio
            new_height = img_height * ratio

            img_buffer.seek(0)
            photo_element = RLImage(img_buffer, width=new_width, height=new_height)
        except Exception:
            photo_element = Paragraph("[Imagen no disponible]", body_style)

    # Preparar transcripción
    transcription_text = transcription if transcription else "Sin transcripción de audio"
    transcription_paragraph = Paragraph(transcription_text, body_style)

    # Tabla Franja 3
    franja3_header = [
        [Paragraph("<b>Foto del Incidente</b>", section_header_style),
         Paragraph("<b>Transcripción del Audio</b>", section_header_style)]
    ]
    franja3_content = [
        [photo_element, transcription_paragraph]
    ]

    franja3_table = Table(franja3_header + franja3_content, colWidths=[col_width, col_width])
    franja3_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (0, 1), (0, 1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#cccccc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#dddddd")),
    ]))
    elements.append(franja3_table)
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 0.15 * inch))

    # ========== FRANJA 4: DESCRIPCIÓN IA | ACCIONES IA ==========
    # Preparar descripción
    descripcion_paragraph = Paragraph(descripcion_ia if descripcion_ia else "Pendiente de análisis", body_style)

    # Preparar acciones
    if isinstance(acciones_ia, list):
        acciones_text = "<br/>".join([f"• {a}" for a in acciones_ia])
    else:
        acciones_text = str(acciones_ia) if acciones_ia else "Pendiente de definir"
    acciones_paragraph = Paragraph(acciones_text, body_style)

    # Tabla Franja 4
    franja4_header = [
        [Paragraph("<b>Descripción del Incidente</b>", section_header_style),
         Paragraph("<b>Acciones Inmediatas</b>", section_header_style)]
    ]
    franja4_content = [
        [descripcion_paragraph, acciones_paragraph]
    ]

    franja4_table = Table(franja4_header + franja4_content, colWidths=[col_width, col_width])
    franja4_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#cccccc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#dddddd")),
    ]))
    elements.append(franja4_table)

    # ========== FOOTER ==========
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#333333")))
    elements.append(Spacer(1, 0.1 * inch))

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666")
    )

    report_number = report.get("report_number", "N/A")
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')

    elements.append(Paragraph(f"Reporte #{report_number} | Generado: {fecha}", footer_style))
    elements.append(Paragraph("Safety Flash Pro - Sistema de Reportes de Incidentes", footer_style))

    # Build PDF
    doc.build(elements)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


def get_pdf_filename(report: Dict) -> str:
    """Genera nombre de archivo para el PDF"""
    report_number = report.get("report_number", "N")
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    return f"ReporteFlash_{report_number}_{date_str}.pdf"
