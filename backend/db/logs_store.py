from db.astra_client import get_collection
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def save_run(run: dict) -> bool:
    try:
        col = get_collection("workflow_runs")
        run.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        col.replace_one({"run_id": run["run_id"]}, run, upsert=True)
        return True
    except Exception as e:
        logger.error("Failed to save run %s: %s", run.get("run_id"), e)
        return False


def get_run(run_id: str) -> dict | None:
    try:
        col = get_collection("workflow_runs")
        return col.find_one({"run_id": run_id})
    except Exception as e:
        logger.error("Failed to get run %s: %s", run_id, e)
        return None


def list_runs(limit: int = 50) -> list[dict]:
    try:
        col = get_collection("workflow_runs")
        return list(col.find({}, limit=limit))
    except Exception as e:
        logger.error("Failed to list runs: %s", e)
        return []


def save_error(error: dict) -> bool:
    try:
        col = get_collection("workflow_errors")
        col.insert_one(error)
        return True
    except Exception as e:
        logger.error("Failed to save error: %s", e)
        return False


def get_errors(run_id: str) -> list[dict]:
    try:
        col = get_collection("workflow_errors")
        return list(col.find({"run_id": run_id}))
    except Exception as e:
        logger.error("Failed to get errors for run %s: %s", run_id, e)
        return []


def save_trace(trace: dict) -> bool:
    try:
        col = get_collection("workflow_traces")
        col.insert_one(trace)
        return True
    except Exception as e:
        logger.error("Failed to save trace: %s", e)
        return False


def get_traces(run_id: str) -> list[dict]:
    try:
        col = get_collection("workflow_traces")
        return list(col.find({"run_id": run_id}))
    except Exception as e:
        logger.error("Failed to get traces for run %s: %s", run_id, e)
        return []


def save_graphrag_path(path: dict) -> bool:
    try:
        col = get_collection("graphrag_paths")
        col.insert_one(path)
        return True
    except Exception as e:
        logger.error("Failed to save graphrag path: %s", e)
        return False
