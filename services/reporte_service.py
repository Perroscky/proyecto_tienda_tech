# services/reporte_service.py
import os
from datetime import datetime
from reportlab.lib import colors # pyright: ignore[reportMissingModuleSource]
from reportlab.lib.pagesizes import letter, landscape # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore
from reportlab.lib.units import inch # type: ignore
from reportlab.pdfbase import pdfmetrics # pyright: ignore[reportMissingModuleSource]
from reportlab.pdfbase.ttfonts import TTFont # pyright: ignore[reportMissingModuleSource]
from reportlab.lib.fonts import addMapping # pyright: ignore[reportMissingModuleSource]

class ReporteService:
    """Servicio para generar reportes en PDF"""
    
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generar_reporte_productos(self, productos, titulo="Reporte de Productos"):
        """Generar reporte PDF con lista de productos"""
        
        filename = f"reporte_productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Crear documento
        doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            alignment=1,
            spaceAfter=30
        )
        story.append(Paragraph(titulo, titulo_style))
        
        # Fecha de generación
        fecha_style = ParagraphStyle(
            'FechaStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", fecha_style))
        story.append(Spacer(1, 20))
        
        # Datos de la tabla
        data = [['ID', 'Nombre', 'Precio', 'Cantidad', 'Categoría', 'Descripción']]
        
        total_valor = 0
        total_productos = 0
        
        for p in productos:
            data.append([
                str(p.get('id', '')),
                p.get('nombre', ''),
                f"${p.get('precio', 0):.2f}",
                str(p.get('cantidad', 0)),
                p.get('categoria', ''),
                p.get('descripcion', '')[:50] + ('...' if len(p.get('descripcion', '')) > 50 else '')
            ])
            total_valor += p.get('precio', 0) * p.get('cantidad', 0)
            total_productos += 1
        
        # Agregar fila de totales
        data.append(['', '', '', '', '', ''])
        data.append(['', '', '', '', 'TOTAL PRODUCTOS:', str(total_productos)])
        data.append(['', '', '', '', 'VALOR TOTAL INVENTARIO:', f"${total_valor:.2f}"])
        
        # Crear tabla
        table = Table(data, colWidths=[50, 120, 70, 60, 90, 180])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (5, 0), (5, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('SPAN', (0, -3), (4, -3)),
            ('SPAN', (0, -2), (4, -2)),
            ('SPAN', (0, -1), (4, -1)),
        ]))
        
        story.append(table)
        
        # Pie de página
        story.append(Spacer(1, 30))
        pie_style = ParagraphStyle(
            'PieStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph("Tienda Tech Online - Sistema de Gestión de Inventarios", pie_style))
        story.append(Paragraph(f"Documento generado automáticamente el {datetime.now().strftime('%d/%m/%Y')}", pie_style))
        
        # Construir PDF
        doc.build(story)
        
        return filename, filepath
    
    def generar_reporte_bajo_stock(self, productos):
        """Generar reporte de productos con bajo stock"""
        
        filename = f"reporte_bajo_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#e74c3c'),
            alignment=1,
            spaceAfter=20
        )
        story.append(Paragraph("⚠️ Productos con Bajo Stock", titulo_style))
        
        # Fecha
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Datos
        data = [['ID', 'Nombre', 'Stock Actual', 'Precio', 'Categoría']]
        
        for p in productos:
            data.append([
                str(p.get('id', '')),
                p.get('nombre', ''),
                str(p.get('cantidad', 0)),
                f"${p.get('precio', 0):.2f}",
                p.get('categoria', '')
            ])
        
        table = Table(data, colWidths=[50, 180, 70, 70, 90])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table)
        
        doc.build(story)
        return filename, filepath
    
    def generar_reporte_por_categoria(self, productos, categoria):
        """Generar reporte de productos por categoría"""
        
        filename = f"reporte_categoria_{categoria}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2ecc71'),
            alignment=1,
            spaceAfter=20
        )
        
        # Mapeo de categorías a íconos
        iconos = {
            'computadoras': '💻',
            'perifericos': '🖱️',
            'audio': '🎧',
            'celulares': '📱',
            'tablets': '📲',
            'otros': '📦'
        }
        icono = iconos.get(categoria, '📦')
        
        story.append(Paragraph(f"{icono} Productos - Categoría: {categoria.title()}", titulo_style))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Datos
        data = [['ID', 'Nombre', 'Precio', 'Stock']]
        
        total_valor = 0
        for p in productos:
            data.append([
                str(p.get('id', '')),
                p.get('nombre', ''),
                f"${p.get('precio', 0):.2f}",
                str(p.get('cantidad', 0))
            ])
            total_valor += p.get('precio', 0) * p.get('cantidad', 0)
        
        table = Table(data, colWidths=[50, 200, 80, 60])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Valor total de inventario en esta categoría: ${total_valor:.2f}", styles['Normal']))
        
        doc.build(story)
        return filename, filepath