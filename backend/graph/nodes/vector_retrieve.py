import time
import logging
from graph.state import AdminTPEState
from db.vector_store import search_chunks_by_keywords, search_chunks_by_embedding

logger = logging.getLogger(__name__)


def node_vector_retrieve(state: AdminTPEState) -> dict:
    start = time.time()
    vector_query = state.get("vector_query", "")
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    keywords = vector_query.split()
    results = search_chunks_by_keywords(keywords, top_k=5)

    if not results:
        results = search_chunks_by_keywords(["administration", "TPE", "PME", "aide", "autorisation"], top_k=3)

    formatted = []
    for chunk in results:
        formatted.append({
            "source": chunk.get("source_name", ""),
            "section": chunk.get("section", ""),
            "chunk_id": chunk.get("chunk_id", ""),
            "extrait": chunk.get("chunk_text", "")[:500],
            "utilite": "Passage pertinent retrouvé par recherche par mots-clés.",
        })

    if not formatted:
        errors.append({
            "node_name": "node_vector_retrieve",
            "error_type": "no_results",
            "message": "Aucun chunk pertinent retrouvé.",
            "user_explanation": "Aucun chunk pertinent n'a été retrouvé dans le document de contexte.",
            "suggestion": "Vérifiez que le document administratif a été indexé.",
        })

    status = "warning" if not formatted else "success"
    debug_trace.append({
        "node_name": "node_vector_retrieve",
        "status": status,
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"query={vector_query[:80]}",
        "output_summary": f"results={len(formatted)}",
    })

    timings = state.get("timings", {})
    timings["node_vector_retrieve"] = time.time() - start

    return {
        "vector_results": formatted,
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
