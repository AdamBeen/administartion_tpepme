import time
import json
import logging
from graph.state import AdminTPEState

logger = logging.getLogger(__name__)


def node_merge_contexts(state: AdminTPEState) -> dict:
    start = time.time()
    question = state.get("question_administrateur", "")
    dossier = state.get("dossier_temporaire", {})
    vector_results = state.get("vector_results", [])
    graph_paths = state.get("graph_paths", [])
    debug_trace = state.get("debug_trace", [])

    parts = []
    parts.append(f"QUESTION ADMINISTRATEUR:\n{question}\n")
    parts.append(f"RÉSUMÉ DOSSIER TEMPORAIRE:\n{json.dumps(dossier, ensure_ascii=False, indent=2)[:5000]}\n")

    if vector_results:
        parts.append("RÉSULTATS RAG VECTORIEL:")
        for i, vr in enumerate(vector_results):
            parts.append(f"  [{i+1}] Section: {vr.get('section', '')} | Source: {vr.get('source', '')}")
            parts.append(f"      Extrait: {vr.get('extrait', '')[:300]}")
        parts.append("")

    if graph_paths:
        parts.append("RÉSULTATS GRAPHRAG (chemins multi-hop):")
        for i, gp in enumerate(graph_paths):
            parts.append(f"  [{i+1}] {gp.get('chemin', '')}")
            parts.append(f"      Relations: {' -> '.join(gp.get('relations', []))}")
        parts.append("")

    merged = "\n".join(parts)

    debug_trace.append({
        "node_name": "node_merge_contexts",
        "status": "success",
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"vector={len(vector_results)}, graph={len(graph_paths)}",
        "output_summary": f"merged_len={len(merged)}",
    })

    timings = state.get("timings", {})
    timings["node_merge_contexts"] = time.time() - start

    return {
        "merged_context": merged,
        "debug_trace": debug_trace,
        "timings": timings,
    }
