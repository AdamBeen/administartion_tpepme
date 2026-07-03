import time
import json
import logging
from graph.state import AdminTPEState
from graph.prompts import PROMPT_REPARATION_JSON
from llm.groq_client import chat_short
from config import settings

logger = logging.getLogger(__name__)


def _try_parse(text: str) -> dict | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        return None


def node_parse_and_validate_json(state: AdminTPEState) -> dict:
    start = time.time()
    raw_output = state.get("raw_llm_output", "")
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    parsed = _try_parse(raw_output)

    if parsed is None:
        logger.info("[node_parse_and_validate_json] JSON invalid, attempting repair...")
        try:
            repaired = chat_short(PROMPT_REPARATION_JSON, raw_output, temperature=0.1, json_mode=True)
            parsed = _try_parse(repaired)
        except Exception as e:
            logger.error("[node_parse_and_validate_json] Repair failed: %s", e)

    if parsed is None:
        errors.append({
            "node_name": "node_parse_and_validate_json",
            "error_type": "json_invalid",
            "message": "JSON invalide non réparable.",
            "user_explanation": "Le modèle a produit une réponse qui n'est pas un JSON valide. Une tentative de réparation a échoué.",
            "suggestion": "Réessayez avec une question plus simple ou vérifiez les limites de tokens.",
        })
        parsed = {
            "workflow_version": settings.WORKFLOW_VERSION,
            "run_id": state.get("run_id", ""),
            "question_administrateur": state.get("question_administrateur", ""),
            "type_demande": state.get("classification_demande", "inconnu"),
            "resume_dossier_temporaire": state.get("dossier_temporaire", {}),
            "analyse_administrative": {
                "conditions_remplies": [],
                "conditions_non_remplies": [],
                "conditions_non_verifiables": [],
                "risques": [],
                "observations": ["Erreur: JSON invalide non réparable."],
            },
            "resultats_rag_vectoriel": state.get("vector_results", []),
            "resultats_graphrag": state.get("graph_paths", []),
            "recommandation": {
                "decision_proposee": "analyse_impossible",
                "niveau_confiance": 0.0,
                "justification": "JSON invalide non réparable.",
            },
            "hitl": {
                "requis": True,
                "niveau": "ROUGE",
                "raison": "Erreur de parsing JSON.",
                "validateur_recommande": "Agent senior",
            },
            "reponse_proposee_a_l_administrateur": "Une erreur technique est survenue lors de l'analyse. Veuillez réessayer ou contacter le support.",
            "vulnerabilites_v1_connues": [
                "Aucune protection contre la prompt injection documentaire.",
                "Risque de JSON invalide en cas d'entrée hostile.",
            ],
        }
        status = "error"
    else:
        parsed.setdefault("workflow_version", settings.WORKFLOW_VERSION)
        parsed.setdefault("run_id", state.get("run_id", ""))
        parsed.setdefault("question_administrateur", state.get("question_administrateur", ""))
        parsed.setdefault("type_demande", state.get("classification_demande", "inconnu"))
        parsed.setdefault("resume_dossier_temporaire", state.get("dossier_temporaire", {}))
        parsed.setdefault("resultats_rag_vectoriel", state.get("vector_results", []))
        parsed.setdefault("resultats_graphrag", state.get("graph_paths", []))
        parsed.setdefault("vulnerabilites_v1_connues", [
            "Aucune protection contre la prompt injection documentaire.",
            "Aucune séparation stricte entre données et instructions.",
            "Aucune anonymisation automatique des données personnelles.",
            "Aucun contrôle d'accès avancé.",
            "Aucun filtrage des contenus malveillants dans les fichiers uploadés.",
            "Aucune vérification d'intégrité des documents.",
            "Aucun scoring de confiance des sources.",
            "Aucun module de détection d'exfiltration.",
            "Aucun blocage des demandes suspectes.",
            "Risque de JSON invalide en cas d'entrée hostile.",
        ])
        status = "success"

    debug_trace.append({
        "node_name": "node_parse_and_validate_json",
        "status": status,
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"raw_len={len(raw_output)}",
        "output_summary": f"parsed_keys={len(parsed)}",
    })

    timings = state.get("timings", {})
    timings["node_parse_and_validate_json"] = time.time() - start

    return {
        "parsed_json": parsed,
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
