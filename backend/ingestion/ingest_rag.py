import os
import sys
import re
import hashlib
import logging
import io
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.astra_client import get_collection
from db.schema import init_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

RAG_SOURCES = [
    {
        "path": os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "contexte_rag_vectoriel",
            "corpus_rag_vectoriel_administration_maroc_tpe_pme_2026.pdf",
        ),
        "source_name": "corpus_rag_vectoriel_administration_maroc_tpe_pme_2026.pdf",
        "document_id": "corpus_rag_vectoriel_2026",
    },
]


def _extract_pdf(path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        text += "\n"
    return text.strip()


def chunk_text(text: str, source_name: str, document_id: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    full_text = text
    start = 0
    chunk_idx = 0
    chunks = []

    while start < len(full_text):
        end = min(start + chunk_size, len(full_text))
        ct = full_text[start:end]

        section = "General"
        for marker in re.finditer(r"^#{1,3} (.+)$", ct, re.MULTILINE):
            section = marker.group(1).strip()

        chunk_id = hashlib.md5(f"{document_id}_{chunk_idx}".encode()).hexdigest()[:16]
        chunks.append({
            "chunk_id": chunk_id,
            "document_id": document_id,
            "source_name": source_name,
            "section": section,
            "chunk_text": ct,
            "metadata": {
                "version_document": "v1",
                "date_ingestion": datetime.now(timezone.utc).isoformat(),
                "chunk_index": str(chunk_idx),
                "source_type": "pdf",
                "source_path": source_name,
            },
        })
        start += chunk_size - overlap
        chunk_idx += 1

    return chunks


def ingest_rag():
    init_schema()

    all_chunks = []
    for src in RAG_SOURCES:
        path = src["path"]
        if not os.path.isfile(path):
            logger.error("RAG source not found: %s", path)
            continue

        logger.info("Extracting text from %s...", src["source_name"])
        text = _extract_pdf(path)
        logger.info("Extracted %d characters from %s", len(text), src["source_name"])

        chunks = chunk_text(text, src["source_name"], src["document_id"])
        logger.info("Created %d chunks from %s", len(chunks), src["source_name"])
        all_chunks.extend(chunks)

    if not all_chunks:
        logger.error("No chunks to ingest. Check RAG_SOURCES paths.")
        return

    logger.info("Inserting %d total chunks in batch...", len(all_chunks))
    col = get_collection("vector_chunks")
    col.delete_many({})
    col.insert_many(all_chunks)
    logger.info("Chunks stored: %d", len(all_chunks))
    print(f"RAG ingestion complete: {len(all_chunks)} chunks stored (batch mode).")


if __name__ == "__main__":
    ingest_rag()
