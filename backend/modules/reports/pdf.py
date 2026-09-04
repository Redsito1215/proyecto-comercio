from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak,Paragraph,SimpleDocTemplate,Spacer,Table,TableStyle


def create_pdf(snapshot):
    buffer=BytesIO();styles=getSampleStyleSheet();accent=colors.HexColor("#2FAE9B");ink=colors.HexColor("#132033");muted=colors.HexColor("#64748B")
    doc=SimpleDocTemplate(buffer,pagesize=landscape(A4),rightMargin=14*mm,leftMargin=14*mm,topMargin=16*mm,bottomMargin=15*mm,title=snapshot["title"],author="Comercio Inteligente")
    story=[Paragraph(snapshot["title"],ParagraphStyle("TitleCI",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=22,textColor=ink,spaceAfter=5)),Paragraph(f'Generado: {snapshot["generated_at"][:19].replace("T"," ")} UTC',ParagraphStyle("Meta",parent=styles["BodyText"],fontSize=8,textColor=muted)),Spacer(1,7*mm)]
    for index,section in enumerate(snapshot["sections"]):
        if index:story.append(PageBreak())
        story.append(Paragraph(section["label"],ParagraphStyle("Section",parent=styles["Heading1"],fontName="Helvetica-Bold",fontSize=16,textColor=accent,spaceAfter=4*mm)))
        metrics="   ".join(f'{key.replace("_"," ").title()}: {value}' for key,value in section["metrics"].items());story.append(Paragraph(metrics or "Sin indicadores",ParagraphStyle("Metrics",parent=styles["BodyText"],fontSize=9,textColor=ink,spaceAfter=4*mm)))
        data=[section["columns"]]+[[str(cell)[:70] for cell in row] for row in section["rows"][:100]]
        if len(data)==1:data.append(["Sin datos para el período"]+[""]*(len(section["columns"])-1))
        widths=[(landscape(A4)[0]-28*mm)/len(section["columns"])]*len(section["columns"]);table=Table(data,colWidths=widths,repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),ink),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),7.5),("GRID",(0,0),(-1,-1),.3,colors.HexColor("#CBD5E1")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F7FA")]),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]));story.append(table)
    def footer(canvas,_doc):
        canvas.saveState();canvas.setFont("Helvetica",7);canvas.setFillColor(muted);canvas.drawString(14*mm,8*mm,"Comercio Inteligente - Documento generado desde una instantánea auditable");canvas.drawRightString(landscape(A4)[0]-14*mm,8*mm,f"Página {canvas.getPageNumber()}");canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer);buffer.seek(0);return buffer
