import time
import json
import logging
from datetime import datetime, timezone
from graph.state import AdminTPEState
from db.logs_store import save_run, save_error, save_trace, save_graphrag_path
from config import settings

logger = logging.getLogger(__name__)


def node_persist_run_logs(state: AdminTPEState) -> dict:
    start = time.time()
    run_id = state.get("run_id", "")
    parsed = state.get("parsed_json", {})
    cleaned = state.get("cleaned_response", {})
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])
    timings = state.get("timings", {})
    graph_paths = state.get("graph_paths", [])

    total_duration_ms = int(sum(timings.values()) * 1000)

    try:
        save_run({
            "run_id": run_id,
            "question": state.get("question_administrateur", ""),
            "status": "completed" if not errors else "completed_with_errors",
            "type_demande": parsed.get("type_demande", "inconnu"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "total_duration_ms": total_duration_ms,
            "final_json": json.dumps(parsed, ensure_ascii=False),
            "cleaned_response": json.dumps(cleaned, ensure_ascii=False),
        })
    except Exception as e:
        logger.error("[node_persist_run_logs] Failed to save run: %s", e)

    for err in errors:
        try:
            save_error({
                "run_id": run_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "node_name": err.get("node_name", "unknown"),
                "error_type": err.get("error_type", "unknown"),
                "error_message": err.get("message", ""),
                "stack_trace": "",
                "user_explanation": err.get("user_explanation", ""),
                "suggestion": err.get("suggestion", ""),
            })
        except Exception as e:
            logger.error("[node_persist_run_logs] Failed to save error: %s", e)

    for i, trace in enumerate(debug_trace):
        try:
            save_trace({
                "run_id": run_id,
                "step_index": i,
                "node_name": trace.get("node_name", ""),
                "input_summary": trace.get("input_summary", ""),
                "output_summary": trace.get("output_summary", ""),
                "duration_ms": trace.get("duration_ms", 0),
                "status": trace.get("status", "success"),
            })
        except Exception as e:
            logger.error("[node_persist_run_logs] Failed to save trace: %s", e)

    for i, gp in enumerate(graph_paths):
        try:
            save_graphrag_path({
                "run_id": run_id,
                "path_id": f"{run_id}_{i}",
                "path_text": gp.get("chemin", ""),
                "nodes": gp.get("noeuds", []),
                "relations": gp.get("relations", []),
                "interpretation": gp.get("interpretation", ""),
            })
        except Exception as e:
            logger.error("[node_persist_run_logs] Failed to save graphrag path: %s", e)

    debug_trace.append({
        "node_name": "node_persist_run_logs",
        "status": "success",
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"errors={len(errors)}, traces={len(debug_trace)}",
        "output_summary": "persisted",
    })

    timings["node_persist_run_logs"] = time.time() - start

    return {
        "debug_trace": debug_trace,
        "timings": timings,
    }
