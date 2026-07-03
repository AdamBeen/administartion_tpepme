import time
import logging
import re
from graph.state import AdminTPEState

logger = logging.getLogger(__name__)

_STOP_WORDS = {
    "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "mais",
    "est", "sont", "dans", "pour", "par", "sur", "avec", "sans", "que", "qui",
    "ce", "cette", "ces", "quel", "quelle", "quelles", "à", "au", "aux",
    "il", "elle", "ils", "elles", "on", "nous", "vous", "je", "tu",
    "ne", "pas", "plus", "tres", "tres", "tout", "tous", "toute", "toutes",
    "se", "ses", "son", "sa", "leur", "leurs", "notre", "votre",
    "comment", "pourquoi", "quand", "où", "quel", "quelle",
}


def _extract_keywords(text: str, max_kw: int = 8) -> list[str]:
    words = re.findall(r"[a-zA-ZàâäéèêëïîôöùûüçÀÂÄÉÈÊËÏÎÔÖÙÛÜÇ]{3,}", text.lower())
    keywords = [w for w in words if w not in _STOP_WORDS]
    seen = set()
    result = []
    for w in keywords:
        if w not in seen:
            seen.add(w)
            result.append(w)
        if len(result) >= max_kw:
            break
    return result


def node_build_vector_query(state: AdminTPEState) -> dict:
    start = time.time()
    question = state.get("question_administrateur", "")
    dossier = state.get("dossier_temporaire", {})
    debug_trace = state.get("debug_trace", [])

    dossier_text = question
    if isinstance(dossier, dict):
        dossier_text += " " + " ".join(str(v) for v in dossier.values() if isinstance(v, (str, list)))

    keywords = _extract_keywords(dossier_text, max_kw=6)
    vector_query = " ".join(keywords)

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
        "debug_trace": debug_trace,
        "timings": timings,
    }
