from datetime import date, datetime
from decimal import Decimal

from bson import Decimal128, ObjectId


def to_mongo(value):
    if isinstance(value, Decimal):
        return Decimal128(value)
    if isinstance(value, dict):
        return {key: to_mongo(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_mongo(item) for item in value]
    return value


def to_json(value):
    if isinstance(value, Decimal128):
        return str(value.to_decimal())
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: to_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_json(item) for item in value]
    return value
