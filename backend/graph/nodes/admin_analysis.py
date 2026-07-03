import time
import json
import logging
from graph.state import AdminTPEState
from graph.prompts import PROMPT_ANALYSE_FINALE
from llm.gemini_client import chat_long
from config import settings

logger = logging.getLogger(__name__)


def node_administrative_analysis_llm(state: AdminTPEState) -> dict:
    start = time.time()
    merged_context = state.get("merged_context", "")
    run_id = state.get("run_id", "")
    question = state.get("question_administrateur", "")
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    prompt_with_context = f"{PROMPT_ANALYSE_FINALE}\n\nCONTEXTE FUSIONNÉ:\n{merged_context}\n\nrun_id: {run_id}\nquestion_administrateur: {question}"

    try:
        raw_output = chat_long(
            "Tu es un copilote interne d'instruction administrative TPE/PME au Maroc.",
            prompt_with_context,
            temperature=0.4,
            max_tokens=8192,
        )
        logger.info("[node_administrative_analysis_llm] LLM output received, len=%d", len(raw_output))
    except Exception as e:
        errors.append({
            "node_name": "node_administrative_analysis_llm",
            "error_type": "llm_error",
            "message": str(e),
            "user_explanation": "Le modèle d'analyse administrative n'a pas répondu.",
            "suggestion": "Vérifiez la clé API Google et la connectivité.",
        })
        raw_output = "{}"

    debug_trace.append({
        "node_name": "node_administrative_analysis_llm",
        "status": "success" if raw_output != "{}" else "error",
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"merged_len={len(merged_context)}",
        "output_summary": f"output_len={len(raw_output)}",
    })

    timings = state.get("timings", {})
    timings["node_administrative_analysis_llm"] = time.time() - start

    return {
        "raw_llm_output": raw_output,
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
