from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def create_receipt_pdf(receipt):
    stream=BytesIO();styles=getSampleStyleSheet();ink=colors.HexColor("#132033");accent=colors.HexColor("#147D6F");muted=colors.HexColor("#64748B")
    document=SimpleDocTemplate(stream,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=16*mm,title=f'Comprobante {receipt["sale_number"]}',author=receipt["business_name"])
    title=ParagraphStyle("ReceiptTitle",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=22,textColor=ink,spaceAfter=3*mm)
    centered=ParagraphStyle("Centered",parent=styles["BodyText"],alignment=TA_CENTER,textColor=muted,fontSize=8)
    right=ParagraphStyle("Right",parent=styles["BodyText"],alignment=TA_RIGHT,fontSize=9,textColor=ink)
    story=[Paragraph(receipt["business_name"],title),Paragraph("COMPROBANTE DE VENTA",ParagraphStyle("Kind",parent=title,fontSize=14,textColor=accent)),Paragraph("Documento interno - no constituye comprobante tributario autorizado",centered),Spacer(1,7*mm)]
    metadata=[["Venta",receipt["sale_number"],"Fecha",receipt["sale_date"]],["Cliente",receipt["customer_name"],"Identificación",receipt["customer_document"]],["Pago",receipt["payment_id"],"Medio",receipt["payment_method"]]]
    meta=Table(metadata,colWidths=[25*mm,60*mm,27*mm,62*mm]);meta.setStyle(TableStyle([("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(-1,-1),ink),("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F2F5F3")),("BOX",(0,0),(-1,-1),.5,colors.HexColor("#CBD5E1")),("INNERGRID",(0,0),(-1,-1),.25,colors.HexColor("#DCE3E0")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("PADDING",(0,0),(-1,-1),6)]));story.extend([meta,Spacer(1,7*mm)])
    data=[["Producto","SKU","Cantidad","Precio unitario","Total"]]+[[line["name"],line["sku"],str(line["quantity"]),line["unit_price"],line["line_total"]] for line in receipt["items"]]
    table=Table(data,colWidths=[65*mm,28*mm,20*mm,30*mm,31*mm],repeatRows=1);table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),ink),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),8.5),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#CBD5E1")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F7F9F8")]),("ALIGN",(2,1),(-1,-1),"RIGHT"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("PADDING",(0,0),(-1,-1),6)]));story.extend([table,Spacer(1,6*mm)])
    totals=Table([["Total de la venta",receipt["sale_total"]],["Pagado en esta operación",receipt["payment_amount"]],["Saldo posterior",receipt["remaining_due"]]],colWidths=[55*mm,35*mm],hAlign="RIGHT");totals.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("ALIGN",(1,0),(1,-1),"RIGHT"),("FONTSIZE",(0,0),(-1,-1),10),("TEXTCOLOR",(0,0),(-1,-1),ink),("LINEABOVE",(0,-1),(-1,-1),.8,accent),("PADDING",(0,0),(-1,-1),5)]));story.extend([totals,Spacer(1,12*mm),Paragraph("Gracias por su compra",ParagraphStyle("Thanks",parent=styles["Heading2"],alignment=TA_CENTER,textColor=accent)),Paragraph(f'Generado por Comercio Inteligente · {receipt["generated_at"]}',centered)])
    def footer(canvas,_doc):canvas.saveState();canvas.setFont("Helvetica",7);canvas.setFillColor(muted);canvas.drawString(18*mm,9*mm,"Comprobante interno verificable mediante el identificador de pago");canvas.drawRightString(A4[0]-18*mm,9*mm,f"Página {canvas.getPageNumber()}");canvas.restoreState()
    document.build(story,onFirstPage=footer,onLaterPages=footer);stream.seek(0);return stream
