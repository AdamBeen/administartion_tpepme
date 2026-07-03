import time
import json
import logging
from graph.state import AdminTPEState
from graph.prompts import PROMPT_CLASSIFICATION
from llm.groq_client import chat_short_json

logger = logging.getLogger(__name__)


def node_classify_admin_request(state: AdminTPEState) -> dict:
    start = time.time()
    question = state.get("question_administrateur", "")
    dossier = state.get("dossier_temporaire", {})
    type_optionnel = state.get("type_dossier_optionnel", "")
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    if type_optionnel and type_optionnel != "inconnu":
        classification = type_optionnel
        logger.info("[node_classify_admin_request] Using provided type: %s", classification)
    else:
        user_prompt = f"Question: {question}\nRésumé dossier: {json.dumps(dossier, ensure_ascii=False)[:3000]}"
        try:
            result = chat_short_json(PROMPT_CLASSIFICATION, user_prompt)
            classification = result.get("classification", "inconnu")
        except Exception as e:
            errors.append({
                "node_name": "node_classify_admin_request",
                "error_type": "llm_error",
                "message": str(e),
                "user_explanation": "La classification automatique a échoué.",
                "suggestion": "Vérifiez la clé API Groq.",
            })
            classification = "inconnu"

    valid_types = ["aide", "autorisation", "recours", "mixte", "inconnu"]
    if classification not in valid_types:
        classification = "inconnu"

    status = "warning" if classification == "inconnu" else "success"
    debug_trace.append({
        "node_name": "node_classify_admin_request",
        "status": status,
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"question_len={len(question)}",
        "output_summary": f"classification={classification}",
    })

    timings = state.get("timings", {})
    timings["node_classify_admin_request"] = time.time() - start

    return {
        "classification_demande": classification,
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
