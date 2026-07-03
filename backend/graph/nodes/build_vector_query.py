import time
import logging
from graph.state import AdminTPEState
from graph.prompts import PROMPT_BUILD_VECTOR_QUERY
from llm.groq_client import chat_short

logger = logging.getLogger(__name__)


def node_build_vector_query(state: AdminTPEState) -> dict:
    start = time.time()
    question = state.get("question_administrateur", "")
    dossier = state.get("dossier_temporaire", {})
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    import json
    user_prompt = f"Question: {question}\nRésumé dossier: {json.dumps(dossier, ensure_ascii=False)[:2000]}"

    try:
        vector_query = chat_short(PROMPT_BUILD_VECTOR_QUERY, user_prompt, temperature=0.2, max_tokens=100)
        vector_query = vector_query.strip().strip('"').strip("'")
    except Exception as e:
        errors.append({
            "node_name": "node_build_vector_query",
            "error_type": "llm_error",
            "message": str(e),
            "user_explanation": "La construction de la requête vectorielle a échoué.",
            "suggestion": "Vérifiez la clé API Groq.",
        })
        vector_query = question[:200]

    debug_trace.append({
        "node_name": "node_build_vector_query",
        "status": "success",
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"question_len={len(question)}",
        "output_summary": f"query={vector_query[:80]}",
    })

    timings = state.get("timings", {})
    timings["node_build_vector_query"] = time.time() - start

    return {
        "vector_query": vector_query,
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
