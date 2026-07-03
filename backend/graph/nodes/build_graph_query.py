import time
import json
import logging
from graph.state import AdminTPEState
from graph.prompts import PROMPT_BUILD_GRAPH_QUERY
from llm.groq_client import chat_short_json

logger = logging.getLogger(__name__)


def node_build_graph_query(state: AdminTPEState) -> dict:
    start = time.time()
    question = state.get("question_administrateur", "")
    classification = state.get("classification_demande", "inconnu")
    dossier = state.get("dossier_temporaire", {})
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    user_prompt = f"Question: {question}\nClassification: {classification}\nRésumé dossier: {json.dumps(dossier, ensure_ascii=False)[:2000]}"

    try:
        result = chat_short_json(PROMPT_BUILD_GRAPH_QUERY, user_prompt, temperature=0.2)
        keywords = result.get("keywords", [])
    except Exception as e:
        errors.append({
            "node_name": "node_build_graph_query",
            "error_type": "llm_error",
            "message": str(e),
            "user_explanation": "La construction de la requête GraphRAG a échoué.",
            "suggestion": "Vérifiez la clé API Groq.",
        })
        keywords = [classification, "aide", "autorisation", "recours", "piece", "condition"]

    if not keywords:
        keywords = [classification, "aide", "autorisation", "recours"]

    debug_trace.append({
        "node_name": "node_build_graph_query",
        "status": "success",
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"classification={classification}",
        "output_summary": f"keywords={keywords[:5]}",
    })

    timings = state.get("timings", {})
    timings["node_build_graph_query"] = time.time() - start

    return {
        "graph_query": json.dumps(keywords),
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
