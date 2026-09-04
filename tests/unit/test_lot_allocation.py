from backend.modules.core.services import allocate_lot_quantities


def test_fefo_uses_earliest_expiry_first():
    lots = [
        {"_id": "late", "available_quantity": 5, "expires_at": "2027-02-01"},
        {"_id": "early", "available_quantity": 2, "expires_at": "2027-01-01"},
    ]
    assert allocate_lot_quantities(lots, 4) == [
        {"lot_id": "early", "quantity": 2}, {"lot_id": "late", "quantity": 2},
    ]


def test_fefo_rejects_insufficient_lots():
    try:
        allocate_lot_quantities([{"_id": "one", "available_quantity": 1, "expires_at": None}], 2)
        assert False, "Debió rechazar cantidad insuficiente"
    except ValueError as error:
        assert "insuficiente" in str(error).lower()
