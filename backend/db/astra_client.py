from astrapy import DataAPIClient
from config import settings
import logging

logger = logging.getLogger(__name__)

_client = None
_db = None


def get_db():
    global _client, _db
    if _db is not None:
        return _db
    try:
        _client = DataAPIClient(settings.ASTRA_DB_APPLICATION_TOKEN)
        _db = _client.get_database(
            settings.ASTRA_DB_API_ENDPOINT,
            namespace=settings.ASTRA_DB_KEYSPACE,
        )
        logger.info("Connected to Astra DB at %s", settings.ASTRA_DB_API_ENDPOINT)
        return _db
    except Exception as e:
        logger.error("Failed to connect to Astra DB: %s", e)
        raise


def get_collection(name: str):
    db = get_db()
    return db.get_collection(name)


def healthcheck() -> bool:
    try:
        db = get_db()
        collections = db.list_collection_names()
        return True
    except Exception as e:
        logger.error("Astra DB healthcheck failed: %s", e)
        return False
