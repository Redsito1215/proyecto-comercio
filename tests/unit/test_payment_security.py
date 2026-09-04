from decimal import Decimal
from backend.modules.payments.gateway import LocalSandboxGateway


def test_sandbox_is_explicitly_not_production_ready():
    gateway=LocalSandboxGateway();assert gateway.name=='local-sandbox' and gateway.production_ready is False


def test_sandbox_uses_token_outcome_without_card_data():
    assert LocalSandboxGateway().charge('tok_approved_test',Decimal('5'))['status']=='approved'
    assert LocalSandboxGateway().charge('tok_declined_test',Decimal('5'))['status']=='declined'
