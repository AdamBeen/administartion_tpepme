import time
import logging
from graph.state import AdminTPEState

logger = logging.getLogger(__name__)


def node_error_handler(state: AdminTPEState) -> dict:
    start = time.time()
    errors = state.get("errors", [])
    run_id = state.get("run_id", "")
    debug_trace = state.get("debug_trace", [])

    last_error = errors[-1] if errors else {
        "node_name": "unknown",
        "error_type": "unknown",
        "message": "Erreur inconnue.",
        "user_explanation": "Une erreur inconnue est survenue.",
        "suggestion": "Contactez le support technique.",
    }

    error_response = {
        "run_id": run_id,
        "status": "error",
        "node_en_erreur": last_error.get("node_name", "unknown"),
        "type_erreur": last_error.get("error_type", "unknown"),
        "message_technique": last_error.get("message", ""),
        "explication_lisible": last_error.get("user_explanation", ""),
        "suggestion_correction": last_error.get("suggestion", ""),
        "total_errors": len(errors),
        "all_errors": errors,
    }

    debug_trace.append({
        "node_name": "node_error_handler",
        "status": "error",
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"errors={len(errors)}",
        "output_summary": f"error_node={last_error.get('node_name', '')}",
    })

    timings = state.get("timings", {})
    timings["node_error_handler"] = time.time() - start

    return {
        "cleaned_response": error_response,
        "final_json": error_response,
        "debug_trace": debug_trace,
        "timings": timings,
    }
