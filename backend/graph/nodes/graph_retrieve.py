import time
import json
import logging
from graph.state import AdminTPEState
from db.kg_store import get_all_nodes, find_paths_multi_hop, get_node

logger = logging.getLogger(__name__)


def node_graph_retrieve_paths(state: AdminTPEState) -> dict:
    start = time.time()
    graph_query = state.get("graph_query", "[]")
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    try:
        keywords = json.loads(graph_query)
    except json.JSONDecodeError:
        keywords = []

    all_nodes = get_all_nodes()
    matched_nodes = []
    for node in all_nodes:
        label = node.get("label", "").lower()
        node_id = node.get("node_id", "").lower()
        node_type = node.get("node_type", "").lower()
        description = node.get("description", "").lower()
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in label or kw_lower in node_id or kw_lower in node_type or kw_lower in description:
                matched_nodes.append(node)
                break

    if not matched_nodes:
        for node in all_nodes:
            if node.get("node_type") in ["Aide", "Autorisation", "Recours"]:
                matched_nodes.append(node)
        matched_nodes = matched_nodes[:15]

    paths = []
    seen = set()
    for node in matched_nodes[:15]:
        node_id = node.get("node_id", "")
        raw_paths = find_paths_multi_hop(node_id, max_depth=3)
        for rp in raw_paths[:5]:
            path_key = tuple(rp["nodes"])
            if path_key not in seen:
                seen.add(path_key)
                node_labels = []
                for nid in rp["nodes"]:
                    n = get_node(nid)
                    node_labels.append(n.get("label", nid) if n else nid)
                paths.append({
                    "chemin": " -> ".join(node_labels),
                    "noeuds": rp["nodes"],
                    "relations": rp["relations"],
                    "interpretation": f"Chemin relationnel depuis {node_labels[0]}",
                })
        if len(paths) >= 30:
            break

    if not paths:
        errors.append({
            "node_name": "node_graph_retrieve_paths",
            "error_type": "no_paths",
            "message": "Aucun chemin pertinent trouvé.",
            "user_explanation": "Aucun chemin pertinent n'a été trouvé dans le Knowledge Graph.",
            "suggestion": "Vérifiez que les nœuds et relations administratives ont été ingérés.",
        })

    status = "warning" if not paths else "success"
    debug_trace.append({
        "node_name": "node_graph_retrieve_paths",
        "status": status,
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"keywords={len(keywords)}",
        "output_summary": f"paths={len(paths)}, matched_nodes={len(matched_nodes)}",
    })

    timings = state.get("timings", {})
    timings["node_graph_retrieve_paths"] = time.time() - start

    return {
        "graph_paths": paths,
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
