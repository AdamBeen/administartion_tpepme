import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.astra_client import get_collection
from db.schema import init_schema
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_kg():
    init_schema()

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "kg_seed.json",
    )
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    now = datetime.now(timezone.utc).isoformat()

    for node in nodes:
        node.setdefault("created_at", now)
        node["updated_at"] = now

    for edge in edges:
        edge.setdefault("created_at", now)

    by_source_docs = [
        {
            "source_node_id": e["source_node_id"],
            "relation_type": e["relation_type"],
            "target_node_id": e["target_node_id"],
            "edge_id": e["edge_id"],
        }
        for e in edges
    ]
    by_target_docs = [
        {
            "target_node_id": e["target_node_id"],
            "relation_type": e["relation_type"],
            "source_node_id": e["source_node_id"],
            "edge_id": e["edge_id"],
        }
        for e in edges
    ]

    logger.info("Inserting %d nodes in batch...", len(nodes))
    nodes_col = get_collection("kg_nodes")
    nodes_col.delete_many({})
    nodes_col.insert_many(nodes)
    logger.info("Nodes inserted: %d", len(nodes))

    logger.info("Inserting %d edges in batch...", len(edges))
    edges_col = get_collection("kg_edges")
    edges_col.delete_many({})
    edges_col.insert_many(edges)
    logger.info("Edges inserted: %d", len(edges))

    logger.info("Inserting %d edge indexes (by_source)...", len(by_source_docs))
    by_source_col = get_collection("kg_edges_by_source")
    by_source_col.delete_many({})
    by_source_col.insert_many(by_source_docs)

    logger.info("Inserting %d edge indexes (by_target)...", len(by_target_docs))
    by_target_col = get_collection("kg_edges_by_target")
    by_target_col.delete_many({})
    by_target_col.insert_many(by_target_docs)

    print(f"Knowledge Graph seeded: {len(nodes)} nodes, {len(edges)} edges (batch mode).")


if __name__ == "__main__":
    seed_kg()
