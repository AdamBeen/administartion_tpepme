from typing import TypedDict, Any
from langgraph.graph import MessagesState


class AdminTPEState(TypedDict, total=False):
    run_id: str
    question_administrateur: str
    uploaded_files: list[dict[str, Any]]
    extracted_texts: dict[str, str]
    dossier_temporaire: dict[str, Any]
    classification_demande: str
    type_dossier_optionnel: str
    identifiant_dossier: str
    vector_query: str
    vector_results: list[dict[str, Any]]
    graph_query: str
    graph_paths: list[dict[str, Any]]
    merged_context: str
    raw_llm_output: str
    parsed_json: dict[str, Any]
    hitl_result: dict[str, Any]
    cleaned_response: dict[str, Any]
    errors: list[dict[str, Any]]
    debug_trace: list[dict[str, Any]]
    timings: dict[str, float]
    final_json: dict[str, Any]
