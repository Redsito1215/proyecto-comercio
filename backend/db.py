from contextlib import contextmanager

from pymongo import MongoClient

from backend.config import get_settings

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(get_settings().mongo_uri, serverSelectionTimeoutMS=3000)
    return _client


def get_db():
    return get_client()[get_settings().mongo_db]


@contextmanager
def transaction():
    with get_client().start_session() as session:
        with session.start_transaction():
            yield session


def ping() -> bool:
    return bool(get_client().admin.command("ping").get("ok"))
