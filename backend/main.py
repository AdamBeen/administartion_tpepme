import os
import sys
import json
import logging
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from graph.workflow import get_workflow
from db.astra_client import healthcheck as astra_healthcheck
from db.logs_store import get_run, list_runs, get_errors, get_traces
from db.kg_store import get_all_nodes, get_all_edges
from ingestion.export_obsidian import export_obsidian
from models.input import HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AdminTPE GraphRAG V1", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/api/health")
async def health():
    astra_ok = astra_healthcheck()
    config_errors = settings.validate()
    return HealthResponse(
        status="ok" if astra_ok and not config_errors else "degraded",
        astra_db=astra_ok,
        config_errors=config_errors,
    )


@app.post("/api/analyze")
async def analyze(
    question: str = Form(...),
    type_dossier: str = Form("inconnu"),
    identifiant_dossier: str = Form(""),
    files: list[UploadFile] = File(default=[]),
):
    start_total = time.time()
    logger.info("[/api/analyze] question=%s..., files=%d", question[:50], len(files))

    uploaded_files = []
    for f in files:
        content = await f.read()
        if len(content) > settings.max_file_size_bytes:
            logger.warning("File %s exceeds max size, skipping", f.filename)
            continue
        uploaded_files.append({
            "filename": f.filename,
            "content": content,
            "size": len(content),
        })

    initial_state = {
        "question_administrateur": question,
        "uploaded_files": uploaded_files,
        "type_dossier_optionnel": type_dossier,
        "identifiant_dossier": identifiant_dossier,
        "errors": [],
        "debug_trace": [],
        "timings": {},
    }

    try:
        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)

        total_ms = int((time.time() - start_total) * 1000)
        logger.info("[/api/analyze] completed in %dms, run_id=%s", total_ms, final_state.get("run_id", ""))

        return JSONResponse({
            "run_id": final_state.get("run_id", ""),
            "status": "error" if final_state.get("errors") and not final_state.get("final_json") else "completed",
            "cleaned_response": final_state.get("cleaned_response", {}),
            "final_json": final_state.get("final_json", {}),
            "debug_trace": final_state.get("debug_trace", []),
            "timings": final_state.get("timings", {}),
            "errors": final_state.get("errors", []),
            "total_duration_ms": total_ms,
        })
    except Exception as e:
        logger.error("[/api/analyze] Workflow error: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "run_id": "",
                "status": "error",
                "cleaned_response": {},
                "final_json": {},
                "debug_trace": [],
                "timings": {},
                "errors": [{
                    "node_name": "api",
                    "error_type": "workflow_exception",
                    "message": str(e),
                    "user_explanation": "Une erreur inattendue est survenue lors de l'exécution du workflow.",
                    "suggestion": "Vérifiez les logs serveur et la configuration.",
                }],
                "total_duration_ms": int((time.time() - start_total) * 1000),
            },
        )


@app.get("/api/run/{run_id}")
async def get_run_endpoint(run_id: str):
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    errors = get_errors(run_id)
    traces = get_traces(run_id)
    return {
        "run": run,
        "errors": errors,
        "traces": traces,
    }


@app.get("/api/runs")
async def list_runs_endpoint(limit: int = 50):
    runs = list_runs(limit=limit)
    return {"runs": runs}


@app.get("/api/kg/nodes")
async def kg_nodes():
    nodes = get_all_nodes()
    return {"count": len(nodes), "nodes": nodes}


@app.get("/api/kg/edges")
async def kg_edges():
    edges = get_all_edges()
    return {"count": len(edges), "edges": edges}


@app.post("/api/kg/export-obsidian")
async def export_obsidian_endpoint():
    try:
        export_obsidian()
        return {"status": "success", "message": "Obsidian vault exported."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.isfile(index_path):
        from fastapi.responses import FileResponse
        return FileResponse(index_path)
    return {"message": "AdminTPE GraphRAG V1 API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )
