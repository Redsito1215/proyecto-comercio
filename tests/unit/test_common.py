from decimal import Decimal

from bson import Decimal128

from backend.common.serialization import to_json, to_mongo
from backend.config import Settings


def test_settings_have_safe_defaults():
    settings = Settings(_env_file=None)
    assert settings.mongo_db == "comercio_inteligente"
    assert settings.app_port == 5001


def test_decimal_round_trip():
    stored = to_mongo({"total": Decimal("10.25")})
    assert isinstance(stored["total"], Decimal128)
    assert to_json(stored) == {"total": "10.25"}
