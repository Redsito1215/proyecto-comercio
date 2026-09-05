from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph,SimpleDocTemplate,Spacer,Table,TableStyle


def create_audit_pdf(rows):
    stream=BytesIO();styles=getSampleStyleSheet();page=landscape(A4)
    document=SimpleDocTemplate(stream,pagesize=page,leftMargin=14*mm,rightMargin=14*mm,topMargin=14*mm,bottomMargin=14*mm,title="Auditoría de seguridad")
    data=[["Fecha","Acción","Entidad","Actor","Resultado"]]+[[str(row.get("occurred_at",""))[:19].replace("T"," "),row.get("action","-"),row.get("entity_type","-"),row.get("actor_id","-"),row.get("outcome","-")] for row in rows]
    if len(data)==1:data.append(["Sin eventos para los filtros seleccionados","","","",""])
    table=Table(data,colWidths=[42*mm,54*mm,38*mm,75*mm,30*mm],repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#132033")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7.5),("GRID",(0,0),(-1,-1),.3,colors.HexColor("#CBD5E1")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F7FA")]),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story=[Paragraph("Informe de auditoría y seguridad",styles["Title"]),Paragraph(f"Eventos incluidos: {len(rows)}",styles["BodyText"]),Spacer(1,5*mm),table]
    document.build(story);stream.seek(0);return stream
