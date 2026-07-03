import time
import json
import logging
from graph.state import AdminTPEState
from graph.prompts import PROMPT_EXTRACTION_DOSSIER
from llm.groq_client import chat_short_json

logger = logging.getLogger(__name__)


def node_build_temporary_dossier_summary(state: AdminTPEState) -> dict:
    start = time.time()
    extracted_texts = state.get("extracted_texts", {})
    question = state.get("question_administrateur", "")
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    combined_text = ""
    for filename, text in extracted_texts.items():
        combined_text += f"\n\n--- {filename} ---\n{text}"

    if not combined_text.strip():
        combined_text = "Aucun fichier fourni. Question uniquement."

    user_prompt = f"Question de l'administrateur: {question}\n\nTextes extraits des fichiers:\n{combined_text[:30000]}"

    try:
        dossier = chat_short_json(PROMPT_EXTRACTION_DOSSIER, user_prompt, temperature=0.3, max_tokens=4096)
        logger.info("[node_build_temporary_dossier_summary] Dossier summary created")
    except Exception as e:
        errors.append({
            "node_name": "node_build_temporary_dossier_summary",
            "error_type": "llm_error",
            "message": str(e),
            "user_explanation": "Le modèle n'a pas pu produire un résumé du dossier.",
            "suggestion": "Vérifiez la clé API Google et la connectivité.",
        })
        dossier = {
            "entreprise": "",
            "profil": "",
            "activite": "",
            "objet_demande": "",
            "documents_analyses": list(extracted_texts.keys()),
            "pieces_detectees": [],
            "pieces_manquantes_probables": [],
            "incoherences_detectees": [],
            "dates_importantes": [],
            "observations": "Erreur lors de l'extraction.",
        }

    status = "error" if any(e.get("node_name") == "node_build_temporary_dossier_summary" for e in errors) else "success"
    debug_trace.append({
        "node_name": "node_build_temporary_dossier_summary",
        "status": status,
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"files={len(extracted_texts)}, text_len={len(combined_text)}",
        "output_summary": f"entreprise={dossier.get('entreprise', '')}",
    })

    timings = state.get("timings", {})
    timings["node_build_temporary_dossier_summary"] = time.time() - start

    return {
        "dossier_temporaire": dossier,
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
