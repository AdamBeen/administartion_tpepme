from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    question: str
    type_dossier: Optional[str] = "inconnu"
    identifiant_dossier: Optional[str] = ""


class HealthResponse(BaseModel):
    status: str
    astra_db: bool
    config_errors: list[str]
