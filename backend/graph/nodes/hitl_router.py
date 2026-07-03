import time
import logging
from graph.state import AdminTPEState

logger = logging.getLogger(__name__)


def node_hitl_router(state: AdminTPEState) -> dict:
    start = time.time()
    parsed = state.get("parsed_json", {})
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    recommendation = parsed.get("recommandation", {})
    hitl = parsed.get("hitl", {})
    dossier = parsed.get("resume_dossier_temporaire", {})
    analyse = parsed.get("analyse_administrative", {})
    type_demande = parsed.get("type_demande", "inconnu")

    pieces_manquantes = dossier.get("pieces_manquantes", [])
    incoherences = dossier.get("incoherences_detectees", [])
    risques = analyse.get("risques", [])
    decision = recommendation.get("decision_proposee", "")
    confiance = recommendation.get("niveau_confiance", 0.0)

    niveau = "VERT"
    raisons = []

    if pieces_manquantes:
        niveau = "ORANGE"
        raisons.append("Pièces manquantes détectées")
    if incoherences:
        niveau = "ORANGE"
        raisons.append("Incohérences documentaires détectées")
    if type_demande == "recours":
        niveau = "ORANGE"
        raisons.append("Type de demande: recours")
    if any("fraude" in r.lower() for r in risques):
        niveau = "ROUGE"
        raisons.append("Suspicion de fraude")
    if decision == "rejet_potentiel":
        niveau = "ROUGE"
        raisons.append("Décision proposée: rejet potentiel")
    if confiance < 0.65 and niveau != "ROUGE":
        niveau = "ORANGE"
        raisons.append(f"Confiance faible: {confiance}")
    if confiance < 0.45:
        niveau = "ROUGE"
        raisons.append(f"Confiance très faible: {confiance}")

    hitl_result = {
        "requis": niveau != "VERT",
        "niveau": niveau,
        "raison": "; ".join(raisons) if raisons else "Dossier simple, aucune escalade nécessaire.",
        "validateur_recommande": "Aucun" if niveau == "VERT" else ("Agent senior" if niveau == "ORANGE" else "Responsable de service"),
    }

    parsed["hitl"] = hitl_result

    debug_trace.append({
        "node_name": "node_hitl_router",
        "status": "success",
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"confiance={confiance}, type={type_demande}",
        "output_summary": f"niveau={niveau}, requis={hitl_result['requis']}",
    })

    timings = state.get("timings", {})
    timings["node_hitl_router"] = time.time() - start

    return {
        "parsed_json": parsed,
        "hitl_result": hitl_result,
        "debug_trace": debug_trace,
        "timings": timings,
    }
