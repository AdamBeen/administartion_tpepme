import uuid
import time
import logging
from graph.state import AdminTPEState

logger = logging.getLogger(__name__)


def node_receive_input(state: AdminTPEState) -> dict:
    start = time.time()
    run_id = str(uuid.uuid4())
    logger.info("[node_receive_input] run_id=%s", run_id)

    trace_entry = {
        "node_name": "node_receive_input",
        "status": "success",
        "duration_ms": 0,
        "input_summary": f"question={state.get('question_administrateur', '')[:100]}",
        "output_summary": f"run_id={run_id}",
    }

    timings = state.get("timings", {})
    timings["node_receive_input"] = time.time() - start
    trace_entry["duration_ms"] = int(timings["node_receive_input"] * 1000)

    debug_trace = state.get("debug_trace", [])
    debug_trace.append(trace_entry)

    return {
        "run_id": run_id,
        "debug_trace": debug_trace,
        "timings": timings,
        "errors": [],
    }
