import time
import logging
import io
import os
import tempfile

from graph.state import AdminTPEState

logger = logging.getLogger(__name__)


def _extract_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            text += "\n"
        return text.strip()
    except Exception as e:
        logger.error("PDF extraction error: %s", e)
        raise


def _extract_csv(content: bytes) -> str:
    try:
        import pandas as pd
        df = pd.read_csv(io.BytesIO(content))
        return df.to_string(index=False)
    except Exception as e:
        logger.error("CSV extraction error: %s", e)
        raise


def _extract_excel(content: bytes) -> str:
    try:
        import pandas as pd
        xls = pd.ExcelFile(io.BytesIO(content))
        text = ""
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            text += f"--- Sheet: {sheet} ---\n"
            text += df.to_string(index=False)
            text += "\n"
        return text.strip()
    except Exception as e:
        logger.error("Excel extraction error: %s", e)
        raise


def _extract_text(content: bytes) -> str:
    try:
        return content.decode("utf-8", errors="replace")
    except Exception as e:
        logger.error("Text extraction error: %s", e)
        raise


def node_extract_files(state: AdminTPEState) -> dict:
    start = time.time()
    files = state.get("uploaded_files", [])
    extracted_texts = {}
    errors = state.get("errors", [])
    debug_trace = state.get("debug_trace", [])

    for f in files:
        filename = f.get("filename", "unknown")
        content = f.get("content", b"")
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        try:
            if ext == ".pdf":
                text = _extract_pdf(content)
            elif ext == ".csv":
                text = _extract_csv(content)
            elif ext in (".xls", ".xlsx"):
                text = _extract_excel(content)
            elif ext in (".txt", ".md"):
                text = _extract_text(content)
            else:
                text = _extract_text(content)

            extracted_texts[filename] = text
            logger.info("[node_extract_files] Extracted %s: %d chars", filename, len(text))
        except Exception as e:
            errors.append({
                "node_name": "node_extract_files",
                "error_type": "extraction_failed",
                "message": str(e),
                "user_explanation": f"Le fichier {filename} n'a pas pu être lu. Il peut être scanné, protégé ou corrompu.",
                "suggestion": "Essayez avec un fichier contenant du texte sélectionnable.",
            })
            logger.error("[node_extract_files] Failed to extract %s: %s", filename, e)

    status = "warning" if any(e.get("node_name") == "node_extract_files" for e in errors) else "success"
    debug_trace.append({
        "node_name": "node_extract_files",
        "status": status,
        "duration_ms": int((time.time() - start) * 1000),
        "input_summary": f"files={len(files)}",
        "output_summary": f"extracted={len(extracted_texts)}, errors={sum(1 for e in errors if e.get('node_name') == 'node_extract_files')}",
    })

    timings = state.get("timings", {})
    timings["node_extract_files"] = time.time() - start

    return {
        "extracted_texts": extracted_texts,
        "errors": errors,
        "debug_trace": debug_trace,
        "timings": timings,
    }
