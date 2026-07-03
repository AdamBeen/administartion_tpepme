import time
import logging
from graph.state import AdminTPEState

logger = logging.getLogger(__name__)


def node_clean_response_for_frontend(state: AdminTPEState) -> dict:
    start = time.time()
    parsed = state.get("parsed_json", {})
    hitl = state.get("hitl_result", parsed.get("hitl", {}))
    debug_trace = state.get("debug_trace", [])

    dossier = parsed.get("resume_dossier_temporaire", {})
    analyse = parsed.get("analyse_administrative", {})
    recommandation = parsed.get("recommandation", {})
    rag_results = parsed.get("resultats_rag_vectoriel", [])
    graphrag_results = parsed.get("resultats_graphrag", [])

    cleaned = {
        "run_id": parsed.get("run_id", state.get("run_id", "")),
        "resume_dossier": {
            "entreprise": dossier.get("entreprise", ""),
            "profil": dossier.get("profil", ""),
            "activite": dossier.get("activite", ""),
            "objet_demande": dossier.get("objet_demande", ""),
            "documents_analyses": dossier.get("documents_analyses", []),
            "pieces_detectees": dossier.get("pieces_detectees", []),
            "pieces_manquantes": dossier.get("pieces_manquantes", []),
            "incoherences_detectees": dossier.get("incoherences_detectees", []),
        },
        "type_demande": parsed.get("type_demande", "inconnu"),
        "conditions_remplies": analyse.get("conditions_remplies", []),
        "conditions_non_remplies": analyse.get("conditions_non_remplies", []),
        "conditions_non_verifiables": analyse.get("conditions_non_verifiables", []),
        "risques": analyse.get("risques", []),
        "observations": analyse.get("observations", []),
        "resultats_rag_vectoriel": rag_results,
        "resultats_graphrag": graphrag_results,
        "recommandation": recommandation,
        "hitl": hitl,
        "reponse_proposee": parsed.get("reponse_proposee_a_l_administrateur", ""),
        "vulnerabilites_v1_connues": parsed.get("vulnerabilites_v1_connues", []),
    }

    debug_trace.append({
        "node_name": "node_clean_response_for_frontend",
        "status": "success",
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"parsed_keys={len(parsed)}",
        "output_summary": f"cleaned_keys={len(cleaned)}",
    })

    timings = state.get("timings", {})
    timings["node_clean_response_for_frontend"] = time.time() - start

    return {
        "cleaned_response": cleaned,
        "final_json": parsed,
        "debug_trace": debug_trace,
        "timings": timings,
    }
