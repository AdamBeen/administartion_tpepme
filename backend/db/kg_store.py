from db.astra_client import get_collection
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def upsert_node(node: dict) -> bool:
    try:
        col = get_collection("kg_nodes")
        now = datetime.now(timezone.utc).isoformat()
        node.setdefault("created_at", now)
        node["updated_at"] = now
        col.replace_one({"node_id": node["node_id"]}, node, upsert=True)
        return True
    except Exception as e:
        logger.error("Failed to upsert node %s: %s", node.get("node_id"), e)
        return False


def upsert_edge(edge: dict) -> bool:
    try:
        col = get_collection("kg_edges")
        now = datetime.now(timezone.utc).isoformat()
        edge.setdefault("created_at", now)
        col.replace_one({"edge_id": edge["edge_id"]}, edge, upsert=True)

        by_source = get_collection("kg_edges_by_source")
        by_source.replace_one(
            {"edge_id": edge["edge_id"]},
            {
                "source_node_id": edge["source_node_id"],
                "relation_type": edge["relation_type"],
                "target_node_id": edge["target_node_id"],
                "edge_id": edge["edge_id"],
            },
            upsert=True,
        )

        by_target = get_collection("kg_edges_by_target")
        by_target.replace_one(
            {"edge_id": edge["edge_id"]},
            {
                "target_node_id": edge["target_node_id"],
                "relation_type": edge["relation_type"],
                "source_node_id": edge["source_node_id"],
                "edge_id": edge["edge_id"],
            },
            upsert=True,
        )
        return True
    except Exception as e:
        logger.error("Failed to upsert edge %s: %s", edge.get("edge_id"), e)
        return False


def get_node(node_id: str) -> dict | None:
    try:
        col = get_collection("kg_nodes")
        return col.find_one({"node_id": node_id})
    except Exception as e:
        logger.error("Failed to get node %s: %s", node_id, e)
        return None


def get_all_nodes() -> list[dict]:
    try:
        col = get_collection("kg_nodes")
        return list(col.find({}))
    except Exception as e:
        logger.error("Failed to get all nodes: %s", e)
        return []


def get_all_edges() -> list[dict]:
    try:
        col = get_collection("kg_edges")
        return list(col.find({}))
    except Exception as e:
        logger.error("Failed to get all edges: %s", e)
        return []


def get_edges_from(source_node_id: str) -> list[dict]:
    try:
        col = get_collection("kg_edges_by_source")
        return list(col.find({"source_node_id": source_node_id}))
    except Exception as e:
        logger.error("Failed to get edges from %s: %s", source_node_id, e)
        return []


def get_edges_to(target_node_id: str) -> list[dict]:
    try:
        col = get_collection("kg_edges_by_target")
        return list(col.find({"target_node_id": target_node_id}))
    except Exception as e:
        logger.error("Failed to get edges to %s: %s", target_node_id, e)
        return []


def find_paths_multi_hop(start_node_id: str, max_depth: int = 3) -> list[dict]:
    paths = []

    def _dfs(current_id: str, visited: list[str], relations: list[str], depth: int):
        if depth >= max_depth:
            return
        edges = get_edges_from(current_id)
        for edge in edges:
            target = edge.get("target_node_id", "")
            if target in visited:
                continue
            new_visited = visited + [target]
            new_relations = relations + [edge.get("relation_type", "")]
            paths.append(
                {
                    "nodes": new_visited,
                    "relations": new_relations,
                    "path_text": " -> ".join(new_visited),
                }
            )
            _dfs(target, new_visited, new_relations, depth + 1)

    _dfs(start_node_id, [start_node_id], [], 0)
    return paths
