from pydantic import BaseModel
from typing import Any, Optional


class CleanedResponse(BaseModel):
    run_id: str = ""
    resume_dossier: dict[str, Any] = {}
    type_demande: str = ""
    conditions_remplies: list[str] = []
    conditions_non_remplies: list[str] = []
    conditions_non_verifiables: list[str] = []
    risques: list[str] = []
    observations: list[str] = []
    resultats_rag_vectoriel: list[dict[str, Any]] = []
    resultats_graphrag: list[dict[str, Any]] = []
    recommandation: dict[str, Any] = {}
    hitl: dict[str, Any] = {}
    reponse_proposee: str = ""
    vulnerabilites_v1_connues: list[str] = []


class AnalyzeResponse(BaseModel):
    run_id: str
    status: str
    cleaned_response: dict[str, Any]
    final_json: dict[str, Any]
    debug_trace: list[dict[str, Any]] = []
    timings: dict[str, float] = {}
    errors: list[dict[str, Any]] = []
