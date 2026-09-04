from backend.modules.core.services import validate_return_quantity


def test_return_quantity_respects_previous_returns():
    assert validate_return_quantity(5, 2, 3) == 3
    try:
        validate_return_quantity(5, 2, 4)
        assert False
    except ValueError:
        pass
