from backend.modules.reports.pdf import create_pdf


def test_pdf_has_valid_signature_and_content():
    snapshot={"title":"Informe de prueba","generated_at":"2026-09-04T10:00:00+00:00","sections":[{"label":"Ventas","columns":["Número","Total"],"rows":[["VTA-1","10.00"]],"metrics":{"operaciones":1}}]}
    data=create_pdf(snapshot).read();assert data.startswith(b'%PDF-') and len(data)>1000
