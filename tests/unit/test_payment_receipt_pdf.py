from backend.modules.payments.pdf import create_receipt_pdf


def test_payment_receipt_pdf_has_valid_header():
    receipt={"business_name":"Comercio Inteligente","sale_number":"VTA-000001","sale_date":"2026-09-08 12:00:00","customer_name":"Cliente Demo","customer_document":"0999999999","payment_id":"68bf00000000000000000001","payment_method":"Tarjeta tokenizada","items":[{"name":"Café molido","sku":"CAF-001","quantity":2,"unit_price":"$4.00","line_total":"$8.00"}],"sale_total":"$8.00","payment_amount":"$8.00","remaining_due":"$0.00","generated_at":"2026-09-08 12:01:00"}
    stream=create_receipt_pdf(receipt)
    assert stream.read(4)==b"%PDF"
