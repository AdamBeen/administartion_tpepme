from db.astra_client import get_collection
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def store_chunk(chunk: dict) -> bool:
    try:
        col = get_collection("vector_chunks")
        chunk.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        col.replace_one({"chunk_id": chunk["chunk_id"]}, chunk, upsert=True)
        return True
    except Exception as e:
        logger.error("Failed to store chunk %s: %s", chunk.get("chunk_id"), e)
        return False


def get_all_chunks() -> list[dict]:
    try:
        col = get_collection("vector_chunks")
        return list(col.find({}))
    except Exception as e:
        logger.error("Failed to get all chunks: %s", e)
        return []


def search_chunks_by_embedding(embedding: list[float], top_k: int = 5) -> list[dict]:
    try:
        col = get_collection("vector_chunks")
        pipeline = [
            {"$sort": {"$vector": 1}},
            {"$limit": top_k},
        ]
        cursor = col.find({}, sort={"$vector": embedding}, limit=top_k)
        return list(cursor)
    except Exception as e:
        logger.error("Vector search failed: %s", e)
        return []


def search_chunks_by_keywords(keywords: list[str], top_k: int = 5) -> list[dict]:
    try:
        col = get_collection("vector_chunks")
        results = []
        all_chunks = list(col.find({}))
        for chunk in all_chunks:
            text = (chunk.get("chunk_text", "") + " " + chunk.get("section", "")).lower()
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                chunk["_score"] = score
                results.append(chunk)
        results.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return results[:top_k]
    except Exception as e:
        logger.error("Keyword search failed: %s", e)
        return []
