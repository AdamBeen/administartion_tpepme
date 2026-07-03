import time
import logging
from graph.state import AdminTPEState

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = [".pdf", ".csv", ".xls", ".xlsx", ".txt", ".md"]


def node_validate_input_basic(state: AdminTPEState) -> dict:
    start = time.time()
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    question = state.get("question_administrateur", "").strip()
    files = state.get("uploaded_files", [])

    validation_errors = []
    if not question:
        validation_errors.append({
            "node_name": "node_validate_input_basic",
            "error_type": "missing_question",
            "message": "Aucune question fournie.",
            "user_explanation": "Vous devez poser une question pour lancer l'analyse.",
            "suggestion": "Saisissez une question dans la zone de texte.",
        })

    for f in files:
        filename = f.get("filename", "")
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext and ext not in SUPPORTED_FORMATS:
            validation_errors.append({
                "node_name": "node_validate_input_basic",
                "error_type": "unsupported_format",
                "message": f"Format non supporté: {ext} pour {filename}",
                "user_explanation": f"Le fichier {filename} a un format non supporté ({ext}).",
                "suggestion": f"Formats acceptés: {', '.join(SUPPORTED_FORMATS)}",
            })

    errors.extend(validation_errors)
    status = "warning" if validation_errors else "success"

    debug_trace.append({
        "node_name": "node_validate_input_basic",
        "status": status,
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"question_len={len(question)}, files={len(files)}",
        "output_summary": f"errors={len(validation_errors)}",
    })

    timings = state.get("timings", {})
    timings["node_validate_input_basic"] = time.time() - start

    return {
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
