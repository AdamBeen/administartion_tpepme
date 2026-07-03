from db.astra_client import get_db
import logging

logger = logging.getLogger(__name__)

COLLECTIONS = [
    "kg_nodes",
    "kg_edges",
    "kg_edges_by_source",
    "kg_edges_by_target",
    "vector_chunks",
    "workflow_runs",
    "workflow_errors",
    "workflow_traces",
    "graphrag_paths",
]


def init_schema():
    db = get_db()
    existing = db.list_collection_names()
    created = []
    for name in COLLECTIONS:
        if name not in existing:
            db.create_collection(name)
            created.append(name)
            logger.info("Created collection: %s", name)
    if not created:
        logger.info("All collections already exist.")
    return created


def drop_all_collections():
    db = get_db()
    existing = db.list_collection_names()
    for name in COLLECTIONS:
        if name in existing:
            db.drop_collection(name)
            logger.info("Dropped collection: %s", name)


if __name__ == "__main__":
    init_schema()
    print("Schema initialized.")
