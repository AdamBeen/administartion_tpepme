import time
import json
import logging
from datetime import datetime, timezone
from graph.state import AdminTPEState
from db.astra_client import get_collection
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
        runs_col = get_collection("workflow_runs")
        runs_col.replace_one(
            {"run_id": run_id},
            {
                "run_id": run_id,
                "question": state.get("question_administrateur", ""),
                "status": "completed" if not errors else "completed_with_errors",
                "type_demande": parsed.get("type_demande", "inconnu"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "total_duration_ms": total_duration_ms,
                "final_json": json.dumps(parsed, ensure_ascii=False),
                "cleaned_response": json.dumps(cleaned, ensure_ascii=False),
            },
            upsert=True,
        )
    except Exception as e:
        logger.error("[node_persist_run_logs] Failed to save run: %s", e)

    if errors:
        try:
            error_docs = [
                {
                    "run_id": run_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "node_name": err.get("node_name", "unknown"),
                    "error_type": err.get("error_type", "unknown"),
                    "error_message": err.get("message", ""),
                    "stack_trace": "",
                    "user_explanation": err.get("user_explanation", ""),
                    "suggestion": err.get("suggestion", ""),
                }
                for err in errors
            ]
            errors_col = get_collection("workflow_errors")
            errors_col.insert_many(error_docs)
        except Exception as e:
            logger.error("[node_persist_run_logs] Failed to save errors: %s", e)

    if debug_trace:
        try:
            trace_docs = [
                {
                    "run_id": run_id,
                    "step_index": i,
                    "node_name": trace.get("node_name", ""),
                    "input_summary": trace.get("input_summary", ""),
                    "output_summary": trace.get("output_summary", ""),
                    "duration_ms": trace.get("duration_ms", 0),
                    "status": trace.get("status", "success"),
                }
                for i, trace in enumerate(debug_trace)
            ]
            traces_col = get_collection("workflow_traces")
            traces_col.insert_many(trace_docs)
        except Exception as e:
            logger.error("[node_persist_run_logs] Failed to save traces: %s", e)

    if graph_paths:
        try:
            path_docs = [
                {
                    "run_id": run_id,
                    "path_id": f"{run_id}_{i}",
                    "path_text": gp.get("chemin", ""),
                    "nodes": gp.get("noeuds", []),
                    "relations": gp.get("relations", []),
                    "interpretation": gp.get("interpretation", ""),
                }
                for i, gp in enumerate(graph_paths)
            ]
            paths_col = get_collection("graphrag_paths")
            paths_col.insert_many(path_docs)
        except Exception as e:
            logger.error("[node_persist_run_logs] Failed to save graphrag paths: %s", e)

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
