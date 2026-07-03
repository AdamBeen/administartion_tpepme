import time
import json
import logging
import re
from graph.state import AdminTPEState

logger = logging.getLogger(__name__)

_STOP_WORDS = {
    "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "mais",
    "est", "sont", "dans", "pour", "par", "sur", "avec", "sans", "que", "qui",
    "ce", "cette", "ces", "quel", "quelle", "quelles", "à", "au", "aux",
    "il", "elle", "ils", "elles", "on", "nous", "vous", "je", "tu",
    "ne", "pas", "plus", "tout", "tous", "toute", "toutes",
    "se", "ses", "son", "sa", "leur", "leurs", "notre", "votre",
    "comment", "pourquoi", "quand", "où",
}


def _extract_keywords(text: str, max_kw: int = 10) -> list[str]:
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


def node_build_graph_query(state: AdminTPEState) -> dict:
    start = time.time()
    question = state.get("question_administrateur", "")
    classification = state.get("classification_demande", "inconnu")
    dossier = state.get("dossier_temporaire", {})
    debug_trace = state.get("debug_trace", [])

    dossier_text = question
    if isinstance(dossier, dict):
        dossier_text += " " + " ".join(str(v) for v in dossier.values() if isinstance(v, (str, list)))

    keywords = _extract_keywords(dossier_text, max_kw=8)

    type_map = {"aide": "Aide", "autorisation": "Autorisation", "recours": "Recours", "mixte": "", "inconnu": ""}
    type_kw = type_map.get(classification, "")
    if type_kw and type_kw.lower() not in keywords:
        keywords.insert(0, type_kw.lower())

    base_kw = ["aide", "autorisation", "recours", "condition", "piece", "eligibilite"]
    for bk in base_kw:
        if bk not in keywords and len(keywords) < 10:
            keywords.append(bk)

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
        "debug_trace": debug_trace,
        "timings": timings,
    }
